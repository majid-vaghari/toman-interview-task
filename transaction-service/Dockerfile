FROM python:3.12-slim

WORKDIR /app

COPY --chmod=0755 . .

RUN pip install -r requirements.txt

RUN useradd --create-home runner

USER runner

EXPOSE 8010

CMD [ "daphne", "-b", "0.0.0.0", "-p", "8010", "app:asgi_app" ]
