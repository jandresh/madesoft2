from flask import Flask, jsonify, request
import requests
import urllib.parse

app = Flask(__name__)

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def get_json_orcid_request(id_type, doc_id):
    url = 'https://pub.sandbox.orcid.org/v3.0/expanded-search'
    headers = {'Accept': 'application/json',}
    params = (('q', f'{id_type}-self:{doc_id}'),)
    return requests.get(url, headers=headers, params=params).json()

#
# Este metodo retorna informacion de microservicios disponibles
#

@app.route('/')
def root():
    return 'orchestratorws endpoints: /'

@app.route('/pipeline3', methods=['GET'])
def pipeline3():
    try:
        patterns_list = post_json_request(
            'http://dbws:5000/mysql-query',
            {"query" : "select * from patterns"}
        )
    except:
        patterns_list = None
    create_mongo_db = post_json_request(
        'http://dbws:5000/mongo-db-create',
        {"db-name" : "adccali"}
    )
    actual_pattern = 1
    if patterns_list is not None and create_mongo_db == 0:
        for pattern in patterns_list:
            create_mongo_coll_metadata = post_json_request(
                'http://dbws:5000/mongo-coll-create',
                {
                    "db-name" : "adccali",
                    "coll-name" : "metadata{}".format(actual_pattern)
                }
            )
            create_mongo_coll_author_vs_doc_id = post_json_request(
                'http://dbws:5000/mongo-coll-create',
                {
                    "db-name" : "adccali",
                    "coll-name" : "author_vs_doc_id{}".format(actual_pattern)
                }
            )
            print(f"pattern id: {pattern['id']}")
            if (pattern['db'] == 'PUBMED'):
                try:
                    pmids_json = post_json_request(
                        'http://metapubws:5000/pmids', {"query": pattern['pattern']})
                    pmids = pmids_json['pmids']
                except:
                    pmids = None
                print(f"pmids count: {len(pmids)}")
                if pmids is not None:
                    for pmid in pmids:
                        print(f"actual pmid: {pmid}")
                        if pmid is not None:
                            try:
                                orcid = get_json_orcid_request("pmid", str(pmid))['expanded-result'][0]['orcid-id']
                            except:
                                orcid = ""
                            try:
                                metadata_json = post_json_request(
                                    'http://metapubws:5000/metadata', {"id": "{}".format(pmid)})
                            except:
                                metadata_json = None
                                print(f"can't get metadata for {pmid}")
                            try:
                                if metadata_json['abstract'] is not None:
                                    text = metadata_json['abstract']
                                elif metadata_json['title'] is not None:
                                    text = metadata_json['title']
                                else:
                                    text = ""
                                lang_json = post_json_request(
                                    'http://preprocessingws:5000/text2lang', {"text": text})
                                print(f"lang: {lang_json['lang']}")
                            except:
                                lang_json['lang'] = ""
                                print(f"can't get language for {pmid}")
                            if metadata_json is not None:
                                success_doc_insert = 1
                                try:
                                    success_doc_insert = post_json_request(
                                        'http://dbws:5000/mongo-doc-insert',
                                        {
                                            "db-name" : "adccali",
                                            "coll-name" : "metadata{}".format(actual_pattern),
                                            "document" : {
                                                "pat_id": pattern['id'] if pattern['id'] is not None else "",
                                                "pmid" : metadata_json['pmid'] if metadata_json['pmid'] is not None else "",
                                                "coreid" : "",
                                                "doi" : metadata_json['doi'] if metadata_json['doi'] is not None else "",
                                                "orcid" : orcid,
                                                "title" : metadata_json['title'] if metadata_json['title'] is not None else "",
                                                "abstract" : metadata_json['abstract'] if metadata_json['abstract'] is not None else "",
                                                "authors" : metadata_json['authors'] if metadata_json['authors'] is not None else "",
                                                "org" : "",
                                                "url" : metadata_json['url'] if metadata_json['url'] is not None else "",
                                                "year" : metadata_json['year'] if metadata_json['year'] is not None else "",
                                                "lang" : lang_json['lang'] if lang_json['lang'] is not None else ""
                                            }
                                        }
                                    )
                                except:
                                    print(f"Exception on can't insert document for {pmid}")
                                if success_doc_insert == 0:
                                    print(f"Inserted on mongo a doc for {pmid}")
                                try:
                                    doc_id = metadata_json['pmid'] if metadata_json['pmid'] is not None else "000000",
                                    for i in range(len(metadata_json['authors'])):
                                        success_author_insert = post_json_request(
                                            'http://dbws:5000/mongo-doc-insert',
                                            {
                                                "db-name" : "adccali",
                                                "coll-name" : "author_vs_doc_id{}".format(actual_pattern),
                                                "document" : {
                                                    "author" : metadata_json['authors'][i] if metadata_json['authors'][i] is not None else "",
                                                    str(doc_id[0]) : 1,
                                                    "orcid" : orcid,
                                                }
                                            }
                                    )
                                except:
                                    success_author_insert = 1
            actual_pattern += 1
    return jsonify(patterns_list)
