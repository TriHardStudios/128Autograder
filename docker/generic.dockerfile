FROM python:3.12-alpine

ADD source/requirements.txt /app/source/requirements.txt

RUN apk add --no-cache git && \
    apk add --no-cache build-base && \
    apk add --no-cache bash && \
    python3 -m pip install --break-system-package -r /app/source/requirements.txt 

ADD source /app/source

RUN mkdir -p /app/bin

WORKDIR /app/source

ENTRYPOINT [ "python", "run.py" ]
