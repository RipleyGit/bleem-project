#FROM registry.cn-hangzhou.aliyuncs.com/dockerhub_mirror/java:21-anolis
FROM alpine:latest

# 安装依赖
RUN apk add --no-cache openjdk17-jre curl iputils ncurses vim libcurl bash libstdc++

WORKDIR /pig-register

ARG JAR_FILE=target/pig-register.jar

COPY ${JAR_FILE} app.jar

EXPOSE 8848 9848 8080

ENV TZ=Asia/Shanghai JAVA_OPTS="-Xms128m -Xmx256m -Djava.security.egd=file:/dev/./urandom"

CMD sleep 30; java $JAVA_OPTS -jar app.jar
