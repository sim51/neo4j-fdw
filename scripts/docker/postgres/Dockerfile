FROM postgres:10.10 AS fdwPostgres

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB test

RUN mkdir -p /neo4j-fdw
COPY . /neo4j-fdw/source

RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           build-essential \
           python-dev \
           python-setuptools \
           python-dev \
           python-pip \
           git \
           libfaketime \
           wget \
      && rm -rf /var/lib/apt/lists/*

RUN cp /neo4j-fdw/source/scripts/faketime.sh /docker-entrypoint-initdb.d/

RUN mkdir /tmp/pgdebs \
      && wget --quiet -P /tmp/pgdebs \
              https://atalia.postgresql.org/morgue/p/postgresql-10/postgresql-server-dev-10_10.10-1.pgdg90%2B1_amd64.deb \
              https://atalia.postgresql.org/morgue/p/postgresql-10/postgresql-plpython-10_10.10-1.pgdg90%2B1_amd64.deb \
              https://atalia.postgresql.org/morgue/p/postgresql-10/libpq5_10.10-1.pgdg90%2B1_amd64.deb \
              https://atalia.postgresql.org/morgue/p/postgresql-10/libpq-dev_10.10-1.pgdg90%2B1_amd64.deb \
      && apt install -y --allow-downgrades \
              /tmp/pgdebs/postgresql-server-dev-10_10.10-1.pgdg90+1_amd64.deb \
              /tmp/pgdebs/postgresql-plpython-10_10.10-1.pgdg90+1_amd64.deb \
              /tmp/pgdebs/libpq5_10.10-1.pgdg90+1_amd64.deb \
              /tmp/pgdebs/libpq-dev_10.10-1.pgdg90+1_amd64.deb
RUN rm -r /tmp/pgdebs

RUN ["chmod", "+x", "/neo4j-fdw/source/scripts/docker/postgres/init.sh"]
RUN /neo4j-fdw/source/scripts/docker/postgres/init.sh
