function(doc) { 
     if (doc.doc_type == "ChatItem") 
          emit(doc._id, doc); 
}