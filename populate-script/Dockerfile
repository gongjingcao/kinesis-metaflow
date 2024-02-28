FROM python:3.8

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY populate_stream.py /app/

ENV PYTHONUNBUFFERED=1

CMD ["python", "populate_stream.py"]
