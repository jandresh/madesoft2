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
    result_flag = 0
    while result_flag < 5:
        print(f"result_flag: {result_flag")
        time.sleep(10)
        try:
            headers = {"Authorization": "Bearer "+apikey}
            if not scrollId:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scroll=true", headers=headers)
            else:
                response = requests.get(
                    f"{search_url}?q={query}&limit=100&scrollId={scrollId}", headers=headers)
            print(f"response: {str(response)}, query: {query}, scrollId: {scrollId}")
        except:
            print("Control Point 1")
            print('Post request fail, trying again ...')
            time.sleep(3)
            response = None
        if response is not None:
            if(str(response)=="<Response [200]>"):
                print("Control Point 2")
                success = True
                try:
                    result = response.json()
                    elapsed = response.elapsed.total_seconds()
                except:
                    print("Control Point 3")
                    success = False
            else:
                time.sleep(50)
            if success:
                print("Control Point 4")
                return result, elapsed
        print("Control Point 6)
        result_flag +=1
    print("Control Point 7")
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
                print(f'scrollId : {result["scrollId"]}')
                if result is None:
                    print("Control Point 8")
                    break
            except:
                print("Control Point 9")
                result=None
            if result is not None:
                scrollId = result["scrollId"]
                totalhits = result["totalHits"]
                result_size = len(result["results"])
                if result_size == 0:
                    print("Control Point 10")
                    break
                file_name = f'{int((ptid + 1) / 2)}.csv'
                with open(file_name, mode='a') as file2:
                    writer2 = csv.writer(file2, delimiter=';', quotechar="'", quoting=csv.QUOTE_ALL)
                    for item in result["results"]:
                        if item['title']==None:
                            item['title']=''
                        try:
                            esp_detect_title = detect(item['title'].lower())=='es'
                        except:
                            esp_detect_title  = False
                        if item['abstract']==None:
                            item['abstract']=''
                        try:
                            esp_detect_abstract = detect(item['abstract'].lower())=='es'
                        except:
                            esp_detect_abstract  = False
                        if item['fullText']==None:
                            item['fullText']=''
                        try:
                            esp_detect_fullText = detect(item['fullText'].lower())=='es'
                        except:
                            esp_detect_fullText  = False
                        if esp_detect_title or esp_detect_abstract or esp_detect_fullText:
                            print("Control Point 11")
                            writer2.writerow([
                                int((ptid + 1) / 2),
                                item['id'],
                                item['downloadUrl'],
                                item['title'].replace("\'", ""),
                                item['abstract'].replace("\'", ""),
                                item['fullText'].replace("\'", "")
                            ])
                            spanish_count+=1
                        print('PatternId:', int((ptid + 1) / 2), 'SpanishCount:', spanish_count)
                    count += result_size
                    print(f"{count}/{totalhits} {elapsed}s")
                    writer.writerow([
                        datetime.now(),
                        'PatternId: {}, spanishCount: {}, {}/{}'.format(int((ptid + 1) / 2), spanish_count, count, totalhits)
                        ])
                    file2.close()
                    print("Control Point 12")
                    if (spanish_count > 12000 or count == totalhits):
                        print("Control Point 13")
                        break
            else:
                print("Control Point 14")
                file.close()
                break
            print("Control Point 15")
            file.close()
    print("Control Point 16")
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
