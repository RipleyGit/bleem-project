#FROM registry.cn-hangzhou.aliyuncs.com/dockerhub_mirror/java:21-anolis
FROM alpine:latest

# 安装依赖
RUN apk add --no-cache openjdk17-jre curl iputils ncurses vim libcurl bash libstdc++

RUN apt-get update && apt-get install -y fontconfig fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /pig-auth

ARG JAR_FILE=target/pig-auth.jar

COPY ${JAR_FILE} app.jar

EXPOSE 5000

ENV TZ=Asia/Shanghai JAVA_OPTS="-Xms128m -Xmx256m -Djava.security.egd=file:/dev/./urandom"

CMD sleep 60; java $JAVA_OPTS -jar app.jar
