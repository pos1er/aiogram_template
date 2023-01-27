FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

# ENV PYTHONPATH /usr/bin/python3

RUN pip3 install --upgrade setuptools
RUN pip3 install -r /app/requirements.txt
# RUN chmod 755 .

COPY . .