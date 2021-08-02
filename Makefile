SHELL:=/bin/bash -euo pipefail
UID = $(shell id -u)
GID = $(shell id -g)
ROOT_DIR = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
DEBS = $(patsubst $(ROOT_DIR)%/, %, $(filter %/, $(wildcard $(ROOT_DIR)debs/*/)))
OUTPUT = $(wildcard $(ROOT_DIR)out/dists/focal/main/binary-amd64/*.deb)

.PHONY: debs $(DEBS)

.PHONY: fix-permissions
fix-permissions:
	docker run -v "$(abspath .)/out:/out" ubuntu:focal-20210713  find /out -group root -exec chown $(UID):$(GID) {} \;

.PHONY: clean
clean: fix-permissions
	rm -rf $(ROOT_DIR)out

test:
	@echo $(DEBS)

debs:
	$(MAKE) -C debs all

$(DEBS):
	$(MAKE) -C debs $(patsubst debs/%, %, $@)

upload: $(OUTPUT)
	$(foreach package, $(OUTPUT), curl -u "$(ARTIFACTORY_USR):$(ARTIFACTORY_PSW)" -XPUT "https://artifactory.osirium.net/artifactory/debian-local/pool/$(notdir $(package));deb.distribution=focal;deb.component=main;deb.architecture=amd64" -T $(package);)
