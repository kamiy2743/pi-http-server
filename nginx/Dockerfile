FROM python:3.12-alpine AS builder

WORKDIR /app

RUN apk add --no-cache \
    bash \
    graphviz \
    fontconfig \
    font-noto-cjk

COPY ./requirements.txt ./requirements.txt
RUN python3 -m venv .venv \
 && .venv/bin/pip install --no-cache-dir --retries 5 --timeout 120 -r requirements.txt

COPY ./content ./content
COPY ./public ./public
COPY ./scripts ./scripts

COPY ./build.sh ./build.sh
RUN chmod +x ./build.sh \
 && ./build.sh

FROM nginx:1.27-alpine

COPY ./nginx/http-server.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/public /usr/share/nginx/html
