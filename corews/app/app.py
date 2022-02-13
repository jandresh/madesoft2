import csv
from datetime import datetime
from flask import Flask, jsonify, request
from langdetect import detect
import re
import requests
import time

app = Flask(__name__)
apikey = "JAnjvcE7LDiB0aHeh8ruR3gUGFVW6qSI"

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def query_api(search_url, query, scrollId=None):
    time.sleep(10)
    result_flag = 0
    while result_flag < 3:
        try:
            headers = {"Authorization": "Bearer "+apikey}
            if not scrollId:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scroll=true", headers=headers)
            else:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scrollId={scrollId}", headers=headers)
        except:
            print('Post request fail, trying again ...')
            time.sleep(3)
            result_flag +=1
            response = None
        if response is not None:
            print(str(response))
            if(str(response)=="<Response [429]>"):
                time.sleep(300)
            try:
                result = response.json()
                elapsed = response.elapsed.total_seconds()
            except:
                return None, None
            return result, elapsed
    return None, None


def scroll(search_url, query, extract_info_callback):
    allresults = []
    count = 0
    scrollId = None
    while True:
        result, elapsed = query_api(search_url, query, scrollId)
        scrollId = result["scrollId"]
        totalhits = result["totalHits"]
        result_size = len(result["results"])
        if result_size == 0:
            break
        for hit in result["results"]:
            if extract_info_callback:
                allresults.append(extract_info_callback(hit))
            else:
                allresults.append(extract_info(hit))
        count += result_size
        print(f"{count}/{totalhits} {elapsed}s")
    return allresults

def scroll2(search_url, query, ptid):
    count = 0
    spanish_count = 0
    scrollId = None
    while True:
        with open('program_out.csv', mode='a') as file:
            writer = csv.writer(file, delimiter=';', quotechar="'", quoting=csv.QUOTE_ALL)
            result=True
            try:
                result, elapsed = query_api(search_url, query, scrollId)
                time.sleep(2)
            except:
                result=False
            if result:
                scrollId = result["scrollId"]
                totalhits = result["totalHits"]
                result_size = len(result["results"])
                if result_size == 0:
                    break
                file_name = '{}.csv'.format(ptid)
                with open(file_name, mode='a') as file2:
                    writer2 = csv.writer(file2, delimiter=';', quotechar="'", quoting=csv.QUOTE_ALL)
                    for item in result["results"]:
                        if item['title']==None:
                            item['title']=''
                        try:
                            esp_detect_title = detect(item['title'].lower())=='es'
                            # print(f"detect title = {str(detect(item['title'].lower()))}")
                        except:
                            esp_detect_title  = False
                        if item['abstract']==None:
                            item['abstract']=''
                        try:
                            esp_detect_abstract = detect(item['abstract'].lower())=='es'
                            # print(f"detect abstract = {str(detect(item['abstract'].lower()))}")
                        except:
                            esp_detect_abstract  = False
                        if item['fullText']==None:
                            item['fullText']=''
                        try:
                            esp_detect_fullText = detect(item['fullText'].lower())=='es'
                            # print(f"detect fullText = {str(detect(item['fullText'].lower()))}")
                        except:
                            esp_detect_fullText  = False
                        # try:
                        if esp_detect_title or esp_detect_abstract or esp_detect_fullText:
                            writer2.writerow([
                                ptid,
                                item['id'],
                                item['downloadUrl'],
                                item['title'].replace("\'", ""),
                                item['abstract'].replace("\'", ""),
                                item['fullText'].replace("\'", "")
                                # ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['title'].capitalize()))),
                                # ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['abstract'].capitalize()))),
                                # ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['fullText'].capitalize())))
                                ])
                            # insert=post_json_request(
                            #     'http://mysqlws:5000/search2mysql',
                            #     {
                            #     "patternid" : ptid,
                            #     "docid": item['id'],
                            #     "title" : item['title'],
                            #     "abstract" : item['abstract'],
                            #     "fulltext" : item['fullText']
                            #     })
                            # # if insert['result']=='0':
                            spanish_count+=1
                        # except:
                        #     print('No inserted docid: ', item['id'])
                        #     writer.writerow([
                        #         datetime.now(),
                        #         'No inserted docid: {}'.format(item['id'])
                        #         ])
                        print('PatternId:', ptid, 'SpanishCount:', spanish_count)
                    count += result_size
                    print(f"{count}/{totalhits} {elapsed}s")
                    writer.writerow([
                        datetime.now(),
                        'PatternId: {}, spanishCount: {}, {}/{}'.format(ptid, spanish_count, count, totalhits)
                        ])
                    file2.close()
                    if (spanish_count > 12000 or count == totalhits):
                        break
            file.close()
        # if result:
        #     if result_size == 0:
        #         break
        #     for item in result["results"]:
        #         if item['title']==None:
        #             item['title']=''
        #         if item['abstract']==None:
        #             item['abstract']=''
        #         if item['fullText']==None:
        #             item['fullText']=''
        #         try:
        #             detect_es=detect(item['title'].lower())=='es' or detect(item['abstract'].lower())=='es' or detect(item['fullText'].lower())=='es'
        #             if detect_es:
        #                 file_name = '{}.csv'.format(ptid)
        #                 with open(file_name, mode='a') as file:
        #                     writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_ALL)
        #                     writer.writerow([
        #                         ptid,
        #                         item['id'],
        #                         item['downloadUrl'],
        #                         ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['title'].capitalize()))),
        #                         ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['abstract'].capitalize()))),
        #                         ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', item['fullText'].capitalize())))
        #                         ])
        #                     file.close()
        #                 # insert=post_json_request(
        #                 #     'http://mysqlws:5000/search2mysql',
        #                 #     {
        #                 #     "patternid" : ptid,
        #                 #     "docid": item['id'],
        #                 #     "title" : item['title'],
        #                 #     "abstract" : item['abstract'],
        #                 #     "fulltext" : item['fullText']
        #                 #     })
        #                 # # if insert['result']=='0':
        #                 spanish_count+=1
        #         except:
        #             print('No inserted docid: ', item['id'])
        #         print('PatternId:', ptid, 'SpanishCout:', spanish_count)
        #     count += result_size
        #     print(f"{count}/{totalhits} {elapsed}s")
        #     with open('program_out.csv', mode='a') as file:
        #         writer = csv.writer(file, delimiter=',', quotechar="'", quoting=csv.QUOTE_ALL)
        #         writer.writerow([
        #             'PatternId: {}, spanishCount: {}, {}/{}'.format(ptid, spanish_count, count, totalhits)
        #             ])
        #         file.close()

    return spanish_count

#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama" }' http://localhost:5003/core | jq '.' | less
#

@app.route("/core", methods=['POST'])
def query_core():
    if not request.json:
        abort(400)
    result = None
    query = request.json['query']
    search, seconds = query_api(
        f"https://api.core.ac.uk/v3/search/works", query)
    for key, value in search.items():
        if(key == 'results'):
            result = value
            # # print(key, ":", value)
            # for item in list(value):
            #     print('title : ', item['title'])
            #     print('Abstract :', item['abstract'])
    return jsonify(result)

#
# *****query_core******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "query": "carcinoma lobulillar de mama", "idpattern": 1 }' http://localhost:5003/core | jq '.' | less
#


@app.route("/core2", methods=['POST'])
def query_core_scroll():
    if not request.json:
        abort(400)
    result = None
    query = request.json['query']
    ptid = request.json['idpattern']
    result = scroll2(
        f"https://api.core.ac.uk/v3/search/works",
        query,
        ptid)
    return jsonify(result=result)
# Eliminar volumenes en docker
# sudo docker volume rm mysqlws_my-db
# sudo docker volume ls

# Nuevo error:

# corews_1  | PatternId: 949 SpanishCount: 628
# corews_1  | PatternId: 949 SpanishCount: 629
# corews_1  | PatternId: 949 SpanishCount: 630
# corews_1  | PatternId: 949 SpanishCount: 631
# corews_1  | PatternId: 949 SpanishCount: 632
# corews_1  | PatternId: 949 SpanishCount: 633
# corews_1  | PatternId: 949 SpanishCount:[2022-02-12 04:39:35,386] ERROR in app: Exception on /core2 [POST]
# corews_1  | Traceback (most recent call last):
# corews_1  |   File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 2073, in wsgi_app
# corews_1  |     response = self.full_dispatch_request()
# corews_1  |   File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1518, in full_dispatch_request
# corews_1  |     rv = self.handle_user_exception(e)
# corews_1  |   File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1516, in full_dispatch_request
# corews_1  |     rv = self.dispatch_request()
# corews_1  |   File "/usr/local/lib/python3.7/site-packages/flask/app.py", line 1502, in dispatch_request
# corews_1  |     return self.ensure_sync(self.view_functions[rule.endpoint])(**req.view_args)
# corews_1  |   File "/app/app.py", line 240, in query_core_scroll
# corews_1  |     ptid)
# corews_1  |   File "/app/app.py", line 79, in scroll2
# corews_1  |     scrollId = result["scrollId"]
# corews_1  | KeyError: 'scrollId'
# corews_1  | 172.18.0.6 - - [12/Feb/2022 04:39:35] "POST /core2 HTTP/1.1" 500 -
# corews_1  |  634
# corews_1  | PatternId: 949 SpanishCount: 635
# corews_1  | PatternId: 949 SpanishCount: 636

# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = ca
# corews_1  | detect abstract = es
# corews_1  | detect fullText = ca
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 67
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 68
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 68
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 69
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 70
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 70
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 70
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 71
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 72
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 72
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 73
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 74
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 74
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 74
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 74
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 74
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 75
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 76
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 76
# corews_1  | detect title = es
# corews_1  | detect abstract = en
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 77
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 78
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 79
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 80
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 81
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 82
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 83
# corews_1  | detect title = it
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 84
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 84
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 85
# corews_1  | detect title = it
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 85
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 86
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 87
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 88
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 89
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 90
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 91
# corews_1  | detect title = it
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 91
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 91
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 92
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 93
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 94
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 94
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 95
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 95
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 96
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | PatternId: 1 SpanishCount: 97
# corews_1  | detect title = it
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 98
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 99
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 100
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 100
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 101
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 102
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 103
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 103
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 104
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 105
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 106
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 107
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 108
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 109
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 110
# corews_1  | detect title = ca
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 111
# corews_1  | detect title = ca
# corews_1  | detect abstract = ca
# corews_1  | detect fullText = ca
# corews_1  | PatternId: 1 SpanishCount: 111
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 112
# corews_1  | detect title = pt
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 113
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 114
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 115
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 116
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 116
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 117
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 117
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 118
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 118
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 119
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 119
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 120
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 120
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 120
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 120
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 121
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 121
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 122
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 122
# corews_1  | 200/2293 1.740071s
# corews_1  | <Response [200]>
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 122
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 123
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 123
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 123
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 123
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 124
# corews_1  | detect title = pt
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 125
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 126
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 126
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 126
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 127
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 128
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | PatternId: 1 SpanishCount: 128
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 129
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 130
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 130
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 130
# corews_1  | detect title = es
# corews_1  | detect abstract = en
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 131
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 131
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 132
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 132
# corews_1  | detect title = ca
# corews_1  | detect abstract = ca
# corews_1  | detect fullText = ca
# corews_1  | PatternId: 1 SpanishCount: 132
# corews_1  | detect title = ca
# corews_1  | detect abstract = ca
# corews_1  | detect fullText = ca
# corews_1  | PatternId: 1 SpanishCount: 132
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 133
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 133
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 133
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 134
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 135
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 136
# corews_1  | detect title = ca
# corews_1  | detect abstract = es
# corews_1  | detect fullText = ca
# corews_1  | PatternId: 1 SpanishCount: 137
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 138
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 138
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 139
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 140
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 141
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 141
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 141
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 141
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 141
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 142
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 142
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 143
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 144
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 145
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 146
# corews_1  | detect title = pt
# corews_1  | detect abstract = es
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 147
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 147
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 148
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 148
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 148
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | PatternId: 1 SpanishCount: 149
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 149
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 150
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 150
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 150
# corews_1  | detect title = es
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 150
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | PatternId: 1 SpanishCount: 150
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 151
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 152
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 152
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 153
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 153
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 153
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 154
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 154
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 154
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 154
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 154
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 155
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 155
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 155
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 155
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 155
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 156
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 157
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 158
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 159
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 159
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 159
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 159
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 159
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 160
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 160
# corews_1  | detect title = en
# corews_1  | detect abstract = en
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 160
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 161
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 162
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 163
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 163
# corews_1  | detect title = es
# corews_1  | detect abstract = ca
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | 300/2293 2.338881s
# corews_1  | <Response [200]>
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 164
# corews_1  | detect title = es
# corews_1  | detect abstract = en
# corews_1  | PatternId: 1 SpanishCount: 165
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 165
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 166
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 166
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 166
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 167
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 167
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 168
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 169
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 170
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 171
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 172
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 173
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 173
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 173
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 173
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 174
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 174
# corews_1  | detect title = es
# corews_1  | detect abstract = en
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 175
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 175
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 176
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 177
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 177
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 178
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 178
# corews_1  | detect title = en
# corews_1  | detect abstract = es
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 179
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 180
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 181
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 182
# corews_1  | detect title = es
# corews_1  | detect abstract = en
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 183
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 183
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 183
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 184
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 184
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 185
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 186
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 186
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 187
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 188
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 188
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 188
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 188
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 189
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 189
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 189
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 190
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 191
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 191
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 191
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 192
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 192
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 193
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 193
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 194
# corews_1  | detect title = pt
# corews_1  | detect abstract = en
# corews_1  | detect fullText = pt
# corews_1  | PatternId: 1 SpanishCount: 194
# corews_1  | detect title = en
# corews_1  | detect abstract = pt
# corews_1  | detect fullText = en
# corews_1  | PatternId: 1 SpanishCount: 194
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 195
# corews_1  | detect title = es
# corews_1  | detect abstract = es
# corews_1  | detect fullText = es
# corews_1  | PatternId: 1 SpanishCount: 196
# corews_1  | detect title = pt
# corews_1  | detect abstract = pt
