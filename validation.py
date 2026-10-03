from typing import Any

def validate_and_normalize(raw: Any, criteria, supplier_name: str):
    warnings = []
    if not isinstance(raw, dict):
        raw = {}
        warnings.append('LLM response was not a JSON object; all criteria were defaulted.')

    raw_items = raw.get('criteria', [])
    if not isinstance(raw_items, list):
        warnings.append('LLM criteria field was not a list; all criteria were defaulted.')
        raw_items = []

    by_id = {}
    for item in raw_items:
        if not isinstance(item, dict):
            warnings.append('Ignored criterion result that was not a JSON object.')
            continue
        try:
            cid = int(item.get('criterion_id'))
        except (TypeError, ValueError):
            warnings.append('Ignored criterion result with invalid criterion_id.')
            continue
        if cid in by_id:
            warnings.append(f'Duplicate criterion {cid}; the last returned result was used.')
        by_id[cid] = item

    normalized = []
    for c in criteria:
        cid = int(c['criterion_id'])
        max_score = float(c['max_score'])
        item = by_id.get(cid)
        if item is None:
            warnings.append(f'Missing criterion {cid}; score defaulted to 0.')
            normalized.append({
                'criterion_id': cid, 'score': 0.0, 'max_score': max_score,
                'justification': 'No valid LLM result was returned.',
                'evidence': 'No evidence available.'
            })
            continue

        raw_score = item.get('score', 0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0
            warnings.append(f'Criterion {cid} had a malformed score; defaulted to 0.')
        clipped = max(0.0, min(score, max_score))
        if clipped != score:
            warnings.append(f'Criterion {cid} score {score} was clipped to 0-{max_score}.')

        justification = item.get('justification', 'No justification provided.')
        evidence = item.get('evidence', 'No evidence provided.')
        normalized.append({
            'criterion_id': cid,
            'score': clipped,
            'max_score': max_score,
            'justification': str(justification),
            'evidence': str(evidence),
        })
    return normalized, warnings
