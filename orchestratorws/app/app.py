from flask import Flask, jsonify, request
import requests
import urllib.parse

app = Flask(__name__)

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def get_json_orcid_request(name):
    url = 'https://pub.sandbox.orcid.org/v3.0/expanded-search'
    headers = {'Accept': 'application/json',}
    # params = (('q', f'{id_type}-self:{doc_id}'),)
    name = name.split()
    params = (('q', f'family-name:{name[0]}+AND+given-names:{name[1]}&start=0&rows=1'),)
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
    create_metadata_db = post_json_request(
        'http://dbws:5000/mongo-db-create',
        {"db-name" : "metadata"}
    )
    create_authors_db = post_json_request(
        'http://dbws:5000/mongo-db-create',
        {"db-name" : "authors"}
    )
    actual_pattern = 1
    if patterns_list is not None and create_metadata_db == 0 and create_authors_db == 0:
        for pattern in patterns_list:
            create_mongo_coll_metadata = post_json_request(
                'http://dbws:5000/mongo-coll-create',
                {
                    "db-name" : "metadata",
                    "coll-name" : f"metadata_{actual_pattern}"
                }
            )
            create_mongo_coll_author_vs_doc_id = post_json_request(
                'http://dbws:5000/mongo-coll-create',
                {
                    "db-name" : "authors",
                    "coll-name" : "author_vs_doc_id_{}".format(actual_pattern)
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
                                            "db-name" : "metadata",
                                            "coll-name" : f"metadata_{actual_pattern}",
                                            "document" : {
                                                "pat_id": pattern['id'] if pattern['id'] is not None else "",
                                                "pmid" : metadata_json['pmid'] if metadata_json['pmid'] is not None else "",
                                                "coreid" : "",
                                                "doi" : metadata_json['doi'] if metadata_json['doi'] is not None else "",
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
                                        try:
                                            orcid = get_json_orcid_request(str(metadata_json['authors'][i]))['expanded-result'][0]['orcid-id']
                                        except:
                                            orcid = ""
                                        success_author_insert = post_json_request(
                                            'http://dbws:5000/mongo-doc-insert',
                                            {
                                                "db-name" : "authors",
                                                "coll-name" : f"author_vs_doc_id_{actual_pattern}",
                                                "document" : {
                                                    "author" : metadata_json['authors'][i] if metadata_json['authors'][i] is not None else "",
                                                    "doc_id" : str(doc_id[0]),
                                                    "orcid" : orcid,
                                                }
                                            }
                                        )
                                except:
                                    success_author_insert = 1
            actual_pattern += 1
    return jsonify(patterns_list)

@app.route('/pipeline4', methods=['GET'])
def pipeline4():
    db_name = 'network'
    create_network_db = post_json_request(
        'http://dbws:5000/mongo-db-create',
        {"db-name" : db_name}
    )
    coll_list = post_json_request(
        'http://dbws:5000/mongo-coll-list',
        {"db-name" : "authors"}
    )
    for collection in coll_list['collections']:
        coll_name = f"works{collection.replace('author_vs_doc_id', '')}"
        create_mongo_coll_metadata = post_json_request(
            'http://dbws:5000/mongo-coll-create',
            {
                "db-name" : db_name,
                "coll-name" : coll_name,
            }
        )
        author_list = post_json_request(
            'http://dbws:5000/mongo-doc-distinct',
            {"db-name" : "authors", "coll-name" : collection, "field" : "author", "query" : {}, "options" : {}}
        )
        for author in author_list['result']:
            works_obj = post_json_request(
                'http://dbws:5000/mongo-doc-find',
                {"db-name" : "authors", "coll-name" : collection, "query" : {"author" : author}, "projection" : {"doc_id": 1}}
            )
            works = []
            for work in works_obj:
                works.append(str(work['doc_id']))
            try:
                success_works_insert = post_json_request(
                    'http://dbws:5000/mongo-doc-insert',
                    {
                        "db-name" : db_name,
                        "coll-name" : coll_name,
                        "document" : {
                            "author" : author,
                            "works" : works,
                        }
                    }
                )
            except:
                print("error on works insert")
            print(f"Author: {author}, works: {works}")
    return jsonify(author_list)
