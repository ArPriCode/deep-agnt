def make_children(docs):
    children = []
    for doc in docs:
        pos = 0
        for sec_idx, section in enumerate(doc["sections"]):
            for text in section["sentences"]:
                children.append({
                    "text": text,
                    "doc": doc["id"],
                    "section": sec_idx,
                    "pos": pos,
                })
                pos += 1
    return children


def small_to_big(docs, query, k=4, window=None, max_tokens=None):
    children = make_children(docs)
    
    scored = []
    for idx, child in enumerate(children):
        score = similarity(query, child["text"])
        if score > 0:
            scored.append((-score, idx, child))
            
    scored.sort()
    kept = [item[2] for item in scored[:k]]
    
    doc_sentences = {}
    section_spans = {}
    for doc in docs:
        doc_id = doc["id"]
        sentences = []
        pos = 0
        for sec_idx, section in enumerate(doc["sections"]):
            start = pos
            sentences.extend(section["sentences"])
            pos += len(section["sentences"])
            section_spans[(doc_id, sec_idx)] = (start, pos - 1)
        doc_sentences[doc_id] = sentences
        
    passages = []
    total_tokens = 0
    
    for child in kept:
        doc_id = child["doc"]
        pos = child["pos"]
        
        if any(p["doc"] == doc_id and p["span"][0] <= pos <= p["span"][1] for p in passages):
            continue
            
        sentences = doc_sentences[doc_id]
        if window is None:
            first, last = section_spans[(doc_id, child["section"])]
        else:
            first = max(0, pos - window)
            last = min(len(sentences) - 1, pos + window)
            
        text = " ".join(sentences[first : last + 1])
        
        if max_tokens is not None:
            tokens = count_tokens(text)
            if total_tokens + tokens > max_tokens:
                continue
            total_tokens += tokens
            
        passages.append({
            "doc": doc_id,
            "span": (first, last),
            "text": text,
        })
        
    return passages
