docker run -d -it \
    --restart=always \
    -e MYSQL_HOST=dsm.bleem.site \
    -e MYSQL_PORT=3306 \
    -e MYSQL_DB=pg-config \
    -e DB_USERNAME=nacos \
    -e DB_PASSWORD=nAcos118.34 \
    -p 8848:8848 \
    -p 9848:9848 \
    -p 9090:8080 \
    --name pig-register \
    pig-register:latest