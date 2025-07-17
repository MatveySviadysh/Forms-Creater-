.PHONY: run build clean

run:
	./scripts/clean_run.sh
	docker-compose down && docker-compose up --build

build:
	docker-compose build

clean:
	docker-compose down