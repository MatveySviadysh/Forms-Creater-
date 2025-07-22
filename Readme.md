docker-compose exec db_forms psql -U admin -d auth_db

make run 

export COMMIT_SHA=fca05a5

docker-compose -f docker-compose.prod.yml up

alembic init migrations