#!/bin/sh
echo "ENTRYPOINT SCRIPTI CALISTI ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
echo "$DEBUG"
echo "$BUILD_ENV"
echo "$DJANGO_SETTINGS_MODULE"
echo "$APP_PORT"

python3 manage.py wait_for_db
python3 manage.py migrate

# CPU cekirdek sayisini al
CPU_CORES=$(nproc)
# CPU cekirdek sayisini yuvarla
CPU_LIMIT=$(awk -v cpus="$CPU_CORES" 'BEGIN { printf "%.0f", cpus }')
# Worker sayisini hesapla
WORKERS=$((2 * CPU_LIMIT + 1))

if [ "$BUILD_ENV" = "dev" ]
then
  python3 manage.py runserver 0.0.0.0:8000
else
  python3 manage.py collectstatic --no-input --clear --settings="${DJANGO_SETTINGS_MODULE}"
  gunicorn --bind 0.0.0.0:8000 sacrifice.asgi:application -w $WORKERS -k uvicorn.workers.UvicornWorker --worker-tmp-dir /dev/shm --log-level debug --access-logfile - --error-logfile -
fi
