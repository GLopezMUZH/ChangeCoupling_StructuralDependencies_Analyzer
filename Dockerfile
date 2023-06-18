FROM python:3.10.2-slim

RUN apt-get update \
  && apt-get install -y \
  gcc \
  git \
  curl \
  libxml2 \
  libarchive13 \
  default-jdk \
  && rm -rf /var/lib/apt/lists/*

#RUN curl --output /tmp/srcml.deb http://131.123.42.38/lmcrs/v1.0.0/srcml_1.0.0-1_ubuntu20.04.deb \
#  && dpkg -i /tmp/srcml.deb \
#  && rm /tmp/srcml.deb

ENV SHELL=/bin/bash \
  POETRY_VERSION=1.1.8

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /var/project

COPY pyproject.toml poetry.lock /var/project/

RUN poetry install