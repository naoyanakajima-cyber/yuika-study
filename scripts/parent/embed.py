"""Embed the storage boundary before any app code; keep standalone HTML."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
START,END='<!-- YUIKA_PARENT_BEGIN -->','<!-- YUIKA_PARENT_END -->'
block=START+'\n<script>\n'+Path(__file__).with_name('runtime.js').read_text()+'\n</script>\n'+END
for p in ROOT.glob('*.html'):
 text=p.read_text()
 if START in text:
  a=text.index(START);b=text.index(END,a)+len(END)
  if text[b:b+1]=='\n':b+=1
  text=text[:a]+text[b:]
 # Keep charset within the first 1024 bytes and CSP before executable code.
 # Place the boundary before the whole notification block so re-embedding
 # notifications cannot remove a parent runtime nested inside its markers.
 positions=[text.lower().index('</head>'), text.lower().index('<script')]
 if '<!-- YUIKA_REPORTS_BEGIN -->' in text:
  positions.append(text.index('<!-- YUIKA_REPORTS_BEGIN -->'))
 pos=min(positions)
 text=text[:pos]+block+'\n'+text[pos:]
 p.write_text(text)
