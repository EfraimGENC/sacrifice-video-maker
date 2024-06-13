

### Quickstart
1. Create your `.env` file based on `env-sample`.
2. Run the following docker commands.
3. Create superuser in app container with [django command](https://docs.djangoproject.com/en/4.2/intro/tutorial02/#creating-an-admin-user).

```shell
docker compose down
docker compose pull --ignore-pull-failures
docker compose build --no-cache
docker compose up -d
docker compose logs -tf
```

Docker Web Container Execute
```shell
docker compose run --rm app bash
```

Open Shell Plus with ipython 
```shell
docker compose run --rm app ./manage.py shell_plus --ipython
```