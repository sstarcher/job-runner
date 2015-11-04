# The Concept
**Stitch together a Docker job scheduler, distributed locking, task runner, and alerting system**


Project: [https://github.com/sstarcher/job-runner]
(https://github.com/sstarcher/job-runner)

Docker image: [https://registry.hub.docker.com/u/sstarcher/job-runner/]
(https://registry.hub.docker.com/u/sstarcher/job-runner/)

[![](https://badge.imagelayers.io/sstarcher/job-runner:latest.svg)](https://imagelayers.io/?images=sstarcher/job-runner:latest 'Get your own badge on imagelayers.io')
[![Docker Registry](https://img.shields.io/docker/pulls/sstarcher/job-runner.svg)](https://registry.hub.docker.com/u/sstarcher/job-runner)&nbsp;

* Job Scheduler: Cron
* Distributed Locking: Consul
* Task Runners: Docker, Kubernetes
* Job Alerting: Sensu


### Run Methods
* Cron
  * If ran with no command argument it will start in cron mode and run on the cron schedule.  
* Single Job
  * If a job name is specified it will run the job, tail the logs, and exit when the job is finished. 
  * Lockers and Alerters are disabled in this mode

### Deployment Methods
* Docker 
  * docker run sstarcher/job-runner:latest

* Kubernetes
  * Example pod for running under Kubernetes

```
apiVersion: v1
kind: ReplicationController
metadata:
  name: job-runner
spec:
  replicas: 1
  selector:
    name: job-runner
  template:
    metadata:
      labels:
        name: job-runner
    spec:
      containers:
      - name: job-runner
        image: sstarcher/job-runner:latest
        env:
        - name: RUNNER
          value: kubernetes
        - name: KUBERNETES_MASTER
          value: http://kubernetes:8080
```


### Runners
* Docker
  * Mount either the docker socket or set DOCKER_HOST
* Kubernetes
  * Set `KUBERNETES_MASTER` to your Kubernetes cluster url example `http://127.0.0.1:8080`
  * compose2kube binary has been built from - https://github.com/sstarcher/compose2kube

### Lockers
* Consul
  * CONSUL_HOST to an address without your cluster - default `localhost`
  * CONSUL_PORT to the port your cluster is listening on - default `8500`


### Alerters
* Sensu
  * SENSU_HOST to an address for Sensu - default `127.0.0.1`
  * SENSU_PORT to the port Sensu is listening on for the client - default `3030`
  * KIBANA_HOST optional URL.  If set a Kibana link will be sent to the sensu data


### Configuration
* Alerters, Lockers are disabled by default
* Docker is the default runner
* Example job formats are in the `example-jobs` folder
* Job names must be unique
* example-jobs
  * [DEFAULTS.yaml](example-jobs/DEFAULTS.yaml)
  * [test.yaml](example-jobs/test.yaml)
* This project utilizes docker ONBUILD so any yaml files added under a `jobs` directory will be added and processed
1. Create a Dockerfile
```
FROM sstarcher/job-runner:latest
```
2. Create a folder called jobs
3. Create a job
```
Example:
  image: debian:jessie #This value is overriding what is set in the DEFAULTS.yaml
  Jobs:
    - Test:
        time: '* * * * *'
        command: echo $job 
```
4. docker build -t jobs .
5. docker run jobs








