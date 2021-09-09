SHELL:=/bin/bash -euo pipefail
UID = $(shell id -u)
GID = $(shell id -g)
ROOT_DIR = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
DEBS = $(patsubst $(ROOT_DIR)%/, %, $(filter %/, $(wildcard $(ROOT_DIR)debs/*/)))
OUTPUT = $(wildcard $(ROOT_DIR)out/dists/focal/main/binary-amd64/*.deb)

.PHONY: debs $(DEBS)

.PHONY: fix-permissions
fix-permissions:
	docker run -v "$(abspath .):/third-party" ubuntu:focal-20210713  find /third-party/out -group root -exec chown $(UID):$(GID) {} \;

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
	$(foreach package, $(OUTPUT), curl -u "$(AD_USR):$(AD_PSW)" -H "Content-Type: multipart/form-data" --data-binary "@$(package)" "https://nexus.osirium.net/repository/third-party-focal/";)
