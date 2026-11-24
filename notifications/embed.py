from pathlib import Path
root=Path(__file__).resolve().parent.parent
client=(root/'notifications/client.js').read_text()
start='<!-- YUIKA_REPORTS_BEGIN -->'
end='<!-- YUIKA_REPORTS_END -->'
for name in ['index.html','heian-review.html','onin-review.html','kamakura-review.html','yuika-review-v2.html','edo-review.html','mock-focus-review.html']:
 p=root/name;s=p.read_text();block=start+'\n<script>\n'+client+'\n</script>\n'+end
 if start in s:
  a=s.index(start);b=s.index(end,a)+len(end);s=s[:a]+block+s[b:]
 else:
  i=s.index('<!-- YUIKA_PARENT_END -->')+len('<!-- YUIKA_PARENT_END -->')
  s=s[:i]+'\n'+block+s[i:]
 if name!='index.html':s=s.replace("connect-src 'none'","connect-src https://*.workers.dev")
 p.write_text(s)
