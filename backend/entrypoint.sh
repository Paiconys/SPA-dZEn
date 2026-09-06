#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time
import MySQLdb

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))
user = os.environ.get("DB_USER", "spa_user")
password = os.environ.get("DB_PASSWORD", "spa_password")
name = os.environ.get("DB_NAME", "spa_dzen")

for i in range(60):
    try:
        conn = MySQLdb.connect(
            host=host, port=port, user=user, passwd=password, db=name
        )
        conn.close()
        print("Database is ready.")
        break
    except Exception as exc:
        print(f"DB not ready ({exc}), retry {i + 1}/60...")
        time.sleep(2)
else:
    raise SystemExit("Database did not become ready in time.")
PY

python manage.py migrate --noinput
exec "$@"
