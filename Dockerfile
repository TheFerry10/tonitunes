FROM python:3.12-slim

WORKDIR /app

COPY src/cardsync/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/cardsync /app

EXPOSE 5000

ENV FLASK_APP=cardmanager.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]
