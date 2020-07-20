FROM postgres:10.10 AS fdwPostgres

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB test

RUN mkdir -p /neo4j-fdw
COPY . /neo4j-fdw/source

RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           build-essential \
           postgresql-server-dev-10 \
           python3-dev \
           python3-setuptools \
           python3-dev \
           python3-pip \
           postgresql-plpython3-10 \
           git \
      && rm -rf /var/lib/apt/lists/*

RUN ["chmod", "+x", "/neo4j-fdw/source/scripts/docker/postgres/init.sh"]
RUN /neo4j-fdw/source/scripts/docker/postgres/init.sh
