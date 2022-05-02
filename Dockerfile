FROM rootproject/root:6.24.06-conda

RUN mkdir /app

WORKDIR /app

RUN apt-get install python3-pip -y

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . .

RUN python -m unittest
