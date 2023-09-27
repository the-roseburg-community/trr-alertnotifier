FROM python:3.9.18-alpine3.17

WORKDIR /app

RUN pip3 install requests mailersend bs4

COPY . .

CMD ["python3", "alert-check.py"]
