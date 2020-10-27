#!/bin/bash -e

REPO_BRANCH=apt-repo
KEYNAME=
GIT_REMOTE=origin

###

if [ -z "$1" ]; then
  echo "Usage: $0 <\*.deb>"
  exit 1
fi

echo "=== Determine working branch"
[ -z ${GITHUB_REF} ] && GITHUB_REF=$(git symbolic-ref -q HEAD)
WORK_BRANCH=${GITHUB_REF##*/}

echo "=== Set Git identity"
NAME=$(git log -1 --pretty=format:'%an')
EMAIL=$(git log -1 --pretty=format:'%ae')

git config user.name "${NAME}"
git config user.email "${EMAIL}"

echo "${NAME} <${EMAIL}>"

echo "=== Check out repository branch: ${REPO_BRANCH}"
if ! git checkout -f ${REPO_BRANCH}; then
  git checkout --orphan ${REPO_BRANCH}
  git rm -rf .
  echo "Debian package repository for ${GITHUB_REPOSITORY}" > README.md
  git add README.md
  git commit -m "Add empty README"
fi
git reset --hard HEAD

echo "=== Replace files in ${WORK_BRANCH}"
rm -rf ${WORK_BRANCH}
mkdir ${WORK_BRANCH}
cd ${WORK_BRANCH}
cp -v $@ .

# based roughly on:
# https://medium.com/sqooba/create-your-own-custom-and-authenticated-apt-repository-1e4a4cf0b864

echo "=== Build Packages"
apt-ftparchive packages . > Packages
gzip -k -f Packages

echo "=== Build Release"
apt-ftparchive release . > Release
git add Release

if [ -n "${KEYNAME}" ]; then
  echo "=== Sign Release"
  gpg --default-key ${KEYNAME} -abs -o Release.gpg Release

  echo "=== Sign InRelease"
  gpg --default-key ${KEYNAME} --clearsign -o InRelease Release
else
  echo "=== No key name set; skipping signatures"
fi

if git describe --tags --exact-match 2>/dev/null; then
  echo "=== Previous Git commit was tagged; adding a new commit"
else
  echo "=== Overwrite previous automated Git commit"
  AMEND=--amend
fi
git add .
git commit ${AMEND} -m "${GITHUB_WORKFLOW:-workflow} ${GITHUB_RUN_NUMBER:-(unknown)} from ${GITHUB_REPOSITORY:-(unknown)}"

if [ -n "${GIT_REMOTE}" ]; then
  echo "=== Force push to remote"
  git push -f ${GIT_REMOTE} ${REPO_BRANCH}
fi
