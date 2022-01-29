import csv
from flask import Flask, jsonify, request
import re
import requests
import time
from datetime import datetime
from langdetect import detect

app = Flask(__name__)
apikey = "JAnjvcE7LDiB0aHeh8ruR3gUGFVW6qSI"

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()

def query_api(search_url, query, scrollId=None):
    headers = {"Authorization": "Bearer "+apikey}
    if not scrollId:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scroll=true", headers=headers)
    else:
        response = requests.get(
            f"{search_url}?q={query}&limit=100&scrollId={scrollId}", headers=headers)
    return response.json(), response.elapsed.total_seconds()
def query_api(search_url, query, scrollId=None):
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
        query_api(search_url, query, scrollId)
    return response.json(), response.elapsed.total_seconds()

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
                scrollId = result["scrollId"]
                totalhits = result["totalHits"]
                result_size = len(result["results"])
            except:
                result=False
            if result:
                if result_size == 0:
                    break
                file_name = '{}.csv'.format(ptid)
                with open(file_name, mode='a') as file2:
                    writer2 = csv.writer(file2, delimiter=';', quotechar="'", quoting=csv.QUOTE_ALL)
                    for item in result["results"]:
                        if item['title']==None:
                            item['title']=''
                        if item['abstract']==None:
                            item['abstract']=''
                        if item['fullText']==None:
                            item['fullText']=''
                        try:
                            detect_es=detect(item['title'].lower())=='es' or detect(item['abstract'].lower())=='es' or detect(item['fullText'].lower())=='es'
                            if detect_es:
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
                        except:
                            print('No inserted docid: ', item['id'])
                            writer.writerow([
                                datetime.now(),
                                'No inserted docid: {}'.format(item['id'])
                                ])
                        print('PatternId:', ptid, 'SpanishCout:', spanish_count) 
                    count += result_size
                    if (spanish_count > 12000): 
                        break   
                    print(f"{count}/{totalhits} {elapsed}s")
                    writer.writerow([
                        datetime.now(),
                        'PatternId: {}, spanishCount: {}, {}/{}'.format(ptid, spanish_count, count, totalhits)
                        ])
                    file2.close()        
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