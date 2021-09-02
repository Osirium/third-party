SHELL:=/bin/bash -euo pipefail
ROOT_DIR = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
DEBS = $(patsubst $(ROOT_DIR)%/, %, $(filter %/, $(wildcard $(ROOT_DIR)debs/*/)))
OUTPUT = $(wildcard $(ROOT_DIR)out/dists/xenial/main/binary-amd64/*.deb)

.PHONY: debs $(DEBS)

test:
	@echo $(DEBS)

debs:
	$(MAKE) -C debs all

$(DEBS):
	$(MAKE) -C debs $(patsubst debs/%, %, $@)

upload: $(OUTPUT)
	$(foreach package, $(OUTPUT), curl -u "$(ARTIFACTORY_USR):$(ARTIFACTORY_PSW)" -H "Content-Type: multipart/form-data" --data-binary "@$(package)" "https://nexus.osirium.net/repository/third-party-xenial/";)
