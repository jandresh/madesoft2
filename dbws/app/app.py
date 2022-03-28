import csv
from flask import Flask, jsonify, request
import pymongo
import mysql.connector
import requests
import re

app = Flask(__name__)

config = {
    'user': 'adccali',
    'password': 'adccali',
    'host': 'mysql',
    'port': '3306',
    'database': 'adccali'
}

def post_json_request(url, obj):
    return requests.post(url, json=obj).json()


def execute_mysql_query(query, connection):

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        columns = cursor.description
        results = [{columns[index][0]:column for index,
                    column in enumerate(value)} for value in cursor.fetchall()]
    except Exception as e:
        print (str(e))
        results = [{"error" : str(e)}]
    cursor.close()

    return results


def execute_mysql_query2(query, connection):

    result = 0
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    except Exception as e:
        print (str(e))
        result = 1
    cursor.close()

    return result


def txt2text(path):
    with open(path, mode="r", encoding="utf-8") as f:
        text_str = f.read()
        f.close()
    return text_str


def str2eq(pattern, sentences_str):
    pattern = re.compile(pattern)
    match = ''
    sentences = []
    while match != None:
        match = pattern.search(sentences_str)
        if(match != None):
            sentences.append(sentences_str[:match.start()].split())
            sentences_str = sentences_str[match.end():]
    return sentences

@app.route('/')
def root():
    return '''dbws endpoints:
    /
    /init               GET
    /pattern2mysql      POST

    '''

# *****init()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/init

@app.route('/init', methods=['GET'])
def init():
    connection = mysql.connector.connect(**config)
    error = execute_mysql_query2(
            """CREATE TABLE patterns (
                    id INT(10) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                    pattern TEXT NOT NULL,
                    db TEXT NOT NULL,
                    description TEXT
                )""", connection)
    error += execute_mysql_query2(
                """CREATE TABLE searches (
                    patid INT(10) NOT NULL,
                    docid INT(10) NOT NULL,
                    title TEXT,
                    abs TEXT,
                    ftext MEDIUMTEXT,
                    PRIMARY KEY (patid,docid)
                )""", connection)
    if error:
        print('Error on tables creation')
    connection.close()
    return jsonify(error=error)

# *****patten_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "pattern": "Cancer de piel", "db": "PUBMED", "description": "Cancer muy comun"}' http://localhost:5001/pattern2mysql


@app.route("/pattern2mysql", methods=['POST'])
def pattern_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    pattern = request.json['pattern']
    db = request.json['db']
    description = request.json['description']
    query = 'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");' % (
        pattern, db, description)
    error = execute_mysql_query2(query, connection)
    result = [{"output": "Pattern can't be inserted"}]
    if not error:
        result = execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(result)

# *****search_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{ "patternid": "1", "docid": "CORE", "title": "Test title", "abstract": "Abstract: This is a test", "fulltext": "Tele, abstract, body"}' http://localhost:5001/search2mysql


@app.route("/search2mysql", methods=['POST'])
def search_insert():
    if not request.json:
        abort(400)
    connection = mysql.connector.connect(**config)
    patternid = request.json['patternid']
    docid = request.json['docid']
    title = request.json['title']
    abstract = request.json['abstract']
    fulltext = request.json['fulltext']
    file_name = '{}.csv'.format(patternid)


    try:
        with open(file_name, mode='a') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                patternid,
                docid,
                ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', title.capitalize()))),
                ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', abstract.capitalize()))),
                ' '.join(map(str,re.findall('[a-zA-Z]\w+[.,;:]*', fulltext.capitalize())))
                ])
            file.close()
        result = 0
    except:
        result = 1
    connection.close()
    return jsonify(result=result)

# *****txt_patterns_file_insert()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/txt2patterns

@app.route("/txt2patterns", methods=['GET'])
def txt_patterns_file_insert():
    connection = mysql.connector.connect(**config)
    patterns_text = txt2text('patterns.txt')
    search_queries = str2eq(r'\n', patterns_text)
    error_count = 0
    for query_words in search_queries:
        pattern = 'abstract:('
        for i in range(len(query_words)):
            if(i == len(query_words)-1):
                pattern += '%s)' % (query_words[i])
            else:
                pattern += '%s AND ' % (query_words[i])
        query = 'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");' % (
            pattern, 'CORE', 'Corpus 1')
        error_count += execute_mysql_query2(query, connection)
        pattern = ''
        for i in range(len(query_words)):
            if(i == len(query_words)-1):
                pattern += '%s[Title/Abstract]' % (query_words[i])
            else:
                pattern += '%s[Title/Abstract] AND ' % (query_words[i])
        query = 'INSERT INTO patterns (pattern, db, description) VALUES ("%s", "%s", "%s");' % (
            pattern, 'PUBMED', 'Corpus 1')
        error_count += execute_mysql_query2(query, connection)
    if not error_count:
        result = execute_mysql_query('SELECT * FROM patterns', connection)
    else:
        result = [{"error" : "%i Patterns can't be inserted" % (error_count)}]
    connection.close()
    return jsonify(result)

# *****patterns()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/patterns

@app.route('/patterns', methods=['GET'])
def patterns():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    connection.close()
    return jsonify(results)

# *****searches()******
# Este metodo es invocado de esta forma:
# curl http://<host>:5001/searches

@app.route('/searches', methods=['GET'])
def searches():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM searches', connection)
    connection.close()
    return jsonify(results)

# *****mysql-query()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"query" : "select * from searches"}' http://localhost:5001/mysql-query

@app.route('/mysql-query', methods=['POST'])
def mysql_query():
    if not request.json:
        abort(400)
    query = request.json['query']
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query(str(query), connection)
    connection.close()
    return jsonify(results)

# *****mongo_db_create()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali"}' http://localhost:5001/mongo-db-create

@app.route('/mongo-db-create', methods=['POST'])
def mongo_db_create():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        client[db_name]
    except:
        success = 1
    return str(success)

# *****mongo_db_list()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/mongo-db-list

@app.route('/mongo-db-list', methods=['GET'])
def mongo_db_list():
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    out =""
    # for db in client.list_databases():
    #     out+=str(db)
    return jsonify(databases=client.list_database_names())

# *****mongo_db_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali"}' http://localhost:5001/mongo-db-delete

@app.route('/mongo-db-delete', methods=['POST'])
def mongo_db_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        client.drop_database(db_name)
    except:
        success = 1
    return str(success)

# *****mongo_coll_create()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast"}' http://localhost:5001/mongo-coll-create

@app.route('/mongo-coll-create', methods=['POST'])
def mongo_coll_create():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
    except:
        success = 1
    return str(success)

# *****mongo_coll_list()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali"}' http://localhost:5001/mongo-coll-list

@app.route('/mongo-coll-list', methods=['POST'])
def mongo_coll_list():
    if not request.json:
        abort(400)
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    db_name = request.json['db-name']
    db = client[db_name]
    out =""
    # for coll in db.list_collection_names():
    #     out+=str(coll)
    return jsonify(collections=db.list_collection_names())

# *****mongo_coll_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast"}' http://localhost:5001/mongo-coll-delete

@app.route('/mongo-coll-delete', methods=['POST'])
def mongo_coll_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        collection.drop()
    except:
        success = 1
    return str(success)

# *****mongo_doc_insert()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast", "document" : {"doc-id" : "123456", "doc-name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-insert

@app.route('/mongo-doc-insert', methods=['POST'])
def mongo_doc_insert():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        document = request.json['document']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        insert_id = collection.insert_one(document)
        success = insert_id
    except:
        success = 1
    return str(success)


# *****mongo_doc_list()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast"}' http://localhost:5001/mongo-doc-list

@app.route('/mongo-doc-list', methods=['POST'])
def mongo_doc_list():
    if not request.json:
        abort(400)

    db_name = request.json['db-name']
    coll_name = request.json['coll-name']
    client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
    db = client[db_name]
    collection = db[coll_name]
    data = []
    for doc in collection.find():
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    return jsonify(data)

# *****mongo_doc_delete()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast", "query" : {"doc-name" : "Breast cancer history"}}' http://localhost:5001/mongo-doc-delete

@app.route('/mongo-doc-delete', methods=['POST'])
def mongo_doc_delete():
    if not request.json:
        abort(400)
    success = 0
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        query = request.json['query']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        collection.delete_one(query)
    except:
        success = 1
    return str(success)


# *****mongo_doc_find()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "Breast", "query" : {"doc-name" : "Breast cancer history"}, "projection" : {}}' http://localhost:5001/mongo-doc-find

@app.route('/mongo-doc-find', methods=['POST'])
def mongo_doc_find():
    if not request.json:
        abort(400)
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        query = request.json['query']
        projection = request.json['projection']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        out = collection.find(query, projection)
    except:
        out = None
    data = []
    for doc in out:
        doc['_id'] = str(doc['_id'])
        data.append(doc)
    return jsonify(data)

# *****mongo_doc_distinct()******
# Este metodo es invocado de esta forma:
# curl -X POST -H "Content-type: application/json" -d '{"db-name" : "adccali", "coll-name" : "author_vs_doc_id2", "field" : "author", "query" : {}, "options" : {}}' http://localhost:5001/mongo-doc-distinct | jq

@app.route('/mongo-doc-distinct', methods=['POST'])
def mongo_doc_distinct():
    if not request.json:
        abort(400)
    try:
        db_name = request.json['db-name']
        coll_name = request.json['coll-name']
        field = request.json['field']
        query = request.json['query']
        options = request.json['options']
        client = pymongo.MongoClient("mongodb://adccali:adccali@mongo:27017")
        db = client[db_name]
        collection = db[coll_name]
        out = collection.distinct(field, query, options)
    except:
        out = None
    return jsonify(result=out)

# *****pipeline1()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/pipeline1

@app.route('/pipeline1', methods=['GET'])
def pipeline1():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        get_metadata = True
        if (pattern['db'] == 'PUBMED'):
            try:
                pmids_json = post_json_request(
                    'http://metapubws:5000/pmids', {"query": pattern['pattern']})
            except:
                get_metadata = False
            if get_metadata:
                pmids = pmids_json['pmids']
                doc_id_counter = 0
                insert_counter = 0
                for doc_id in pmids:
                    print("id_pattern:%s" % pattern['id'])
                    print("pattern:%s" % pattern['pattern'])
                    print("doc_id:%s" % doc_id)
                    doc_id_counter += 1
                    print("doc_id_counter:%s" % doc_id_counter)
                    success = 0
                    if doc_id is not None:
                        insert_mysql = True
                        try:
                            metadata_json = post_json_request(
                                'http://metapubws:5000/metadata', {"id": doc_id})
                        except:
                            insert_mysql = False
                        print("title:%s" % metadata_json['title'])
                        print("abstract:%s" % metadata_json['abstract'])
                        if(metadata_json['abstract'] == None):
                            insert_abstract = ""
                        else:
                            insert_abstract = metadata_json['abstract']
                        if(metadata_json['title'] == None):
                            insert_title = ""
                        else:
                            insert_title = metadata_json['title']
                        if insert_mysql:
                            query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
                                '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '', insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '')
                            error = execute_mysql_query2(query, connection)
                            if not error:
                                success = 1
                            else:
                                success = 0
                    insert_counter += success
                    print("insert_counter:%s" % insert_counter)
        elif (pattern['db'] == 'CORE'):
            try:
                search_json = post_json_request(
                    'http://corews:5000/core', {"query": pattern['pattern']})
            except:
                get_metadata = False
                print('Not Success')
            if get_metadata and metadata_json != None :
                insert_counter = 0
                for metadata_json in search_json:
                    print('title : ', metadata_json['title'])
                    print('Abstract :', metadata_json['abstract'])
                    doc_id = metadata_json['id']
                    if(metadata_json['abstract'] == None):
                        insert_abstract = ""
                    else:
                        insert_abstract = metadata_json['abstract']
                    if(metadata_json['title'] == None):
                        insert_title = ""
                    else:
                        insert_title = metadata_json['title']
                    if(metadata_json['fullText'] == None):
                        insert_fulltext = ""
                    else:
                        insert_fulltext = metadata_json['fullText']
                    query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
                        '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), insert_fulltext.replace('"', '').replace('\n', ''), insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), insert_fulltext.replace('"', '').replace('\n', ''))
                    error = execute_mysql_query2(query, connection)
                    if not error:
                        success = 1
                    else:
                        success = 0
                    insert_counter += success
                print("insert_counter:%s" % insert_counter)

    results = execute_mysql_query(
        'SELECT id_pattern, id, title, abstract FROM searches', connection)
    connection.close()
    return jsonify(results)

# *****pipeline2()******
# Este metodo es invocado de esta forma:
# curl http://localhost:5001/pipeline2

@app.route('/pipeline2', methods=['GET'])
def pipeline2():
    connection = mysql.connector.connect(**config)
    results = execute_mysql_query('SELECT * FROM patterns', connection)
    for pattern in results:
        get_metadata = True
        if (pattern['db'] == 'PUBMED'):
            try:
                pmids_json = post_json_request(
                    'http://metapubws:5000/pmids', {"query": pattern['pattern']})
            except:
                get_metadata = False
            # if get_metadata:
            #     pmids = pmids_json['pmids']
            #     doc_id_counter = 0
            #     insert_counter = 0
            #     for doc_id in pmids:
            #         print("id_pattern:%s" % pattern['id'])
            #         print("pattern:%s" % pattern['pattern'])
            #         print("doc_id:%s" % doc_id)
            #         doc_id_counter += 1
            #         print("doc_id_counter:%s" % doc_id_counter)
            #         success = 0
            #         if doc_id is not None:
            #             insert_mysql = True
            #             try:
            #                 metadata_json = post_json_request(
            #                     'http://metapubws:5000/metadata', {"id": doc_id})
            #             except:
            #                 insert_mysql = False
            #             print("title:%s" % metadata_json['title'])
            #             print("abstract:%s" % metadata_json['abstract'])
            #             # time.sleep(0.3)
            #             if(metadata_json['abstract'] == None):
            #                 insert_abstract = ""
            #             else:
            #                 insert_abstract = metadata_json['abstract']
            #             if(metadata_json['title'] == None):
            #                 insert_title = ""
            #             else:
            #                 insert_title = metadata_json['title']
            #             if insert_mysql:
            #                 try:
            #                     query = 'INSERT INTO searches (patid, docid, title, abs, ftext) VALUES (%s,%s,"%s","%s","%s") ON DUPLICATE KEY UPDATE title="%s", abs="%s", ftext="%s";' % (pattern['id'], doc_id, insert_title.replace(
            #                         '"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '', insert_title.replace('"', '').replace('\n', ''), insert_abstract.replace('"', '').replace('\n', ''), '')
            #                     results = execute_mysql_query2(
            #                         query, connection)
            #                     success = 1
            #                 except:
            #                     query = "Mysql not executed"
            #                     success = 0
            #         insert_counter += success
            #         print("insert_counter:%s" % insert_counter)
        elif (pattern['db'] == 'CORE'):
            try:
                search_json = post_json_request(
                    'http://corews:5000/core2', {"query": pattern['pattern'], "idpattern": pattern['id']})
            except:
                get_metadata = False
                print('Not Success')
            if get_metadata:
                print("CORE insert success:%s" % pattern['pattern'])
                print('Spanish results: ', search_json['result'])
            else:
                print("CORE insert not success:%s" % pattern['pattern'])

    results = execute_mysql_query(
        'SELECT patid, docid, title FROM searches order by patid desc', connection)
    connection.close()
    return jsonify(results)
