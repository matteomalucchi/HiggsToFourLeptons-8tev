FROM rootproject/root:6.24.06-ubuntu20.04

RUN mkdir /app

WORKDIR /app

RUN apt-get update

RUN apt-get install python3 python3-pip -y

COPY docs/requirements.txt .

RUN python3 -m pip install -r docs/requirements.txt

COPY . .

 RUN python3 -m unittest
