"""Offline validation/error demonstration for the classroom walkthrough."""
from validation import validate_and_normalize

criteria=[
 {'criterion_id':1,'name':'Technical Capability','max_score':10},
 {'criterion_id':2,'name':'Implementation Plan','max_score':10},
 {'criterion_id':3,'name':'Commercial Value','max_score':10},
 {'criterion_id':4,'name':'Security & Compliance','max_score':10},
 {'criterion_id':5,'name':'Support & Experience','max_score':10},
]
malformed={'criteria':[
 {'criterion_id':1,'score':15,'justification':'test','evidence':'test'},
 {'criterion_id':2,'score':'not-a-number'},
 'invalid criterion object',
 {'criterion_id':1,'score':8},
]}
normalized,warnings=validate_and_normalize(malformed,criteria,'Demo Supplier')
print('Normalized scores:', [x['score'] for x in normalized])
print('Warnings:')
for w in warnings: print('-',w)
