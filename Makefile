.PHONY: install run-scrape run-full docker-build docker-run

install:
	pip install -r requirements.txt

run-scrape:
	python -m src.main --scraper basic

run-full:
	python -m src.main --scraper full

docker-build:
	docker-compose build

docker-run:
	docker-compose run app
