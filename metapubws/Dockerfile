FROM python:3.7-alpine
WORKDIR /code
RUN apk update && \
    apk upgrade
ENV FLASK_APP=metapubws.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apk add --no-cache gcc musl-dev linux-headers libxslt-dev
COPY requirements.txt requirements.txt
COPY metapubws.py metapubws.py
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask","run"]
