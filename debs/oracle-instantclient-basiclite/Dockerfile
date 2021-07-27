FROM ubuntu:focal-20210713

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get --quiet --yes --no-install-recommends install \
      build-essential \
      ca-certificates \
      curl \
      debhelper \
      devscripts \
      equivs \
      lsb-release \
      alien \
      ;

WORKDIR /build/source

# oracle-instantclient-basiclite is required in order to allow the cx_Oracle python package to work
# Oracle do not offer this as a deb, only an rpm, so we convert it and add in the required Ubuntu
# packages and then re-build it in /build

ADD https://download.oracle.com/otn_software/linux/instantclient/211000/oracle-instantclient-basiclite-21.1.0.0.0-1.x86_64.rpm oracle-instantclient-basiclite.rpm

# Convert the rpm to a deb
RUN alien oracle-instantclient-basiclite.rpm --scripts \
 && mv *.deb oracle-instantclient-basiclite.deb \
 && mkdir extracted \
 && dpkg-deb -R /build/source/oracle-instantclient-basiclite.deb extracted \
 && echo "Depends: libaio1" >> extracted/DEBIAN/control \
 && dpkg-deb -b extracted /build/oracle-instantclient-basiclite_$(dpkg-deb -f oracle-instantclient-basiclite.deb Version)_amd64.deb

CMD mkdir -p /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/ \
    && dpkg -c /build/*.deb \
    && cp /build/*.deb /out/dists/$( lsb_release -c -s )/main/binary-$( dpkg --print-architecture )/
