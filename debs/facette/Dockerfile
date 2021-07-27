FROM ubuntu:focal-20210713

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get --quiet --yes --no-install-recommends install \
    ca-certificates \
    curl \
    devscripts \
    equivs \
    lsb-release \
    git \
    go-bindata \
 && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
 && apt update && apt --quiet --yes install yarn \
    ;

WORKDIR /build/source

COPY debian/changelog debian/changelog
RUN export VERSION="$( /usr/bin/dpkg-parsechangelog --show-field Version | cut -d'-' -f1 )" \
 && curl -L "https://github.com/facette/facette/releases/download/${VERSION}/facette_${VERSION}.tar.gz" \
    | tar -x -v -p -z --strip-components=1

RUN apt-get update && mk-build-deps --install --tool 'apt-get --no-install-recommends -y'

COPY debian ./debian

# Facette includes a `make dist-deb` rule, but we ignore it in favour of our usual pattern
# that won't clobber the changelog; or include the package source
# RUN make dist-deb
RUN dpkg-buildflags && DEB_BUILD_OPTIONS="parallel=$(nproc) nocheck" dpkg-buildpackage -B

CMD mkdir -p /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/ \
 && dpkg -c /build/*.deb \
 && cp /build/*.deb /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/
