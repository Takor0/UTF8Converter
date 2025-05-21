.PHONY: dev_install docker-build docker-run run_example

dev_install:
	pip install -r requirements.txt

docker-build:
	mkdir -p input output
	docker build -t converter .

docker-run:
	docker run --rm \
		-u $(shell id -u):$(shell id -g) \
	  	-v $(PWD)/input:/data/input \
	  	-v $(PWD)/output:/data/output \
	  	converter \
	  	-s /data/input -d /data/output

run_example:
	python cli.py -s ./input -d ./output

test:
	pytest tests
