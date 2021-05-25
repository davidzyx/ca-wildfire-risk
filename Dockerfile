FROM jupyter/base-notebook:python-3.8.8

# selenium stuff
USER root
RUN apt-get update && apt-get install curl unzip xvfb libxi6 libgconf-2-4 gnupg -y && apt-get clean
RUN wget https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_linux64.zip -O /tmp/chrome.zip && \
    unzip /tmp/chrome.zip -d /usr/bin && \
    chmod a+x /usr/bin/chromedriver && \
    rm /tmp/chrome.zip

RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add && \
    echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get -y update && \
    apt-get -y install google-chrome-stable && \
    apt-get clean


# python stuff
USER $NB_USER
COPY requirements.txt /tmp
RUN pip --no-cache-dir install -r /tmp/requirements.txt

WORKDIR /app
COPY --chown=$NB_USER:$NB_GID . /app

USER root
RUN chown $NB_USER:$NB_GID /app

USER $NB_USER

EXPOSE 8050
CMD python src/app.py
