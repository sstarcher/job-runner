FROM debian:jessie
MAINTAINER shanestarcher@gmail.com

#Docker Hub does not support docker 1.9 yet change back to ARG https://github.com/docker/hub-feedback/issues/460
ENV dockerize_version=0.0.4
ENV kubernetes_version=1.1.1
ENV compose_version=1.5.0

RUN \
    apt-get update && \
    apt-get install -y curl cron python python-pip netcat && \
    pip install PyYAML && \
    pip install chkcrontab


RUN \
    mkdir -p /usr/local/bin/ &&\
    curl -SL https://github.com/jwilder/dockerize/releases/download/v${dockerize_version}/dockerize-linux-amd64-v${dockerize_version}.tar.gz \
    | tar xzC /usr/local/bin

RUN \
    echo "deb http://http.debian.net/debian jessie-backports main" > /etc/apt/sources.list.d/backports.list && \
    apt-get update && \
    apt-get install -y docker.io

RUN \
    curl -L https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose &&\
    chmod +x /usr/local/bin/docker-compose

RUN \
    curl -SL https://github.com/kubernetes/kubernetes/releases/download/v${kubernetes_version}/kubernetes.tar.gz \
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
RUN curl -SL -o /app/lockers/cronsul -z /app/lockers/cronsul https://raw.githubusercontent.com/EvanKrall/cronsul/master/cronsul &&\
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
