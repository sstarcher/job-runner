.jobs:
	./processor/python.py example-jobs

clean:
	rm -rf .jobs

all: clean .jobs

.PHONY: clean all