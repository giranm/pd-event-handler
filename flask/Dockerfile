FROM python:3.7-alpine3.14

WORKDIR /opt

COPY requirements.txt ./
COPY app.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]