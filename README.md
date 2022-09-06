# FastApi mono repo template [WIP]

## this project is a template ment to be used as a refrince or a starting point for a mono repo for a restApi backend

### Mono Repo ?

### assumptions ...

### fast start with docker

1. install docker and docker-compose
1. run `docker compose up api-${app name}`

### to create migration file run

`alembic revision -m "short message" --autogenerate`

### to run the tests

`docker compose run --rm pytest-${app name}`
