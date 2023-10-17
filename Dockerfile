FROM docker.io/library/python:3.11-slim-bullseye

WORKDIR /code

COPY requirements.txt /

RUN pip install --upgrade pip \
	&& pip install -r /requirements.txt \
	&& rm -rf /root/.cache

COPY ./ ./

EXPOSE 8080

LABEL org.opencontainers.image.source=https://github.com/engisalor/quartz
LABEL org.opencontainers.image.description="Quartz: a corpus linguistics visualization tool for Sketch Engine servers"
LABEL org.opencontainers.image.licenses=GPL-3.0-or-later
LABEL org.opencontainers.image.version="0.2.1"

ENTRYPOINT ["gunicorn", "--config", "gunicorn_config.py", "app:server"]
