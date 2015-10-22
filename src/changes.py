from couchdbkit import Server
from couchdbkit.changes import ChangesStream, foreach
from couchdbkit.exceptions import ResourceNotFound

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import Wildcard
from whoosh.analysis import *

from threading import Thread
from flask import Flask, json

import os, os.path

schema = Schema(title=TEXT(stored=True), artist=TEXT(stored=True), album=TEXT(stored=True), url=ID(stored=True), content=TEXT)
if not os.path.exists("indexdir"):
	os.mkdir("indexdir")

ix = create_in("indexdir", schema)

class IndexThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		s = Server()
		self.db = s['jukebox']
		try:
			self.since = self.db.get("whoosh-meta")["since"]
		except ResourceNotFound:
			self.since = 0

	def run(self):
		stream = ChangesStream(self.db, feed="continuous", heartbeat=True, since = 0)
		print "Getting changes"
		ana = StandardAnalyzer()
		for change in stream:
			if change["id"].startswith(u"http"):
				doc = self.db.get(change["id"])
				if doc["doc_type"] == "MusicFile":
					#print doc
					w = ix.writer()
					keys = {
						"album": doc['album'],
						"artist": doc['artist'],
						"title": doc['title'], 
						"url": doc['_id']
					}

					emptykeys = [x for x in keys.keys() if keys[x] == None]
					for k in emptykeys:
						del keys[k]

					total = " ".join([x for x in keys.values() if x != None])
					keys["content"] = total
					w.add_document(**keys)
					w.commit()
					print keys

app = Flask(__name__)

class AlwaysWildcard(Wildcard):
	def normalize(self):
		print "normalise", self
		return Wildcard(self.fieldname, "*" + self.text + "*")

@app.route("/")
def hello():
	with ix.searcher() as searcher:
		query = QueryParser("content", ix.schema, termclass = AlwaysWildcard).parse("FTW")
		results = searcher.search(query)
		return json.jsonify(results = [x.fields() for x in results])

if __name__ == "__main__":
	it = IndexThread()
	it.daemon = True
	it.start()
	app.run(debug = True)