function(doc) { 
	if (doc.doc_type == "WebPath") {
	    	emit(doc.root != null ? doc.root : doc._id, doc.root != null ? 1 : 0 ); 
	}
	if (doc.doc_type == "MusicFile") {
	    	emit(doc.root, 1);
	}
}