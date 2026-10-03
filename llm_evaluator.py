import json, os
from openai import OpenAI

def evaluate_with_llm(supplier_name, text, criteria):
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured.')
    criterion_text = '\n'.join(
        f"{c['criterion_id']}. {c['name']}: {c['description']} (0-{c['max_score']})"
        for c in criteria
    )
    prompt = f'''You are the Evaluation Agent in a procurement RFP evaluation workflow.\n\nSupplier: {supplier_name}\n\nACTIVE CRITERIA:\n{criterion_text}\n\nSUPPLIER PROPOSAL:\n{text}\n\nRules:\n- Use ONLY evidence present in the supplier proposal.\n- Return exactly one result for every active criterion.\n- Score within each criterion's 0 to max_score range.\n- Give concise justification and proposal-grounded evidence.\n- Do not invent certifications, prices, timelines, references, or capabilities.\n- Return JSON only with supplier_name, criteria, risks, overall_summary.\n'''
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'), temperature=0,
        response_format={'type': 'json_object'},
        messages=[
            {'role': 'system', 'content': 'You produce evidence-grounded procurement evaluation JSON.'},
            {'role': 'user', 'content': prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)
