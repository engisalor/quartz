# NoSkE commands based on https://github.com/ELTE-DH/NoSketch-Engine-Docker

# set current variables
include .env


get_started:
# populates working dir with files for a new project
	cp -i builtin/config/config.yml config.yml
	cp -i builtin/config/environment.env environment/.env
	cp -i builtin/config/environment.env.dev environment/.env.dev
	mkdir assets call components layout markdown pages utils


noske:
# starts noske container
	docker run -d --rm --name noske -p 10070:80 \
	--mount type=bind,src=$(CORPORA_DIR),dst=/corpora \
    $(NOSKE_IMAGE)
	@echo 'URL: http://localhost:10070/'
.PHONY: noske


quartz:
# starts quartz container
	docker run -d --rm --name quartz -p 8080:8080 \
	--mount type=bind,src=$(QUARTZ_DIR),dst=/data \
    $(QUARTZ_IMAGE)
	@echo 'URL: http://localhost:8080/'
.PHONY: quartz


connect:
# connects to container via bash
	docker exec -it noske /bin/bash
.PHONY: connect


execute:
# executes noske command
	docker run --rm -it --mount type=bind,src=$(CORPORA_DIR),dst=/corpora \
     $(NOSKE_IMAGE) "$(CMD)"
.PHONY: execute


compile:
# compiles one corpus
	@read -p "Corpus: " CORPUS; make execute CMD="compilecorp --no-ske --recompile-corpus $$CORPUS"
.PHONY: compile_one
