# ---------- overridable ----------
REGISTRY        ?= docker.io
DOCKER_USER     ?= elemusbarrios
IMAGE_NAME      ?= sqliteapi
CONTEXT_DIR     ?= ./sqliteapi
DOCKERFILE_PATH ?= $(CONTEXT_DIR)/Dockerfile

TAGS            ?= latest 0.1.0

# Puerto interno real del contenedor (uvicorn en main.py)
INTERNAL_PORT   ?= 8500
HOST_PORT       ?= 8500

DATA_DIR        ?= ./sqliteapi/data
SQLITE_PATH     ?= /app/sqliteapi/data/ADS_METRICS.sqlite

# ---------- computed --------------
IMAGE_FULL_NAME := $(REGISTRY)/$(DOCKER_USER)/$(IMAGE_NAME)
DEFAULT_TAG     := $(firstword $(TAGS))

# ---------- meta ----------
.PHONY: all help build publish clean run stop logs test tag-ls

all: clean build                  ## limpia y compila

help:                             ## imprime ayuda inline
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | \
	  sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ---------- build & publish ----------
build:                            ## build + retag para cada TAG
	docker build -f $(DOCKERFILE_PATH) -t $(IMAGE_FULL_NAME):$(DEFAULT_TAG) $(CONTEXT_DIR)
	$(foreach tag,$(filter-out $(DEFAULT_TAG),$(TAGS)), \
	  docker tag $(IMAGE_FULL_NAME):$(DEFAULT_TAG) $(IMAGE_FULL_NAME):$(tag);)

publish:                          ## push de todas las TAGS
	$(foreach tag,$(TAGS), docker push $(IMAGE_FULL_NAME):$(tag);)

tag-ls:                           ## lista imágenes locales
	@docker images $(IMAGE_FULL_NAME) --format '{{.Repository}}:{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}'

clean:                            ## borra imágenes locales + prune
	-$(foreach tag,$(TAGS), docker rmi -f $(IMAGE_FULL_NAME):$(tag);)
	docker system prune -f

# ---------- ciclo local ----------
run:                              ## levanta el contenedor local para pruebas
	mkdir -p $(DATA_DIR)
	docker run -d --rm \
	  --name $(IMAGE_NAME) \
	  -p $(HOST_PORT):$(INTERNAL_PORT) \
	  -e SQLITE_DB_PATH=$(SQLITE_PATH) \
	  -v $(PWD)/sqliteapi/data:/app/sqliteapi/data \
	  $(IMAGE_FULL_NAME):$(DEFAULT_TAG)

stop:                             ## detiene el contenedor local
	- docker stop $(IMAGE_NAME)

logs:                             ## muestra logs del contenedor
	docker logs -f $(IMAGE_NAME)

test:                             ## prueba endpoint /metrics
	curl -s http://localhost:$(HOST_PORT)/health | jq .
