"""Embed the storage boundary before any app code; keep standalone HTML."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
START,END='<!-- YUIKA_PARENT_BEGIN -->','<!-- YUIKA_PARENT_END -->'
block=START+'\n<script>\n'+Path(__file__).with_name('runtime.js').read_text()+'\n</script>\n'+END
for p in ROOT.glob('*.html'):
 text=p.read_text()
 if START in text:
  a=text.index(START);b=text.index(END,a)+len(END)
  text=text[:a]+block+text[b:]
 else:
  pos=text.index('>',text.lower().index('<head'))+1
  text=text[:pos]+'\n'+block+text[pos:]
 p.write_text(text)
