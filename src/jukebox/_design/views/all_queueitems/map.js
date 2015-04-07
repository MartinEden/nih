function(doc) { 
     if (doc.doc_type == "QueueItems") 
          emit(doc._id, doc); 
}