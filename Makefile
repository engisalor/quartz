# NoSkE commands based on https://github.com/ELTE-DH/NoSketch-Engine-Docker

# set current variables
include .env


get_started:
# populates working dir with files for a new project
	mkdir -p custom/config
	cp -i builtin/config/environment.env environment/.env
	cp -i builtin/config/environment.env.dev environment/.env.dev
	cp -i builtin/config/corpora-ske.yml custom/config/corpora-ske.yml
	cp -i builtin/config/corpora-noske.yml custom/config/corpora-noske.yml
	cp -i builtin/config/labels.yml custom/config/labels.yml


noske:
# starts noske container
	docker run -d --rm --name noske -p 10070:80 \
	--mount type=bind,src=$(CORPORA_DIR),dst=/corpora \
    $(NOSKE_IMAGE)
	@echo 'URL: http://localhost:10070/'
.PHONY: noske


quartz:
# starts quartz container
	export SGEX_CONFIG_JSON=$(SGEX_CONFIG_JSON) SERIALIZER_KEY=$(SERIALIZER_KEY) && \
	docker run -d --rm \
	-e SGEX_CONFIG_JSON -e SERIALIZER_KEY \
	--name quartz -p 8080:8080 \
	--mount type=bind,src=$(QUARTZ_DIR),dst=/data \
    $(QUARTZ_IMAGE)
	@echo 'URL: http://localhost:8080/'
.PHONY: quartz
