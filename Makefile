.PHONY: help build dev integration-test push
.DEFAULT_GOAL := help

# Docker image build info
PROJECT:=wordify-webapp
BUILD_TAG?=latest

ALL_IMAGES:=src

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "R starter project"
	@echo "====================="
	@echo "Replace % with a directory name (e.g., make build/rstats-example)"
	@echo
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

########################################################
## Local development
########################################################

build: ## Build the latest image
	docker build -t $(PROJECT):${BUILD_TAG} .

exec: DARGS?=-v $(PWD):/app
exec: ## Exec into the container
	docker run -it --rm $(DARGS) $(PROJECT) bash

dev: DARGS?=-v $(PWD):/app -p 8787:5000 --entrypoint bash  # NOTE docker port must be 80
dev: 
	docker run --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}

container: DARGS?=-p 8787:80  # NOTE docker port must be 80
container: 
	docker run -d --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}
