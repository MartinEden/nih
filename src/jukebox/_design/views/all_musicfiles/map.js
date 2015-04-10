function(doc) { 
     if (doc.doc_type == "MusicFile") 
          emit(doc._id, doc); 
}