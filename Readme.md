docker-compose exec db_forms psql -U admin -d auth_db

make run 

# Узнайте последний тег из Docker Hub или GitHub Actions
export COMMIT_SHA=fca05a5  # замените на актуальный хэш коммита

docker-compose -f docker-compose.prod.yml up