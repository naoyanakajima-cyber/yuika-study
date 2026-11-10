"""Freeze question revisions and embed the archive into offline apps.
Use --record-editorial --reason TEXT only for same-meaning corrections.
Meaning/grading/structure changes require a new question ID.
"""
import argparse
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
APPS = ('onin-review.html', 'kamakura-review.html', 'heian-review.html', 'yuika-review-v2.html')
ARCHIVE = Path(__file__).with_name('revisions.json')
START, END = '// HISTORY_START\n', '// HISTORY_END\n'

def questions(text):
    return json.loads(re.search(r'const QUESTIONS=(\[.*?\n\]);', text, re.S)[1])

def editorial(old, new):
    flexible = {'prompt', 'explanation', 'hint', 'aliases', 'readings'}
    assert {k:v for k,v in old.items() if k not in flexible} == {k:v for k,v in new.items() if k not in flexible}, '意味・採点・構造の変更には新IDが必要です'
    for key in ('aliases', 'readings'):
        assert all(v in new.get(key, []) for v in old.get(key, [])), '既存の別表記・読みは削除できません'

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--record-editorial', action='store_true')
    p.add_argument('--reason', default='')
    args = p.parse_args()
    archive = json.loads(ARCHIVE.read_text()) if ARCHIVE.exists() else {}
    outputs = {}
    for name in APPS:
        text = (ROOT/name).read_text()
        records = archive.setdefault(name, {})
        for q in questions(text):
            versions = records.setdefault(q['id'], [])
            if not versions:
                versions.append({'revision':1, 'kind':'initial', 'reason':'PR #18 baseline', 'question':q})
            elif versions[-1]['question'] != q:
                assert args.record_editorial and args.reason.strip(), f'{name}/{q["id"]}: 版未登録。文章訂正・別表記追加は --record-editorial --reason、意味変更は新ID'
                editorial(versions[-1]['question'], q)
                versions.append({'revision':versions[-1]['revision']+1, 'kind':'editorial', 'reason':args.reason, 'question':q})
        body = 'const QUESTION_REVISIONS='+json.dumps(records, ensure_ascii=False, separators=(',', ':'))+';\n'+Path(__file__).with_name('runtime.js').read_text()
        if START in text:
            before, rest = text.split(START)
            _, after = rest.split(END)
        else:
            before, after = text.split('load();render();')
            after = 'load();render();'+after
        outputs[name] = before+START+body+END+after
    ARCHIVE.write_text(json.dumps(archive, ensure_ascii=False, indent=2)+'\n')
    for name, text in outputs.items():
        (ROOT/name).write_text(text)
