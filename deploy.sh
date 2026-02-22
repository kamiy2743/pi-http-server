#!/usr/bin/env bash

set -euo pipefail

SRC="/home/kamiy2743/workspace/http-server/public/"
DST="/var/www/http-server/"

NGINX_SRC="/home/kamiy2743/workspace/http-server/nginx/http-server.conf"
NGINX_AVAIL="/etc/nginx/sites-available/http-server.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/http-server.conf"

mkdir -p $DST
rsync -av --delete $SRC $DST

install -m 644 $NGINX_SRC $NGINX_AVAIL
ln -sfn $NGINX_AVAIL $NGINX_ENABLED

nginx -t
systemctl restart nginx
