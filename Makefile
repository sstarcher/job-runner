TAG=$(shell git rev-parse --abbrev-ref HEAD)


.jobs:
	./processor/python.py example-jobs

clean:
	rm -rf .jobs

build:
	docker build -t sstarcher/job-runner:${TAG} .

deploy:
	docker push sstarcher/job-runner:${TAG}

all: clean .jobs

.PHONY: clean all