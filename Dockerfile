FROM python:3.9-slim-buster
RUN useradd --create-home bot
WORKDIR /usr/src/bot
COPY --chown=bot requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends sudo \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt --no-cache-dir \ 
    && apt-get purge -y && touch /etc/sudoers.d/bot \
    && echo "bot ALL=NOPASSWD: /usr/bin/apt" > /etc/sudoers.d/bot
USER bot
COPY --chown=bot src/. .
CMD ["python", "/usr/src/bot/tg2.py", "/usr/src/bot/config.yaml"]
