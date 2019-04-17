FROM postgres:10 AS fdwPostgres

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB test

RUN mkdir -p /neo4j-fdw
COPY . /neo4j-fdw/source

RUN apt-get update \
      && apt-get install -y --no-install-recommends \
           build-essential \
           postgresql-server-dev-10 \
           python-dev \
           python-setuptools \
           python-dev \
           python-pip \
           postgresql-plpython-10 \
           git \
      && rm -rf /var/lib/apt/lists/*

RUN ["chmod", "+x", "/neo4j-fdw/source/scripts/docker/postgres/init.sh"]
RUN /neo4j-fdw/source/scripts/docker/postgres/init.sh


