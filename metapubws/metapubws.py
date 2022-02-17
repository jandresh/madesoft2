#!/usr/bin/env python
#
# Author: Jaime Hurtado - jaime.hurtado@correounivalle.edu.co
# Fecha: 2021-03-02
#
from flask import Flask, jsonify, request
from metapub import PubMedFetcher
from metapub import FindIt

app = Flask(__name__)

#
# Este metodo retorna informacion de microservicios disponibles
#

@app.route('/')
def root():
    return 'metapubws endpoints: /title, /abstract, /pmids'

#
# *****title_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/title
#


@app.route("/title", methods=['POST'])
def title_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json['id']
    article = fetch.article_by_pmid(pmid)
    return jsonify(title=article.title)
#
# *****abstract_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/abstract
#


@app.route("/abstract", methods=['POST'])
def abstract_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json['id']
    article = fetch.article_by_pmid(pmid)
    return jsonify(abstract=article.abstract)
#
# *****pmid_from_query()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "breast neoplasm" }' http://localhost:5000/pmids
#


@app.route("/pmids", methods=['POST'])
def pmid_from_query():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    query = request.json['query']
    pmids = fetch.pmids_for_query(query, retmax=10000)
    return jsonify(pmids=pmids)

#
# *****metadata_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "2020202" }' http://localhost:5000/metadata
#


@app.route("/metadata", methods=['POST'])
def metadata_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json['id']
    try:
        article = fetch.article_by_pmid(pmid)
    except:  # Pendiente manejo excepciones
        article = None
    return jsonify(
        pmid=article.pmid,
        title=article.title,
        abstract=article.abstract,
        citation=article.citation,
        pubmed_type=article.pubmed_type,
        url=article.url,
        authors=article.authors,
        # author_list=article.author_list, #Puede no funionar porque devuelve una lista
        # authors_str=article.authors_str,
        # author1_last_fm=article.author1_last_fm,
        # author1_lastfm=article.author1_lastfm,
        # pages=article.pages,
        # first_page=article.first_page,
        # last_page=article.last_page,
        # volume=article.volume,
        # issue=article.issue,
        # volume_issue=article.volume_issue,
        doi=article.doi,
        # pii=article.pii,
        # pmc=article.pmc,
        # issn=article.issn,
        # mesh=article.mesh,
        # chemicals=article.chemicals,
        # grants=article.grants,
        # publication_types=article.publication_types,
        # book_accession_id=article.book_accession_id,
        # book_title=article.book_title,
        # book_publisher=article.book_publisher,
        # book_language=article.book_language,
        # book_editors=article.book_editors,
        # book_abstracts=article.book_abstracts,
        # book_sections =article.book_sections,
        # book_copyright=article.book_copyright,
        # book_medium=article.book_medium,
        # book_synonyms=article.book_synonyms,
        # book_publication_status=article.book_publication_status,
        # book_history =article.book_history ,
        # book_contribution_date=article.book_contribution_date,
        # book_date_revised=article.book_date_revised,
        # journal=article.journal,
        year=article.year
        # history=article.history,
    )

#
# *****pdf_from_pmid()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "id": "32599772"}' http://localhost:5000/pmid2pdf


@app.route("/pmid2pdf", methods=['POST'])
def pdf_from_pmid():
    fetch = PubMedFetcher()
    if not request.json:
        abort(400)
    pmid = request.json['id']
    src = FindIt(pmid)
    print(src.url)
    return jsonify(
        pdf_url=src.url
    )
