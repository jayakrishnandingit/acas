FROM python:3.7.7-buster
ENV PYTHONUNBUFFERED=1

USER root

RUN apt-get update -y
RUN pip install --upgrade pip

WORKDIR /code/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY spider.py spider.py

# switch to a non-root user for security.
RUN useradd jay
RUN chown -R jay /code
USER jay

CMD ["python", "spider.py"]
