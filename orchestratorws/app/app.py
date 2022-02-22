from flask import Flask, jsonify, request
import requests

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
            if (pattern['db'] == 'PUBMED'):
                try:
                    pmids_json = post_json_request(
                        'http://metapubws:5000/pmids', {"query": pattern['pattern']})
                    pmids = pmids_json['pmids']
                except:
                    pmids = None
                if pmids is not None:
                    for pmid in pmids:
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
                            if metadata_json is not None:
                                try:
                                    success_doc_insert = post_json_request(
                                        'http://dbws:5000/mongo-doc-insert',
                                        {
                                            "db-name" : "adccali",
                                            "coll-name" : "metadata{}".format(actual_pattern),
                                            "document" : {
                                                "pmid" : metadata_json['pmid'] if metadata_json['pmid'] is not None else "",
                                                "coreid" : "",
                                                "doi" : metadata_json['doi'] if metadata_json['doi'] is not None else "",
                                                "orcid" : orcid,
                                                "title" : metadata_json['title'] if metadata_json['title'] is not None else "",
                                                "abstract" : metadata_json['abstract'] if metadata_json['abstract'] is not None else "",
                                                "authors" : metadata_json['authors'] if metadata_json['authors'] is not None else "",
                                                "org" : "",
                                                "url" : metadata_json['url'] if metadata_json['url'] is not None else "",
                                                "year" : metadata_json['year'] if metadata_json['year'] is not None else ""
                                            }
                                        }
                                    )
                                except:
                                    success_doc_insert = 1
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
                                                    str(doc_id) : 1,
                                                    "orcid" : orcid,
                                                }
                                            }
                                    )
                                except:
                                    success_author_insert = 1
            actual_pattern += 1
    return jsonify(patterns_list)
