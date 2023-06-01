# Sources:
# https://stackoverflow.com/questions/23391839/clone-private-git-repo-with-dockerfile
# https://fastapi.tiangolo.com/deployment/docker/
# https://dakdeniz.medium.com/fastapi-react-dockerize-in-single-container-e546e80b4e4d

FROM python:3.9


# MAINTAINER Bastien Cagna

FROM node:12.18-alpine AS ReactImage
# Install Git and clone the project
# RUN apt-get update
# RUN apt-get install -y git

# Clone the conf files into the docker container
RUN git clone https://github.com/BastienCagna/sulcilab.git

WORKDIR /app/frontend
COPY ./sulcilab/package.json /app/frontend/
RUN npm install
COPY ./sulcilab ./
RUN npm run build

FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN python3 -m pip install --upgrade pip setuptools wheel 

WORKDIR /app/api

COPY   ./sulcilab/setup.py /app/api/
RUN pip install .

COPY ./sulcilab ./

COPY --from=ReactImage ./app/frontend/build/. ./templates/build/.

WORKDIR /app/api