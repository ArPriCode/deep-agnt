import math


def semantic_chunks(sentences, embed, percentile=90, min_size=2, max_size=8):
    if not sentences:
        return []
    if len(sentences) == 1:
        return [list(sentences)]

    vectors = [embed(s) for s in sentences]
    gaps = [distance(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)]

    sorted_gaps = sorted(gaps)
    rank = max(1, math.ceil(percentile * len(gaps) / 100))
    threshold = sorted_gaps[rank - 1]

    chunks = []
    start = 0
    for i, gap in enumerate(gaps):
        if gap > threshold:
            chunks.append(sentences[start : i + 1])
            start = i + 1
    chunks.append(sentences[start:])

    while len(chunks) > 1 and any(len(c) < min_size for c in chunks):
        idx = next(i for i, c in enumerate(chunks) if len(c) < min_size)
        if idx == 0:
            chunks[0] = chunks[0] + chunks[1]
            chunks.pop(1)
        elif idx == len(chunks) - 1:
            chunks[-2] = chunks[-2] + chunks[-1]
            chunks.pop()
        else:
            left_gap_idx = sum(len(c) for c in chunks[:idx]) - 1
            right_gap_idx = left_gap_idx + len(chunks[idx])
            if gaps[left_gap_idx] <= gaps[right_gap_idx]:
                chunks[idx - 1] = chunks[idx - 1] + chunks[idx]
                chunks.pop(idx)
            else:
                chunks[idx] = chunks[idx] + chunks[idx + 1]
                chunks.pop(idx + 1)

    result = []
    for chunk in chunks:
        for i in range(0, len(chunk), max_size):
            result.append(chunk[i : i + max_size])

    return result
