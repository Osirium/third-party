FROM ubuntu:xenial-20171006

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get --quiet --yes --no-install-recommends install \
      apt-transport-https \
      build-essential \
      ca-certificates \
      curl \
      debhelper \
      devscripts \
      equivs \
      lsb-release \
      ;

# We need yarn for which we need apt-transport-https from the previous step
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    curl -sL https://deb.nodesource.com/setup_10.x | bash -

RUN apt-get update && apt-get install --quiet --yes yarn nodejs

# Facette needs golang to build
RUN curl -L "https://dl.google.com/go/go1.15.5.linux-amd64.tar.gz" \
    | tar -x -v -z -C /usr/local \
    ;

ENV GOPATH=/root/go
ENV GOROOT=/usr/local/go
ENV PATH=$GOPATH/bin:$GOROOT/bin:$PATH

WORKDIR /build/source

COPY debian/changelog debian/changelog
RUN export VERSION="$( /usr/bin/dpkg-parsechangelog --show-field Version | cut -d'-' -f1 )" \
    && curl -L "https://github.com/facette/facette/releases/download/${VERSION}/facette_${VERSION}.tar.gz" \
    | tar -x -v -p -z --strip-components=1

# go-bindata is a pre-req
# go mod vendor fixes an error about inconsistent vendoring
RUN go get -u github.com/jteeuwen/go-bindata/... && \
    go mod vendor \
    ;

# We override facette's control file to remove the golang-go dependency that can't be met on Xenial
COPY debian/control debian/control

RUN apt-get update && mk-build-deps --install --tool 'apt-get --no-install-recommends -y'

COPY debian ./debian

# Facette includes a `make dist-deb` rule, but we ignore it in favour of our usual pattern
# that won't clobber the changelog; or include the package source
# RUN make dist-deb
RUN dpkg-buildflags && DEB_BUILD_OPTIONS="parallel=$(nproc) nocheck" dpkg-buildpackage -B

CMD mkdir -p /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/ \
    && dpkg -c /build/*.deb \
    && cp /build/*.deb /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/




