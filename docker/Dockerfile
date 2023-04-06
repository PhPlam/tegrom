# Author: Philipp Plamper
# Date: 06. april 2023

# base image neo4j
FROM neo4j:latest

# set environment variables
# https://neo4j.com/docs/operations-manual/current/docker/ref-settings/
ENV NEO4J_AUTH=neo4j/test1234
ENV NEO4J_PLUGINS='["apoc", "graph-data-science"]'

# enable files from different import directories
RUN sed -i '/server.directories.import/d' /var/lib/neo4j/conf/neo4j.conf

# update and install python, pip, bash
RUN apt update && apt upgrade -y \
    && apt install python3 -y \
    && apt install pip -y

# copy all files
COPY models /home/models
COPY requirements /home/requirements

# install libraries from requirements
RUN pip install -r /home/requirements/requirements.txt

# todo
# run scripts
# remove enterprise functions/handling of those functions
