.PHONY: run build clean

run:
	./scripts/clean_run.sh

build:
	docker-compose build

clean:
	docker-compose down