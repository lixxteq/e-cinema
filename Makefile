APP_PORT=39015
SERVICE_PORT=39016

app:
	gunicorn -c "python:application.wsgi_app._gunicorn" application.wsgi_app.app:app
service:
	uvicorn application.hls_service.main:app --reload --host 0.0.0.0 --port $(SERVICE_PORT)
rund:
	docker-compose up -d
stopd:
	docker-compose stop
startd:
	sudo systemctl start docker
startssh:
	ssh -R 80:localhost:$(APP_PORT) serveo.net

MAKEFLAGS += --jobs=2
run: app service