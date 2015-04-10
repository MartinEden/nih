function(doc) { 
     if (doc.doc_type == "WebPath") 
          emit(doc._id, doc); 
}