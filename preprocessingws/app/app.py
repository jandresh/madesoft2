from urllib.request import Request, urlopen
import pdftotext
import geograpy
import pdftotext
from nltk import Tree
from nltk import word_tokenize, pos_tag, ne_chunk
from flask import Flask, jsonify, request
import time
import textract
import re
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
from langdetect import detect
import urllib.parse

app = Flask(__name__)


def get_continuous_chunks(text, label):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    prev = None
    continuous_chunk = []
    current_chunk = []

    for subtree in chunked:
        if type(subtree) == Tree and subtree.label() == label:
            current_chunk.append(
                " ".join([token for token, pos in subtree.leaves()]))
        if current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue

    return continuous_chunk


def file_download(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    datatowrite = urlopen(req).read()
    with open('article.pdf', 'wb') as f:
        f.write(datatowrite)
        f.close()
    return r"article.pdf"


def text_from_pdf_file(path):
    with open(path, "rb") as f:
        pdf = pdftotext.PDF(f)
        f.close()
    return "\n\n".join(pdf)


def head_extract(path):
    text = text_from_pdf_file(path)
    return text[:re.search(r'[aA]bstract', text).start(0)]


@app.route('/')
def helloworld():
    return 'metapubws endpoints: /\n/url2text\n/url2htext\n/text2locations\n/text2places\n/text2ner\n/text2emails'

# *****text_from_pdf_url()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2text


@app.route("/url2text", methods=['POST'])
def text_from_pdf_url():
    if not request.json:
        abort(400)
    url = request.json['url']
    return jsonify(pdf2text=text_from_pdf_file(file_download(url)))

# *****htext_from_url()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "url": "http://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7350007&blobtype=pdf"}' http://localhost:5002/url2htext


@app.route("/url2htext", methods=['POST'])
def htext_from_url():
    if not request.json:
        abort(400)
    url = request.json['url']
    return jsonify(htext=head_extract(file_download(url)))

# *****locations_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2locations


@app.route("/text2locations", methods=['POST'])
def locations_from_text():
    if not request.json:
        abort(400)
    text = request.json['text']
    return jsonify(locations=get_continuous_chunks(text, 'GPE'))

# *****places_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2places


@app.route("/text2places", methods=['POST'])
def places_from_text():
    if not request.json:
        abort(400)
    text = request.json['text']
    return jsonify(places=geograpy.get_place_context(text=text))

# *****ner_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2ner


@app.route("/text2ner", methods=['POST'])
def ner_from_text():
    if not request.json:
        abort(400)
    text = request.json['text']
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    nltk.chunk.ne_chunk(tagged)
    return jsonify(entities=nltk.chunk.ne_chunk(tagged))

# *****emails_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2emails

@app.route("/text2emails", methods=['POST'])
def emails_from_text():
    if not request.json:
        abort(400)
    text = request.json['text']
    return jsonify(emails=re.findall(r'[\w\.-]+@[\w\.-]+', text))

# *****language_from_text()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "text": ""}' http://localhost:5002/text2lang

@app.route("/text2lang", methods=['POST'])
def language_from_text():
    if not request.json:
        abort(400)
    return jsonify(lang=detect(request.json['text'].lower()))
