## 打包部署
mvn clean package

## docker 打包

docker build -t pig-gateway:latest .

## docker 运行
docker run -d -it \
    --restart=always \
    -p 9999:9999 \
    --name pig-gateway \
    pig-gateway:latest 

## 更新docker镜像