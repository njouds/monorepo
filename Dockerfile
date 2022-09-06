FROM python:3.10-slim AS production

ARG APP_NAME
ARG RELEASE_SHA=unknown

ENV RELEASE_SHA=$RELEASE_SHA
ENV MODULE_NAME=$APP_NAME.app.main:app
ENV WORKER_CLASS=uvicorn.workers.UvicornWorker
ENV PYTHONPATH=/app
ENV GUNICORN_CONF=/app/gunicorn_conf.py
ENV SQLALCHEMY_WARN_20=true

COPY /start.sh /start.sh
RUN chmod +x /start.sh

COPY /start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

WORKDIR /app/
EXPOSE 80


COPY $APP_NAME/requirements.txt $APP_NAME/requirements.txt
COPY commons/requirements.txt commons/requirements.txt

# to build psycopg2
RUN apt-get update \
    && apt-get install -y libpq-dev gcc openssl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir --upgrade pip \
    pip install --no-cache-dir -r $APP_NAME/requirements.txt


COPY init_db.py /app
COPY commons/gunicorn_conf.py /app
COPY $APP_NAME /app/$APP_NAME
COPY commons /app/commons

# Run the start script, it will run the init_db.py file.
# And then will start Gunicorn with Uvicorn
CMD ["/start.sh"]

FROM production AS dev

ARG APP_NAME
RUN pip install -r $APP_NAME/requirements-dev.txt

