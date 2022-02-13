from flask import Flask, jsonify, request
import requests
import time

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


#
#         elif (pattern['db'] == 'CORE'):
#             try:
#                 search_json = post_json_request(
#                     'http://corews:5000/core2', {"query": pattern['pattern'], "idpattern": pattern['id']})
#             except:
#                 get_metadata = False
#                 print('Not Success')
#             if get_metadata:
#                 print("CORE insert success:%s" % pattern['pattern'])
#                 print('Spanish results: ', search_json['result'])
#             else:
#                 print("CORE insert not success:%s" % pattern['pattern'])

#     results = execute_mysql_query(
#         'SELECT patid, docid, title FROM searches order by patid desc', connection)
#     connection.close()
#     return jsonify(results)


# METAPUB OUT:

# {
#   "abstract": "This article proposes and evaluates two models for integrating self-reported health status measures for the elderly with dominant conceptualizations of physical health. Each model includes three dimensions of physical health: chronic illness, functional limitation, and self-rated health. In Model 1, the dimensions are linked in a causal framework, whereas in Model 2, a second-order factor, labeled physical health status, is hypothesized to account for the relationships among the three dimensions. Each model was tested with data gathered in Cleveland (N = 1,834) and Virginia (N = 2,146) using the Older Americans Resources and Services Multidimensional Functional Assessment Questionnaire (OARS MFAQ). Analyses were further replicated by randomly dividing each sample. Both models fit the data well; their utilities will depend on the way in which physical health is conceptualized and on the nature of the research question at hand.",
#   "authors": [
#     "Whitelaw NA",
#     "Liang J"
#   ],
#   "authors_str": "Whitelaw NA; Liang J",
#   "citation": "Whitelaw NA and Liang J. The structure of the OARS physical health measures. The structure of the OARS physical health measures. 1991; 29:332-47. doi: 10.1097/00005650-199104000-00003",
#   "doi": "10.1097/00005650-199104000-00003",
#   "history": {
#     "entrez": "Mon, 01 Apr 1991 00:00:00 GMT",
#     "medline": "Mon, 01 Apr 1991 00:00:00 GMT",
#     "pubmed": "Mon, 01 Apr 1991 00:00:00 GMT"
#   },
#   "pmid": "2020202",
#   "title": "The structure of the OARS physical health measures.",
#   "url": "https://ncbi.nlm.nih.gov/pubmed/2020202",
#   "year": "1991"
# }

# curl -X GET --header 'Accept: application/json' 'https://pub.sandbox.orcid.org/v3.0/expanded-search?q=pmid-self%3A27281629'
# curl -X GET --header 'Accept: application/json' 'https://pub.sandbox.orcid.org/v3.0/expanded-search?q=doi-self%3A10.1087%2F20120404'
