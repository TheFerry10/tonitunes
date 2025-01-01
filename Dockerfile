FROM python:3.12-slim

WORKDIR /app

COPY src/app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app /app

EXPOSE 5000

ENV FLASK_APP=cardmanager.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "cardmanager:create_app()"]