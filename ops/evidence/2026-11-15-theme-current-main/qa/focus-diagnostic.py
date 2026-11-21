from pathlib import Path
exec(Path('/tmp/yuika-cycle35-qa/theme-probe.py').read_text().split('try:\n with sync_playwright()')[0])
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path=os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH']);c=b.new_context(viewport={'width':768,'height':1024})
  c.route('**/*',lambda r:r.continue_() if r.request.url.startswith(BASE) and r.request.method!='POST' else r.abort())
  p=c.new_page();p.goto(BASE+'kamakura-review.html');p.wait_for_load_state('networkidle')
  def measure():
   r=p.locator('#theme-kamakura').evaluate('e=>({active:document.activeElement===e,focusVisible:e.matches(":focus-visible"),color:getComputedStyle(e).outlineColor,bg:getComputedStyle(document.body).backgroundColor,offset:parseFloat(getComputedStyle(e).outlineOffset)})');r['contrast']=contrast(r['color'],r['bg']);return r
  p.locator('#theme-kamakura').click();p.locator('#theme-kamakura').focus();mouse=measure()
  p.locator('#theme-standard').focus();p.keyboard.press('Enter');p.keyboard.press('Tab');p.keyboard.press('Space');keyboard=measure()
  result={'mouse_then_programmatic_focus':mouse,'actual_keyboard_tab_space':keyboard,'interpretation':'Mouse modality does not activate focus-visible; keyboard modality activates existing rule; no product modification','diagram_measurements':[]}
  assert not mouse['focusVisible'] and keyboard['focusVisible'] and keyboard['active'] and keyboard['offset']>=3 and keyboard['contrast']>=3
  # Complete final numeric evidence that the partial probe did not serialize.
  svg=p.locator('svg[role="img"][aria-label^="鎌倉幕府のしくみの模式図"]')
  for theme in ['standard','kamakura']:
   p.locator('#theme-'+theme).click()
   for media in ['screen','print']:
    p.emulate_media(media=media)
    labels=svg.locator('text').evaluate_all("es=>es.filter(e=>['将軍','執権（北条氏）'].includes(e.textContent)).map(e=>({label:e.textContent,foreground:getComputedStyle(e).fill,background:getComputedStyle(e.previousElementSibling).fill,fontSize:getComputedStyle(e).fontSize}))")
    for label in labels:label['contrast']=contrast(label['foreground'],label['background']);assert label['contrast']>=4.5
    result['diagram_measurements'].append({'theme':theme,'media':media,'labels':labels})
   p.emulate_media(media='screen')
  result['verified_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/'focus-diagnostic-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));b.close()
finally:srv.shutdown();srv.server_close()
