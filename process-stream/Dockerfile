FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install metaflow

COPY . /app/

ENV PYTHONUNBUFFERED=1

CMD ["python", "listener.py"]