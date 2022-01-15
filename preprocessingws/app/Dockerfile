# FROM python:3.7-alpine
FROM python:3.9.9-bullseye
WORKDIR /app
ENV DEBIAN_FRONTEND="noninteractive"
RUN apt-get update && \ 
    apt-get -y upgrade
RUN apt-get -y install python3-sklearn python3-sklearn-lib
RUN apt-get -y install python3-pandas
RUN apt-get -y install build-essential libpoppler-cpp-dev pkg-config python-dev
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
# RUN apk add --no-cache gcc musl-dev linux-headers libxslt-dev
COPY requirements.txt /app
COPY app.py /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask","run"]
