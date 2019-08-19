FROM python:3.7

RUN mkdir /code
WORKDIR /code

RUN apt-get update
RUN apt-get -f install
RUN pip3 install --upgrade pip
ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
CMD ["python"]

