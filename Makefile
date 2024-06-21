APP_PORT=39015
SERVICE_PORT=39016

app:
	gunicorn -c "python:application.wsgi_app._gunicorn"
service:
	uvicorn application.hls_service.main:app --reload --host 127.0.0.1 --port $(SERVICE_PORT)
	# python application/hls_service/_uvicorn.py
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