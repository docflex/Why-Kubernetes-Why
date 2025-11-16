FROM nginx:1.27
RUN apt-get update && apt-get install -y inotify-tools
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d /etc/nginx/conf.d
COPY reloader.sh /usr/local/bin/reloader.sh
RUN chmod +x /usr/local/bin/reloader.sh
CMD ["bash", "-c", "nginx && /usr/local/bin/reloader.sh"]
