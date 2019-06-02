FROM alpine

COPY requirements.txt /tmp/requirements.txt
RUN apk update && \
    apk add python3 py3-virtualenv gcc python3-dev libc-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/requirements.txt

COPY bot /opt/discordbot/bot
COPY main.py /opt/discordbot
COPY templates /opt/discordbot/templates
WORKDIR /opt/discordbot

CMD python3 -u main.py
