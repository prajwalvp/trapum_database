FROM mysql:5.7.15

MAINTAINER me

ENV MYSQL_DATABASE=trapum

ADD TRAPUM_latest_schema.sql /docker-entrypoint-initdb.d

EXPOSE 3306
