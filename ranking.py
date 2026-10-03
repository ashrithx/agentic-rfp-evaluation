def calculate_results(supplier_rows, criteria):
    if not criteria:
        raise ValueError('At least one active criterion is required.')
    total_weight = sum(float(c['weight']) for c in criteria)
    if abs(total_weight - 100.0) > 1e-9:
        raise ValueError(f'Active criterion weights must total 100%; current total is {total_weight:.2f}%.')

    by_supplier = []
    benchmark = {}
    for c in criteria:
        cid = int(c['criterion_id'])
        vals = []
        for s in supplier_rows:
            item = s['criteria'].get(cid)
            if item is not None and item.get('score') is not None:
                vals.append(float(item['score']))
        benchmark[cid] = max(vals) if vals else 0.0

    for s in supplier_rows:
        abs_score = 0.0
        weighted_relative = 0.0
        detail = []
        for c in criteria:
            cid = int(c['criterion_id'])
            item = s['criteria'][cid]
            score = float(item['score'])
            max_score = float(c['max_score'])
            weight = float(c['weight'])
            abs_score += (score / max_score) * weight if max_score else 0.0
            b = benchmark[cid]
            gap = score - b
            relative = (score / b) * 100.0 if b else 0.0
            weighted_relative += relative * (weight / 100.0)
            detail.append({
                'criterion_id': cid, 'criterion': c['name'], 'score': score,
                'max_score': max_score, 'weight': weight, 'benchmark': b,
                'gap': gap, 'relative_performance_pct': relative,
                'evidence': item['evidence'], 'justification': item['justification']
            })
        enriched = dict(s)
        enriched['absolute_score'] = abs_score
        enriched['ppi'] = weighted_relative
        enriched['details'] = detail
        by_supplier.append(enriched)

    by_supplier.sort(key=lambda x: (
        -x['ppi'], x['submission_date'], -float(x['experience_rating']), x['supplier_name'].casefold()
    ))
    for rank, s in enumerate(by_supplier, 1):
        s['final_rank'] = rank
    return by_supplier, benchmark
