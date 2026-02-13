FROM registry.cn-hangzhou.aliyuncs.com/dockerhub_mirror/nginx

COPY ./dist /data

RUN setenforce 0

RUN rm /etc/nginx/conf.d/default.conf

ADD pig-ui.conf /etc/nginx/conf.d/default.conf

RUN /bin/bash -c 'echo init ok'
