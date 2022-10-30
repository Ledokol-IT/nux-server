NUX-server
===

Run `docker compose up --build`

### Run tests
Prepare database (run once) `docker compose -f docker-compose-tests.yml up -d --remove-orphans`
Run tests `pytest`
