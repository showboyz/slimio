# axko.py : turn the English accessibility role names that Orca 1.4.274 prints (since 2026-11-25 afternoon:
# "text field", "button", "pop up button", "tab") back into the Korean names older builds printed ("텍스트 필드",
# "버튼", "팝업 버튼"...), which every script here matches. Only the role right after an element index is changed
# ("  7 text field (settable) 주소창" -> "  7 텍스트 필드 (settable) 주소창"); labels and values stay as they are.
# Roles that were already English before ("container", "link", "axlistmarker", "HTML 콘텐츠") are left alone.
# Used by bin/orca (stdin -> stdout); JSON output keeps its shape, only its strings are changed.
import json, re, sys

ROLES = {
    'text field': '텍스트 필드', 'search text field': '검색 텍스트 필드', 'text entry area': '텍스트 엔트리 영역',
    'text': '텍스트', 'button': '버튼', 'radio button': '라디오 버튼', 'check box': '체크박스', 'checkbox': '체크박스',
    'pop up button': '팝업 버튼', 'popup button': '팝업 버튼', 'menu button': '메뉴 버튼', 'combo box': '콤보 상자',
    'toggle button': '전환 버튼', 'switch': '전환', 'image': '이미지', 'cell': '셀', 'row': '행', 'column': '열',
    'table': '표', 'column header': '열 헤더', 'row header': '행 헤더', 'outline': '윤곽체', 'outline row': '윤곽체 행',
    'scroll area': '스크롤 영역', 'scroll bar': '스크롤 막대', 'slider': '슬라이더', 'toolbar': '도구 막대',
    'tab group': '탭 그룹', 'tab': '탭', 'close button': '닫기 버튼', 'minimize button': '최소화 버튼',
    'full screen button': '전체 화면 버튼', 'zoom button': '확대/축소 버튼', 'menu item': '메뉴 항목', 'menu': '메뉴',
    'menu bar': '메뉴 막대', 'menu bar item': '메뉴 막대 항목', 'list': '목록', 'list box': '목록 상자',
    'content list': '내용 목록', 'definition list': '정의 목록', 'splitter': '분할선', 'dialog': '대화상자',
    'sheet': '시트', 'standard window': '표준 윈도우', 'progress indicator': '진행 표시기',
    'increment arrow button': '화살표 증가 버튼', 'decrement arrow button': '화살표 감소 버튼',
    'increment page button': '페이지 증가 버튼', 'decrement page button': '페이지 감소 버튼',
    'disclosure triangle': '펼침 삼각형', 'heading': '제목',
}
_alt = '|'.join(re.escape(k) for k in sorted(ROLES, key=len, reverse=True))
_line = re.compile(r'(?m)^([ \t]*\d+ )(' + _alt + r')(?= |,|$)')
_focus = re.compile(r'(element is \d+ )(' + _alt + r')(?= |,|$)')


_web = re.compile(r'^([ \t]*)\d+ HTML 콘텐츠')


def ko(s):
    # Tabs inside a web page (ARIA tabs such as Umami's Path/Referrers) were "tab" in English before too, and only
    # Chrome's own tab strip said "탭": req_at.sh and k.sh count "탭 (" lines as Chrome tabs, so keep page tabs as "tab".
    out, web = [], None   # web = indentation of the HTML 콘텐츠 line we are inside, if any
    for ln in s.split('\n'):
        ind = len(ln) - len(ln.lstrip(' \t'))
        if web is not None and ln.strip() and ind <= web: web = None
        def sub(m):
            if web is not None and m.group(2) == 'tab': return m.group(0)
            return m.group(1) + ROLES[m.group(2)]
        ln = _line.sub(sub, ln)
        w = _web.match(ln)
        if w and web is None: web = len(w.group(1))
        out.append(ln)
    return _focus.sub(lambda m: m.group(1) + ROLES[m.group(2)], '\n'.join(out))


def walk(v):
    if isinstance(v, str): return ko(v)
    if isinstance(v, list): return [walk(x) for x in v]
    if isinstance(v, dict): return {k: walk(x) for k, x in v.items()}
    return v


if __name__ == '__main__':
    raw = sys.stdin.read()
    try:
        out = json.dumps(walk(json.loads(raw)), ensure_ascii=False, indent=2)   # orca prints indent 2
        sys.stdout.write(out + ('\n' if raw.endswith('\n') else ''))
    except ValueError:
        sys.stdout.write(ko(raw))
