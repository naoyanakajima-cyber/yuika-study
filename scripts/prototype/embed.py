"""Embed the isolated draft-storage boundary without external dependencies."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
START,END='// PROTOTYPE_START\n','// PROTOTYPE_END\n'
body=Path(__file__).with_name('runtime.js').read_text()
for name in ('onin-review.html','kamakura-review.html','heian-review.html','yuika-review-v2.html','mock-focus-review.html'):
 path=ROOT/name;text=path.read_text()
 if START in text:
  before,rest=text.split(START);_,after=rest.split(END)
 else:
  before,after=text.split('load();render();');after='load();render();'+after
 path.write_text(before+START+body+END+after)
