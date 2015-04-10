function(doc) { 
     if (doc.doc_type == "SpideringPath") {
          emit(doc.url, {_id: doc.url});
     }
}