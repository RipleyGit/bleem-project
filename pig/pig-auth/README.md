## 打包部署
mvn clean package

## docker 打包

docker build -t pig-auth:latest .

## docker 运行
docker run -d -it \
    --restart=always \
    -p 5000:5000 \
    --name pig-auth \
    pig-auth:latest --spring.cloud.nacos.discovery.ip=dsm.bleem.site