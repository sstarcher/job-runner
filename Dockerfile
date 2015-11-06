FROM debian:jessie
MAINTAINER shanestarcher@gmail.com

RUN \
    apt-get update && \
    apt-get install -y curl cron python python-pip netcat && \
    pip install PyYAML

RUN \
    mkdir -p /usr/local/bin/ &&\
    curl -SL https://github.com/jwilder/dockerize/releases/download/v0.0.3/dockerize-linux-amd64-v0.0.3.tar.gz \
    | tar xzC /usr/local/bin

RUN \
    echo "deb http://http.debian.net/debian jessie-backports main" > /etc/apt/sources.list.d/backports.list && \
    apt-get update && \
    apt-get install -y docker.io

RUN \
    curl -L https://github.com/docker/compose/releases/download/1.4.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose &&\
    chmod +x /usr/local/bin/docker-compose

RUN \
    curl -SL https://github.com/kubernetes/kubernetes/releases/download/v1.0.3/kubernetes.tar.gz \
    | tar xz kubernetes/platforms/linux/amd64/kubectl &&\
    mv kubernetes/platforms/linux/amd64/kubectl /usr/local/bin &&\
    rm -rf kubernetes

ADD files/compose2kube /usr/local/bin/compose2kube
ADD files/reaper_cron /etc/cron.d/

WORKDIR /app
ADD . /app

RUN mkdir -p /app/lockers
RUN curl -SL -o /app/lockers/cronsul-cleanup -z /app/lockers/cronsul-cleanup https://raw.githubusercontent.com/EvanKrall/cronsul/master/cronsul-cleanup &&\
    chmod +x /app/lockers/cronsul-cleanup
RUN curl -SL -o /app/lockers/cronsul -z /app/lockers/cronsul https://raw.githubusercontent.com/sstarcher/cronsul/master/cronsul &&\
    chmod +x /app/lockers/cronsul
RUN mkdir /app/compose


ONBUILD ADD jobs jobs
ONBUILD RUN ./processor/python.py /app/jobs &&\
    cp /app/cron/* /etc/cron.d/ &&\
    cp /app/default/* /etc/default/

ENV RUNNER docker
ENV ALERTER ''
ENV LOCKER ''
ENV SENSU_JIT ''
ENV K8S ''
ENV CONSUL_HOST ''

ENTRYPOINT ["/app/processor/start"]
