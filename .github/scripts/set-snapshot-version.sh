#!/bin/bash

# See https://docs.github.com/en/free-pro-team@latest/actions/reference/environment-variables

# Get the latest vX.Y.Z tag from the repo and throw away the v prefix
PROJECT_VERSION=$(git describe --abbrev=0 | cut -c2-)

# Use dch to update debian/changelog
dch --newversion "${PROJECT_VERSION}-b${GITHUB_RUN_NUMBER}" \
  "${GITHUB_WORKFLOW} #${GITHUB_RUN_NUMBER} from ${GITHUB_REPOSITORY}"
