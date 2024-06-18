# Makefile

# Load .env file if it exists
ifneq (,$(wildcard ./.env))
    include .env
    export $(shell sed 's/=.*//' .env)
endif

# Variables
DOCKER_COMPOSE_DEV = docker-compose -f docker-compose.yml -f docker-compose.override.yml
DOCKER_COMPOSE_PROD = docker-compose -f docker-compose.yml -f docker-compose.prod.yml

.PHONY: up down logs restart pull makemigrations migrate createsuperuser shell test rebuild rebuild-no-cache collectstatic

# Check if ENV is set, default to 'dev'
ifeq ($(BUILD_ENV), prod)
    DOCKER_COMPOSE = $(DOCKER_COMPOSE_PROD)
else
    DOCKER_COMPOSE = $(DOCKER_COMPOSE_DEV)
endif

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

# Run Django makemigrations
makemigrations:
	$(DOCKER_COMPOSE) exec app python manage.py makemigrations

# Run Django migrations
migrate:
	$(DOCKER_COMPOSE) exec app python manage.py migrate

# Create a Django superuser
createsuperuser:
	$(DOCKER_COMPOSE) exec app python manage.py createsuperuser

# Open a Django shell
shell:
	$(DOCKER_COMPOSE) exec app python manage.py shell_plus --ipython

# Run Django tests
test:
	$(DOCKER_COMPOSE) exec app python manage.py test

# Clean and rebuild the Docker Compose services
rebuild:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d

# Clean and rebuild the Docker Compose services with no cache
rebuild-no-cache:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d

# Collect static files for Django
collectstatic:
	$(DOCKER_COMPOSE) exec app python manage.py collectstatic --noinput
