NUX-server
===

Run `docker compose up --build`

### Run tests
Prepare database (run once) `docker compose -f docker-compose-tests.yml up -d --remove-orphans`

Prepare env vars
* `source .env && export $(cut -d= -f1 .env)`
* `export POSTGRES_HOST=localhost:5433`
Run tests `pytest`
