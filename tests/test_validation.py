import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from validation import validate_and_normalize

CRITERIA=[{'criterion_id':1,'name':'Technical','max_score':10},{'criterion_id':2,'name':'Plan','max_score':10}]

def test_missing_and_out_of_range():
    raw={'criteria':[{'criterion_id':1,'score':15,'justification':'x','evidence':'y'}]}
    normalized,w=validate_and_normalize(raw,CRITERIA,'Demo')
    assert normalized[0]['score']==10 and normalized[1]['score']==0
    assert any('clipped' in x for x in w) and any('Missing criterion 2' in x for x in w)

def test_negative_and_malformed_score():
    raw={'criteria':[{'criterion_id':1,'score':-4},{'criterion_id':2,'score':'abc'}]}
    n,w=validate_and_normalize(raw,CRITERIA,'Demo')
    assert [x['score'] for x in n]==[0,0]
    assert len(w)==2

def test_malformed_items_and_duplicate_ids():
    raw={'criteria':['bad',{'criterion_id':1,'score':2},{'criterion_id':1,'score':8}]}
    n,w=validate_and_normalize(raw,CRITERIA,'Demo')
    assert n[0]['score']==8 and n[1]['score']==0
    assert any('not a JSON object' in x for x in w)
    assert any('Duplicate criterion 1' in x for x in w)

def test_non_object_response():
    n,w=validate_and_normalize(['bad'],CRITERIA,'Demo')
    assert all(x['score']==0 for x in n)
    assert any('not a JSON object' in x for x in w)
