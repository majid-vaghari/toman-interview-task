FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 8010

ENTRYPOINT [ "daphne" ]

CMD [ "-b 0.0.0.0", "-p 8010", "app:asgi_app" ]
