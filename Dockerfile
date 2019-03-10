FROM debian

COPY requirements.txt /tmp/requirements.txt
RUN apt-get update && \
    apt-get install -y python3 python3-virtualenv python3-pip python-dev nginx 
RUN pip3 install -r /tmp/requirements.txt

COPY default.conf /etc/nginx/sites-enabled/default
COPY bot /opt/discordbot/bot
COPY alttp.py /opt/discordbot
COPY start.sh /opt/discordbot
WORKDIR /opt/discordbot

RUN touch /tmp/index.html
CMD ./start.sh
