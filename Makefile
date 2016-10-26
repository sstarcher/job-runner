
.jobs:
	./processor/python.py example-jobs

all:
	rm -rf .jobs
	./processor/python.py example-jobs