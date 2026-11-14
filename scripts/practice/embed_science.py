"""Embed the same weakness/retention algorithm with a science record adapter."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[2]
source=Path(__file__).with_name('adaptive.js').read_text()
weak=source[source.index('function weaknesses('):source.index("let adaptiveLevel=")]
retention=source[source.index('function retention('):source.index('function dueReviews(')]
adapter=Path(__file__).with_name('science.js').read_text()
interval=re.search(r'const REVIEW_INTERVAL_DAYS=Object.freeze\(\[[^]]+\]\);', source)[0]
adapter=re.sub(r'const REVIEW_INTERVAL_DAYS=Object.freeze\(\[[^]]+\]\);',interval,adapter)
body=adapter+'\n'+weak+retention
path=ROOT/'yuika-review-v2.html';text=path.read_text()
START,END='// SCIENCE_ADAPTIVE_START\n','// SCIENCE_ADAPTIVE_END\n'
if START in text:
 before,rest=text.split(START);_,after=rest.split(END)
else:
 before,after=text.split('// HISTORY_START\n');after='// HISTORY_START\n'+after
path.write_text(before+START+body+END+after)
