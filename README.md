# The Concept
**Stitch together a Docker job scheduler, distributed locking, task runner**

[![CircleCI](https://circleci.com/gh/sstarcher/job-runner.svg?style=svg)](https://circleci.com/gh/sstarcher/job-runner)
[![](https://imagelayers.io/badge/sstarcher/job-runner:latest.svg)](https://imagelayers.io/?images=sstarcher/job-runner:latest 'Get your own badge on imagelayers.io')
[![Docker Registry](https://img.shields.io/docker/pulls/sstarcher/job-runner.svg)](https://registry.hub.docker.com/u/sstarcher/job-runner)&nbsp;

This repo outputs reaps and alerts on finished kubernetes jobs.

Project: [https://github.com/sstarcher/job-runner]
(https://github.com/sstarcher/job-runner)

Docker image: [https://registry.hub.docker.com/u/sstarcher/job-runner/]
(https://registry.hub.docker.com/u/sstarcher/job-runner/)


* Job Scheduler: Cron
* Distributed Locking: Consul
* Task Runners: Kubernetes


### Run Methods
* Cron
  * If ran with no command argument it will start in cron mode and run on the cron schedule.  
* Single Job
  * If a job name is specified it will run the job and print out the pod name
  * Lockers are disabled in this mode

### Deployment Methods

```
apiVersion: v1
kind: Deployment
metadata:
  name: job-runner
spec:
  replicas: 1
  template:
    metadata:
      labels:
        name: job-runner
    spec:
      containers:
      - name: job-runner
        image: sstarcher/job-runner:latest
```


### Runner Kubernetes
  * Set `KUBERNETES_MASTER` to your Kubernetes cluster url example `http://127.0.0.1:8080`


### Lockers
* Consul
  * CONSUL_HOST to an address without your cluster - default `localhost`
  * CONSUL_PORT to the port your cluster is listening on - default `8500`


### Configuration
* Lockers are disabled by default
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
4. docker build --pull -t jobs .
5. docker run jobs
