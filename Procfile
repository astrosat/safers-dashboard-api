#web: python manage.py runserver 0.0.0.0:$PORT
web: cd server && gunicorn config.wsgi
release: cd server && python manage.py migrate
rmq_worker: cd server && python -m safers.rmq.server

