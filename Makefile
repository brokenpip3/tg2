tokenfile := _token
TOKEN :=$(file < $(tokenfile))
versionfile := _version
VERSION :=$(file < $(versionfile))
IMAGE := brokenpip3/tg2
LOCALCONFIG := config.yaml
REMOTECONFIG := /usr/src/bot/config.yaml

.PHONY: all build push docker-run kube-build

all: build push kube-build

build:
	docker build -t $(IMAGE):$(VERSION) . --no-cache

push:
	docker push $(IMAGE):$(VERSION)

run:
	export TGTOKEN=$(TOKEN) && .venv/bin/python src/tg2.py config.yaml

docker-run:
	docker run -i -t --rm -e TGTOKEN=$(TOKEN) -v ${PWD}/examples/cryptocurrency.yaml:/usr/src/bot/config.yaml $(IMAGE):$(VERSION)

kube-build:
	docker build -t $(IMAGE):$(VERSION)-kube -f kubernetes/Dockerfile.kubernetes . --no-cache
	docker push $(IMAGE):$(VERSION)-kube
