import sys
sys.path.insert(0, 'agents')
sys.path.insert(0, '.')
from agent import Agent

a = Agent(name='smoketest')

sample_text = (
    'Helix uses Erlang C calculations for workforce management staffing. '
    'The formula computes required agent counts based on call volume, '
    'average handle time, and target service level.'
)

count = a.index_memory('smoketest_doc', sample_text)
print(f'Indexed {count} chunk(s).')

result = a.retrieve_context('How does Helix calculate staffing requirements?')
print('--- Retrieved context ---')
print(result if result else '(EMPTY -- retrieval failed or found nothing)')
