function(doc) { 
     if (doc.doc_type == "WebPath" && !doc.checkec && !doc.failed) 
          emit(doc._id, doc); 
}