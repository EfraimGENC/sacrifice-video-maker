# Makefile

# Load .env file if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

# Variables
DOCKER_COMPOSE_DEV = docker compose -f docker-compose.yml -f docker-compose.override.yml
DOCKER_COMPOSE_PROD = docker compose -f docker-compose.yml -f docker-compose.prod.yml

.PHONY: build build-no-cache up down logs restart pull prune git-pull rebuild rebuild-no-cache update makemigrations migrate createsuperuser collectstatic shell test

# Check if ENV is set, default to 'dev'
ifeq ($(BUILD_ENV), prod)
    DOCKER_COMPOSE = $(DOCKER_COMPOSE_PROD)
else
    DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)
endif
DOCKER_EXEC_MANAGE = $(DOCKER_COMPOSE) exec app python manage.py

# Build the Docker Compose services
build:
	$(DOCKER_COMPOSE) build

# Build the Docker Compose services with no cache
build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

# Start the Docker Compose services
up:
	$(DOCKER_COMPOSE) up -d

# Stop the Docker Compose services
down:
	$(DOCKER_COMPOSE) down

# View logs for the Docker Compose services
logs:
	$(DOCKER_COMPOSE) logs -tf

# Restart the Docker Compose services
restart:
	$(DOCKER_COMPOSE) restart

# Pull the Docker Compose services
pull:
	$(DOCKER_COMPOSE) pull --ignore-pull-failures

# Docker prune
prune:
	docker system prune --all --volumes --force
	docker builder prune --all --force

# Git pull
git-pull:
	git pull

# Clean and rebuild the Docker Compose services
rebuild: down pull build up prune logs

# Clean and rebuild the Docker Compose services with no cache
rebuild-no-cache: down pull build-no-cache up prune logs

# Update
update: down git-pull rebuild-no-cache


# Django Commands

# Run Django makemigrations
makemigrations:
	$(DOCKER_EXEC_MANAGE) makemigrations

# Run Django migrations
migrate:
	$(DOCKER_EXEC_MANAGE) migrate

# Create a Django superuser
createsuperuser:
	$(DOCKER_EXEC_MANAGE) createsuperuser

# Collect static files for Django
collectstatic:
	$(DOCKER_EXEC_MANAGE) collectstatic --noinput

# Open a Django shell
shell:
	$(DOCKER_EXEC_MANAGE) shell_plus --ipython

# Run Django tests
test:
	$(DOCKER_EXEC_MANAGE) test
