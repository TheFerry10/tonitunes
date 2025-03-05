FROM python:3.12-slim


WORKDIR /code
COPY . /code
RUN pip install --no-cache-dir -r src/app/requirements.txt
RUN pip install -e .
WORKDIR /code/src/app

EXPOSE 5000

ENV FLASK_APP=cardmanager.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "cardmanager:create_app()"]
