until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db_testing" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Run tests
case "${RUN_TESTS}" in
  True) echo "Run tests" && pytest app/tests;;
  * ) echo "Skiping tests";;
esac
