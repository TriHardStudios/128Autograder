FROM python:3.12-alpine

ADD source /tmp/source

RUN apk add --no-cache git && \
    apk add --no-cache build-base && \
    apk add --no-cache bash && \
    python3 -m pip install --break-system-package /tmp/source

RUN mkdir -p /autograder/{bin,submission,tests}

WORKDIR /autograder
