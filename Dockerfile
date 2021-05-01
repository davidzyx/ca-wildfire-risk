FROM jupyter/base-notebook:python-3.8.8

COPY requirements.txt /tmp
RUN pip --no-cache-dir install -r /tmp/requirements.txt

RUN mkdir /app
WORKDIR /app

COPY --chown=$NB_USER:$NB_GID . .