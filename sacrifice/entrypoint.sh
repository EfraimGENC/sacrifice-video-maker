#!/bin/sh
echo "ENTRYPOINT SCRIPTI CALISTI ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||"
echo "$DEBUG"
echo "$BUILD_ENV"
echo "$DJANGO_SETTINGS_MODULE"
echo "$APP_PORT"

# Veritabanını bekleyip, migrate işlemini yap
python3 manage.py wait_for_db
python3 manage.py migrate

# CPU çekirdek sayısını al
CPU_CORES=$(nproc)
# CPU çekirdek sayısını yuvarla
CPU_LIMIT=$(awk -v cpus="$CPU_CORES" 'BEGIN { printf "%.0f", cpus }')
# Worker sayısını hesapla
WORKERS=$((2 * CPU_LIMIT + 1))

# Ortak gunicorn komutunu tanımla
run_gunicorn() {
  gunicorn --bind 0.0.0.0:8000 sacrifice.asgi:application \
    -w $1 \
    -k uvicorn.workers.UvicornWorker \
    --worker-tmp-dir /dev/shm \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --timeout 120 \
    --keep-alive 75 \
    $2
}

# Ortak collectstatic komutunu çalıştır
python3 manage.py collectstatic --no-input --clear --settings="${DJANGO_SETTINGS_MODULE}"

# Environment kontrolü
if [ "$BUILD_ENV" = "dev" ]
then
  run_gunicorn 1 "--reload"
else
  run_gunicorn $WORKERS "--preload"
fi
