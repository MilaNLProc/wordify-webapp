.PHONY: help build dev integration-test push
.DEFAULT_GOAL := help

# Docker image build info
PROJECT:=wordify-webapp
BUILD_TAG?=latest

ALL_IMAGES:=src

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "Wordify webapp"
	@echo "====================="
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

########################################################
## Local development
########################################################

build: ## Build the latest image
	docker build -t $(PROJECT):${BUILD_TAG} .

exec: DARGS?=-v $(PWD):/app
exec: ## Exec into the container
	docker run -it --rm $(DARGS) $(PROJECT) bash

dev: DARGS?=-v $(PWD):/app -p 6006:80  # NOTE docker port must be 80
dev: ## Run dev mode (do not detach terminal)
	docker run --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}

container: DARGS?=-v $(PWD):/app -p 6006:80  # NOTE docker port must be 80
container: ## Run wordify
	docker run -d --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}

deploy: ## Deployment
	git pull origin master
	docker stop wordify-container
	docker image rm $(PROJECT):${BUILD_TAG}
	docker build -t $(PROJECT):${BUILD_TAG} .
	docker run -d --name wordify-container -it --rm $(DARGS) $(PROJECT):${BUILD_TAG}


