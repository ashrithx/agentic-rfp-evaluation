import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from ranking import calculate_results

CRITERIA=[
 {'criterion_id':1,'name':'Technical','weight':50,'max_score':10},
 {'criterion_id':2,'name':'Plan','weight':50,'max_score':10},
]

def supplier(name, scores, date, exp):
 return {'supplier_name':name,'submission_date':date,'experience_rating':exp,
         'criteria':{i+1:{'score':s,'evidence':'e','justification':'j'} for i,s in enumerate(scores)}}

def test_scores_benchmarks_gaps_relative_and_ppi():
    rows=[supplier('A',[8,6],'2026-09-20',5), supplier('B',[10,8],'2026-09-21',5)]
    result,bench=calculate_results(rows,CRITERIA)
    assert bench=={1:10,2:8}
    a=next(x for x in result if x['supplier_name']=='A')
    assert round(a['absolute_score'],6)==70
    assert round(a['ppi'],6)==77.5
    assert a['details'][0]['gap']==-2
    assert a['details'][0]['relative_performance_pct']==80

def test_tie_break_order_date_then_experience_then_name():
    rows=[
      supplier('Zulu',[10,10],'2026-09-20',8),
      supplier('Alpha',[10,10],'2026-09-19',1),
      supplier('Beta',[10,10],'2026-09-19',9),
      supplier('Gamma',[9,10],'2026-09-19',9),
    ]
    result,_=calculate_results(rows,CRITERIA)
    assert [x['supplier_name'] for x in result]==['Beta','Alpha','Zulu','Gamma']
    assert [x['final_rank'] for x in result]==[1,2,3,4]

def test_zero_benchmark_safe_handling():
    rows=[supplier('A',[0,0],'2026-09-20',5),supplier('B',[0,0],'2026-09-21',5)]
    result,bench=calculate_results(rows,CRITERIA)
    assert bench=={1:0,2:0}
    assert all(x['ppi']==0 for x in result)
    assert all(d['relative_performance_pct']==0 for x in result for d in x['details'])

def test_invalid_weights_rejected():
    bad=[dict(CRITERIA[0]),dict(CRITERIA[1],weight=40)]
    try: calculate_results([supplier('A',[5,5],'2026-09-20',5)],bad)
    except ValueError as e: assert '100%' in str(e)
    else: raise AssertionError('Expected invalid weight error')
