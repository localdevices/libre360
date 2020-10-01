FROM debian:buster-slim

WORKDIR /work

COPY . debian

RUN apt-get update && \
    apt-get install -y devscripts git && \
    mk-build-deps -ir -t "apt-get -o Debug::pkgProblemResolver=yes -y --no-install-recommends" && \
    apt-get clean

CMD (cd /src; tar cf - .) | tar -xf - && \
    dpkg-buildpackage --build=any,all && \
    mkdir -p /src/build && \
    mv ../*.deb /src/build

# Build with:
#   docker build -t odm360:build debian
# Run with:
#   docker run -v $(pwd):/src odm360:build
