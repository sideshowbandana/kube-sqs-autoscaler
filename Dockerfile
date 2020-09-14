FROM python:3.8.5
WORKDIR /usr/src/app

COPY scripts/dependencies.sh /tmp/dependencies.sh
RUN /tmp/dependencies.sh

COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY . .
