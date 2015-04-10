function(doc) { 
     if (doc.doc_type == "WebPath" && doc.root == null) 
          emit(doc._id, doc); 
}