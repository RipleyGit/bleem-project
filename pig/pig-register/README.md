
## 编译打包
```
mvn clean package
```
## docker 镜像打包
```
docker build -t pig-register:latest .
```
##  docker 镜像运行
```
docker run -d -it \
    --restart=always \
    -e MYSQL_HOST=dsm.bleem.site \
    -e MYSQL_PORT=3306 \
    -e MYSQL_DB=pg_config \
    -e DB_USERNAME=app \
    -e DB_PASSWORD=a123P456p_ \
    -p 8848:8848 \
    -p 9848:9848 \
    -p 9090:8080 \
    --name pig-register \
    pig-register:latest
    
docker logs -f pig-register
```

## 删除镜像
```
docker stop pig-register

docker rm pig-register

docker rmi pig-register

```


## FQA

### 

```shell
org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'capacityManagementAspect' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/aspect/CapacityManagementAspect.class]: Unsatisfied dependency expressed through constructor parameter 0: Error creating bean with name 'externalConfigInfoPersistServiceImpl' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/service/repository/extrnal/ExternalConfigInfoPersistServiceImpl.class]: Unsatisfied dependency expressed through constructor parameter 0: Error creating bean with name 'externalHistoryConfigInfoPersistServiceImpl' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/service/repository/extrnal/ExternalHistoryConfigInfoPersistServiceImpl.class]: Failed to instantiate [com.alibaba.nacos.config.server.service.repository.extrnal.ExternalHistoryConfigInfoPersistServiceImpl]: Constructor threw exception
        at org.springframework.beans.factory.support.ConstructorResolver.createArgumentArray(ConstructorResolver.java:804)
        at org.springframework.beans.factory.support.ConstructorResolver.autowireConstructor(ConstructorResolver.java:240)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.autowireConstructor(AbstractAutowireCapableBeanFactory.java:1395)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1232)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:569)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:529)
        at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:339)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:373)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:337)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:202)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.instantiateSingleton(DefaultListableBeanFactory.java:1228)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingleton(DefaultListableBeanFactory.java:1194)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.preInstantiateSingletons(DefaultListableBeanFactory.java:1130)
        at org.springframework.context.support.AbstractApplicationContext.finishBeanFactoryInitialization(AbstractApplicationContext.java:990)
        at org.springframework.context.support.AbstractApplicationContext.refresh(AbstractApplicationContext.java:627)
        at org.springframework.boot.SpringApplication.refresh(SpringApplication.java:752)
        at org.springframework.boot.SpringApplication.refreshContext(SpringApplication.java:439)
        at org.springframework.boot.SpringApplication.run(SpringApplication.java:318)
        at org.springframework.boot.builder.SpringApplicationBuilder.run(SpringApplicationBuilder.java:149)
        at com.alibaba.nacos.bootstrap.PigNacosApplication.main(PigNacosApplication.java:59)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke0(Native Method)
        at java.base/jdk.internal.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)
        at java.base/java.lang.reflect.Method.invoke(Method.java:569)
        at org.springframework.boot.loader.launch.Launcher.launch(Launcher.java:106)
        at org.springframework.boot.loader.launch.Launcher.launch(Launcher.java:64)
        at org.springframework.boot.loader.launch.JarLauncher.main(JarLauncher.java:40)
Caused by: org.springframework.beans.factory.UnsatisfiedDependencyException: Error creating bean with name 'externalConfigInfoPersistServiceImpl' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/service/repository/extrnal/ExternalConfigInfoPersistServiceImpl.class]: Unsatisfied dependency expressed through constructor parameter 0: Error creating bean with name 'externalHistoryConfigInfoPersistServiceImpl' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/service/repository/extrnal/ExternalHistoryConfigInfoPersistServiceImpl.class]: Failed to instantiate [com.alibaba.nacos.config.server.service.repository.extrnal.ExternalHistoryConfigInfoPersistServiceImpl]: Constructor threw exception
        at org.springframework.beans.factory.support.ConstructorResolver.createArgumentArray(ConstructorResolver.java:804)
        at org.springframework.beans.factory.support.ConstructorResolver.autowireConstructor(ConstructorResolver.java:240)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.autowireConstructor(AbstractAutowireCapableBeanFactory.java:1395)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1232)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:569)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:529)
        at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:339)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:373)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:337)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:202)
        at org.springframework.beans.factory.config.DependencyDescriptor.resolveCandidate(DependencyDescriptor.java:254)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:1770)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1653)
        at org.springframework.beans.factory.support.ConstructorResolver.resolveAutowiredArgument(ConstructorResolver.java:913)
        at org.springframework.beans.factory.support.ConstructorResolver.createArgumentArray(ConstructorResolver.java:791)
        ... 26 common frames omitted
Caused by: org.springframework.beans.factory.BeanCreationException: Error creating bean with name 'externalHistoryConfigInfoPersistServiceImpl' defined in URL [jar:nested:/pig-register/app.jar/!BOOT-INF/lib/nacos-config-3.1.0-bugfix.jar!/com/alibaba/nacos/config/server/service/repository/extrnal/ExternalHistoryConfigInfoPersistServiceImpl.class]: Failed to instantiate [com.alibaba.nacos.config.server.service.repository.extrnal.ExternalHistoryConfigInfoPersistServiceImpl]: Constructor threw exception
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.instantiateBean(AbstractAutowireCapableBeanFactory.java:1357)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBeanInstance(AbstractAutowireCapableBeanFactory.java:1242)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.doCreateBean(AbstractAutowireCapableBeanFactory.java:569)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.createBean(AbstractAutowireCapableBeanFactory.java:529)
        at org.springframework.beans.factory.support.AbstractBeanFactory.lambda$doGetBean$0(AbstractBeanFactory.java:339)
        at org.springframework.beans.factory.support.DefaultSingletonBeanRegistry.getSingleton(DefaultSingletonBeanRegistry.java:373)
        at org.springframework.beans.factory.support.AbstractBeanFactory.doGetBean(AbstractBeanFactory.java:337)
        at org.springframework.beans.factory.support.AbstractBeanFactory.getBean(AbstractBeanFactory.java:202)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.doResolveDependency(DefaultListableBeanFactory.java:1708)
        at org.springframework.beans.factory.support.DefaultListableBeanFactory.resolveDependency(DefaultListableBeanFactory.java:1653)
        at org.springframework.beans.factory.support.ConstructorResolver.resolveAutowiredArgument(ConstructorResolver.java:913)
        at org.springframework.beans.factory.support.ConstructorResolver.createArgumentArray(ConstructorResolver.java:791)
        ... 40 common frames omitted
Caused by: org.springframework.beans.BeanInstantiationException: Failed to instantiate [com.alibaba.nacos.config.server.service.repository.extrnal.ExternalHistoryConfigInfoPersistServiceImpl]: Constructor threw exception
        at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:223)
        at org.springframework.beans.factory.support.SimpleInstantiationStrategy.instantiate(SimpleInstantiationStrategy.java:123)
        at org.springframework.beans.factory.support.AbstractAutowireCapableBeanFactory.instantiateBean(AbstractAutowireCapableBeanFactory.java:1351)
        ... 51 common frames omitted
Caused by: java.lang.RuntimeException: java.lang.RuntimeException: [db-load-error]load jdbc.properties error
        at com.alibaba.nacos.persistence.datasource.DynamicDataSource.getDataSource(DynamicDataSource.java:60)
        at com.alibaba.nacos.config.server.service.repository.extrnal.ExternalHistoryConfigInfoPersistServiceImpl.<init>(ExternalHistoryConfigInfoPersistServiceImpl.java:76)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance0(Native Method)
        at java.base/jdk.internal.reflect.NativeConstructorAccessorImpl.newInstance(NativeConstructorAccessorImpl.java:77)
        at java.base/jdk.internal.reflect.DelegatingConstructorAccessorImpl.newInstance(DelegatingConstructorAccessorImpl.java:45)
        at java.base/java.lang.reflect.Constructor.newInstanceWithCaller(Constructor.java:500)
        at java.base/java.lang.reflect.Constructor.newInstance(Constructor.java:481)
        at org.springframework.beans.BeanUtils.instantiateClass(BeanUtils.java:197)
        ... 53 common frames omitted
Caused by: java.lang.RuntimeException: [db-load-error]load jdbc.properties error
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceServiceImpl.init(ExternalDataSourceServiceImpl.java:119)
        at com.alibaba.nacos.persistence.datasource.DynamicDataSource.getDataSource(DynamicDataSource.java:55)
        ... 60 common frames omitted
Caused by: java.io.IOException: java.lang.RuntimeException: java.sql.SQLSyntaxErrorException: Access denied for user 'nacos'@'%' to database 'pg_config'
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceServiceImpl.reload(ExternalDataSourceServiceImpl.java:168)
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceServiceImpl.init(ExternalDataSourceServiceImpl.java:116)
        ... 61 common frames omitted
Caused by: java.lang.RuntimeException: java.sql.SQLSyntaxErrorException: Access denied for user 'nacos'@'%' to database 'pg_config'
        at com.alibaba.nacos.persistence.utils.ConnectionCheckUtil.checkDataSourceConnection(ConnectionCheckUtil.java:37)
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceServiceImpl.lambda$reload$0(ExternalDataSourceServiceImpl.java:138)
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceProperties.build(ExternalDataSourceProperties.java:97)
        at com.alibaba.nacos.persistence.datasource.ExternalDataSourceServiceImpl.reload(ExternalDataSourceServiceImpl.java:136)
        ... 62 common frames omitted
Caused by: java.sql.SQLSyntaxErrorException: Access denied for user 'nacos'@'%' to database 'pg_config'
        at com.mysql.cj.jdbc.exceptions.SQLError.createSQLException(SQLError.java:112)
        at com.mysql.cj.jdbc.exceptions.SQLExceptionsMapping.translateException(SQLExceptionsMapping.java:114)
        at com.mysql.cj.jdbc.ConnectionImpl.createNewIO(ConnectionImpl.java:837)
        at com.mysql.cj.jdbc.ConnectionImpl.<init>(ConnectionImpl.java:420)
        at com.mysql.cj.jdbc.ConnectionImpl.getInstance(ConnectionImpl.java:238)
        at com.mysql.cj.jdbc.NonRegisteringDriver.connect(NonRegisteringDriver.java:180)
        at com.zaxxer.hikari.util.DriverDataSource.getConnection(DriverDataSource.java:144)
        at com.zaxxer.hikari.pool.PoolBase.newConnection(PoolBase.java:370)
        at com.zaxxer.hikari.pool.PoolBase.newPoolEntry(PoolBase.java:207)
        at com.zaxxer.hikari.pool.HikariPool.createPoolEntry(HikariPool.java:488)
        at com.zaxxer.hikari.pool.HikariPool.checkFailFast(HikariPool.java:576)
        at com.zaxxer.hikari.pool.HikariPool.<init>(HikariPool.java:97)
        at com.zaxxer.hikari.HikariDataSource.getConnection(HikariDataSource.java:111)
        at com.alibaba.nacos.persistence.utils.ConnectionCheckUtil.checkDataSourceConnection(ConnectionCheckUtil.java:34)
        ... 65 common frames omitted

```