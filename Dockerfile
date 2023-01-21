FROM docker.io/library/python:3.11-slim-bullseye

WORKDIR /code

COPY requirements.txt /

RUN pip install -r /requirements.txt \
	&& rm -rf /root/.cache

COPY ./ ./

ENV ENVIRONMENT_FILE=".env"

EXPOSE 8080

ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app:server"]
