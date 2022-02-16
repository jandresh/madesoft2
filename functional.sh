#! /bin/bash
curl http://localhost:5001/init
curl -X POST -H "Content-type: application/json" -d '{ "pattern": "Cancer de piel", "db": "PUBMED", "description": "Cancer muy comun"}' http://localhost:5001/pattern2mysql
curl -X POST -H "Content-type: application/json" -d '{ "patternid": "1", "docid": "CORE", "title": "Test title", "abstract": "Abstract: This is a test", "fulltext": "Tele, abstract, body"}' http://localhost:5001/search2mysql
