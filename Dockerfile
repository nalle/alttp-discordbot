FROM alpine

COPY requirements.txt /tmp/requirements.txt
RUN apk update && \
    apk add python3 py3-virtualenv nginx gcc python3-dev libc-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt
RUN mkdir -p /run/nginx/

COPY default.conf /etc/nginx/sites-enabled/default
COPY bot /opt/discordbot/bot
COPY alttp.py /opt/discordbot
COPY start.sh /opt/discordbot
WORKDIR /opt/discordbot

RUN touch /tmp/index.html
CMD sh start.sh
