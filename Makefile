.PHONY: (
	      install test test-api-v1 \
          runserver-dev runserver \
		  run-proxy-server run-static-server \
		  run-proxy-server-uwsgi run-static-server-uwsgi \
		  uwsgi-proxy uwsgi-static \
		  deploy clear-expired-extracts
	)

PYTHON := uv run --active python
PIP := $(PYTHON) -m pip
HOST := 0.0.0.0

default: install test runserver

# Target to install dependencies
install:
	uv sync

# Target to run tests
test: test-api-v1

# Target to test RestAPI V1
test-api-v1:
	$(PYTHON) -m pytest tests/test_v1.py -xv

# Delete cached expired extracted info
clear-expired-extracts:
	$(PYTHON) -m app utils delete-expired-extracts

# Target to run development server
runserver-dev:
	$(PYTHON) -m fastapi dev app

# Target to run production server
runserver:
	$(PYTHON) -m fastapi run app

run-proxy-server:
	$(PYTHON) -m servers.proxy http://localhost:8000 --host $(HOST)

run-proxy-server-uwsgi:
	./uwsgi.sh proxy

run-static-server:
	$(PYTHON) -m servers.static --host $(HOST)

run-static-server-uwsgi:
	./uwsgi.sh static

uwsgi-static:
	uwsgi --ini configs/uwsgi/static.ini

uwsgi-proxy:
	uwsgi --ini configs/uwsgi/proxy.ini

kill-uwsgi:
	pkill uwsgi

deploy: install test runserver