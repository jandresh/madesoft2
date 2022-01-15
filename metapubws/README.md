# metapubws
Use of metapub python library as web service for get metadata from pubmed scientific articles

Use:

1. Clone Repository

```
git clone https://github.com/jandresh/metapubws.git
```

2. Execute next commands with Pubmed Key:

```
virtualenv venv
. venv/bin/activate
sudo apt-get install libxml2-dev libxslt-dev python3-dev
pip3 install Flask metapub
export FLASK_APP=metapubws.py
export NCBI_API_KEY="CHANGE_WITH_PUBMED_KEY”
flask run --host=0.0.0.0
```

3. Use of web service with CURL:

```
curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/title
```