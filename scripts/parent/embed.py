"""Embed the storage boundary before any app code; keep standalone HTML."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
START,END='<!-- YUIKA_PARENT_BEGIN -->','<!-- YUIKA_PARENT_END -->'
block=START+'\n<script>\n'+Path(__file__).with_name('runtime.js').read_text()+'\n</script>\n'+END
# Preserve only the existing memory-only prototype reviewed at PR11 HEAD
# 3d2ed2f9a62673d2fb086a360ae841096f35b63e; validate before any HTML writes.
content=ROOT/'content-review.html'
assert hashlib.sha256(content.read_bytes()).hexdigest()=='4e4ef7c02f95d37f8ba0dce412045fc3a188d65debbb67fd6e87dfe7f307a12c'
for p in ROOT.glob('*.html'):
 if p.name=='content-review.html':continue
 text=p.read_text()
 if START in text:
  a=text.index(START);b=text.index(END,a)+len(END)
  if text[b:b+1]=='\n':b+=1
  text=text[:a]+text[b:]
 # Keep charset within the first 1024 bytes and CSP before executable code.
 pos=min(text.lower().index('</head>'), text.lower().index('<script'))
 text=text[:pos]+block+'\n'+text[pos:]
 p.write_text(text)
