.PHONY: compose-up compose-down delete-db delete-images clean migrate-db

all: secrets .env compose-up migrate-db

secrets:
	mkdir secrets
	openssl rand -base64 48 > secrets/db-password.txt
	openssl rand -base64 48 > secrets/django-secret.txt

	echo postgres > secrets/db-host.txt
	echo walletdb > secrets/db-name.txt
	echo walletuser > secrets/db-user.txt

.env:
	cp dev.env .env

compose-up:
	docker compose up --detach

compose-down:
	docker compose down

delete-db:
	docker compose down --volumes

delete-images:
	docker compose down --rmi local

clean:
	docker compose down --volumes --rmi local

migrate-db: ## wait for services to be up and then run migrations
	docker compose exec wallet python manage.py migrate || sleep 2 && docker compose exec wallet python manage.py migrate

