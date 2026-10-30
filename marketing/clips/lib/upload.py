# upload.py <chrome-win> <clip dir> [YYYY-MM-DD HH:MM] : uploads <dir>/<name>.mp4 to Clip Creator PC web (clipcreators.naver.com/web,
# window already open and logged in), fills 설명 (+ hashtags) from spec.json, picks cover 2, category spec.cat (default 교육 > 교육),
# links the blog post whose title starts with spec.postTitle, and either publishes now or (with a date) books 공개 예약.
# Uses the Naver editor helpers (guard.sh idle check, k.sh key input) from marketing/naver/editor.
import json, os, re, subprocess, sys, time
LIB = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(LIB, '../../naver/editor'))
import tblfix as tf
tf.W = W = sys.argv[1]
D = os.path.abspath(sys.argv[2]); S = json.load(open(D + '/spec.json'))
WHEN = sys.argv[3] if len(sys.argv) > 3 else None
def click(i): subprocess.run(['orca', 'computer', 'click', '--app', 'com.google.Chrome', '--window-id', W, '--element-index', str(i), '--no-screenshot'], capture_output=True); tf.done()
def need(ok, why):
    if not ok: print('FAIL', why); sys.exit(1)
def step():
    need(tf.guard(3 * 3600), 'owner busy for 3 h')
step(); need(tf.press(r'^팝업 버튼 업로드$'), 'upload menu'); time.sleep(1)
need(tf.press(r'^메뉴 항목 동영상 업로드$'), 'video upload item'); time.sleep(2.5)
step(); r = subprocess.run(['bash', LIB + '/pick.sh', W, f"{D}/{S['name']}.mp4"], capture_output=True, text=True); tf.done()
need('picked' in r.stdout, 'file pick ' + r.stdout + r.stderr); time.sleep(4)
need(tf.idx(tf.tree(), r'^텍스트 엔트리 영역 \(settable\) 설명'), 'upload form did not open')
step(); tf.press(r'^텍스트 엔트리 영역 \(settable\) 설명'); time.sleep(0.4)
subprocess.run('pbcopy', input=S['desc'] + '\n\n' + ' '.join('#' + h for h in S['hashtags']), text=True)
tf.k('hotkey', '--key', 'CmdOrCtrl+V'); time.sleep(1)
step(); tf.press(r'^버튼 커버 2$'); time.sleep(0.5)
c1, c2 = S.get('cat', ['교육', '교육'])
tf.press(r'^버튼 1차 카테고리$'); time.sleep(0.8); tf.press(rf'^버튼 {re.escape(c1)}$'); time.sleep(0.8)
tf.press(r'^버튼 2차 카테고리$'); time.sleep(0.8)
t = tf.tree(); ids = [l.split()[0] for l in t.splitlines() if re.match(rf'\s*\d+ 버튼 {re.escape(c2)}$', l)]
click(ids[-1]); time.sleep(0.8)
step(); tf.press(r'^버튼 블로그$'); time.sleep(2)
lines = tf.tree().splitlines()
k = [n for n, l in enumerate(lines) if S['postTitle'] in l]
need(k, 'blog post not in picker')
sel = next(l for l in lines[k[-1] + 1:k[-1] + 4] if re.search(r'버튼 선택$', l)).split()[0]
click(sel); time.sleep(1.5)
if WHEN:
    # 공개 예약: date picker (month arrows, day, its own 저장 button), then the hour and minute lists
    d, hm = WHEN.split(); y, mo, dd = (int(x) for x in d.split('-')); hh, mm = hm.split(':')
    step(); need(tf.press(r'^체크박스 \(settable\) 공개 예약'), 'reserve checkbox'); time.sleep(1)
    need(tf.press(r'^버튼 \d{4}\.\d\d\.\d\d$'), 'date button'); time.sleep(1)
    for _ in range(3):
        if f'텍스트, Value: {y}년 {mo}월' in tf.tree(): break
        tf.press(r'^버튼 다음월$'); time.sleep(0.7)
    need(tf.press(rf'^버튼 {y}년 {mo}월 {dd}일 '), 'day'); time.sleep(0.7)
    need(tf.press(r'^버튼 저장$'), 'date save'); time.sleep(0.8)
    for pop, box, val in (('시간', '목록 상자 시간', hh), ('분', '목록 상자 분', mm)):
        tf.press(rf'^팝업 버튼 {pop}'); time.sleep(0.8)
        lines = tf.tree().splitlines(); k = [n for n, l in enumerate(lines) if box in l]
        need(k, box)
        i = next(l for l in lines[k[0]:k[0] + 70] if re.search(rf'텍스트(?: \(selected\))?, Value: {val}$', l)).split()[0]
        click(i); time.sleep(0.8)
    t = tf.tree()
    need(f'버튼 {y}.{mo:02d}.{dd:02d}' in t and '현재 시간 이후로' not in t, 'reservation not set')
t = tf.tree()
ok = S['desc'][:20] in t and S['postTitle'] in t and re.search(r'전환 \(settable\) 전체 공개, Value: 1', t)
need(ok, 'form check')
step(); need(tf.press(r'^버튼 등록$'), 'register'); time.sleep(4)
if '등록 완료' in tf.tree(): tf.press(r'^버튼 확인$'); time.sleep(1.5)
tf.press(r'^버튼 닫기$'); time.sleep(1.5)
rows = re.findall(r'\d+ 행 (.*)', tf.tree())
want = f'공개 예정 {WHEN.split()[0].replace("-", ".")}' if WHEN else time.strftime('%Y.%m.%d')
print(('RESERVED ' if WHEN else 'POSTED ') + WHEN if WHEN and any(want in r for r in rows) else ('POSTED' if not WHEN and any(r.startswith(want) for r in rows) else 'CHECK the clip list: ' + ' | '.join(rows[:4])))
