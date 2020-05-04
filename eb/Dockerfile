FROM python:3.7.7-buster
ENV PYTHONUNBUFFERED=1

USER root

RUN apt-get update -y
RUN pip install --upgrade pip

WORKDIR /code/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY logging_setup.py logging_setup.py
COPY logging.yaml logging.yaml
COPY spider.py spider.py
COPY data/ data/

# switch to a non-root user for security.
RUN useradd jay
RUN chown -R jay /code
USER jay

CMD ["python", "spider.py"]
