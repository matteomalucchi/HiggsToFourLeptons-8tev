FROM rootproject/root:latest

RUN mkdir /app

WORKDIR /app

COPY cachecontrol .

RUN apt-get install python3-pip -y

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . .

RUN python -m unittest
