FROM python:3.12-slim

WORKDIR /app

COPY src/cardsync/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/cardsync /app

EXPOSE 5000

CMD ["flask", "run"]
