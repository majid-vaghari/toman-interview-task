ARG PYTHON_IMAGE_TAG=3.12-slim

FROM python:$PYTHON_IMAGE_TAG AS base
WORKDIR /app
COPY --chmod=0755 requirements.txt requirements.txt

FROM base AS venv

RUN python -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt

FROM base AS service

COPY --from=venv /opt/venv /opt/venv

# activate virtual env
ENV PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home runner

COPY --chmod=0755 . .

FROM service AS webapp

RUN apt-get update && apt-get install -y gettext

RUN [ "python", "./manage.py", "collectstatic" ]
RUN [ "python", "./manage.py", "compilemessages" ]

USER runner

EXPOSE 8000/tcp

CMD [ "daphne", "-b", "0.0.0.0", "-p", "8000", "wallet.asgi:application" ]

FROM service AS worker

USER runner

CMD [ "celery", "-A", "wallet", "worker", "-l", "info" ]
