NAME=daf
HOST=127.0.0.1
PORT=8002
ADDR=127.0.0.1
MANAGE=daf/manage.py
PID=/tmp/.$(NAME).pid
GIT_TAG=$(shell git tag | sort -V | tail -1 | grep . || echo "v0.0.0")
TAG=$(patsubst v%,%,$(GIT_TAG))
IMAGE=z0rr0/daf
BUILDER=daf-multiarch
DOCKER_PLATFORMS=linux/amd64,linux/arm64

.PHONY: all lint test docker docker-push start stop restart

all: test

lint:
	@uv run ruff check .

test: lint
	@mkdir -p daf/static
	uv run $(MANAGE) test podcast

docker: test
	docker buildx build \
		-t $(IMAGE):latest -t $(IMAGE):$(TAG) \
		--load .

docker-push: test
	@test "$(GIT_TAG)" != "v0.0.0" || (echo "no git tag found, refusing to push $(IMAGE):0.0.0" && exit 1)
	@docker buildx inspect $(BUILDER) >/dev/null 2>&1 || docker buildx create --name $(BUILDER) --driver docker-container
	docker buildx build --builder $(BUILDER) \
		--platform $(DOCKER_PLATFORMS) \
		-t $(IMAGE):latest -t $(IMAGE):$(TAG) \
		--push .

start:
	@echo "  >  $(NAME)"
	uv run $(MANAGE) runserver --noreload $(HOST):$(PORT) & echo $$! > $(PID)
	@-cat $(PID)
	@echo "  >  http://$(ADDR):$(PORT)"

stop:
	@-touch $(PID)
	@-cat $(PID)
	@-kill `cat $(PID)` || true
	@-rm $(PID)

restart: stop start
