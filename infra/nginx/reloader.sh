#!/bin/sh
inotifywait -m -e modify,create,delete /etc/nginx/conf.d/upstreams /etc/nginx/conf.d/servers |
while read path action file; do
    echo "[RELOADER] Detected change in $file — reloading NGINX..."
    nginx -t && nginx -s reload
done
