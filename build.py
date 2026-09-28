#!/usr/bin/env python3
"""LIMEN RESEARCH 사이트 생성기.

content/ 의 설정·보고서·문서를 읽어 _site/ 에 정적 HTML을 만든다.
외부 패키지 없이 Python 3.11+ 표준 라이브러리만 쓴다.

    python3 build.py            # _site/ 생성
    LIMEN_LANGS=ko,en python3 build.py   # 설정과 무관하게 언어 지정 (미리보기용)
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import tomllib
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = ROOT / "_site"
KST = dt.timezone(dt.timedelta(hours=9))
TODAY = dt.datetime.now(KST).date()   # '문턱 일정'의 기준일: 빌드한 날 (한국 시간)

esc = html.escape

# ---------------------------------------------------------------------------
# 화면 문구 (언어별)
# ---------------------------------------------------------------------------
T = {
    "ko": {
        "html_lang": "ko",
        "descriptor": "주간 기술산업 보고서",
        "nav_reports": "보고서",
        "nav_samples": "무료 샘플",
        "nav_about": "소개",
        "switch_label": "EN",
        "latest": "이번 호",
        "recent": "지난 호",
        "view_all": "전체 목록 {n}편",
        "col_cover": "표지",
        "col_report": "보고서",
        "col_pages": "분량",
        "col_price": "가격",
        "col_sector": "분야",
        "col_count": "편수",
        "coverage_title": "분야별 발행 기록",
        "coverage_note": "최근 {n}개 호",
        "spec_title": "발행 안내",
        "spec_rows": {
            "cadence": ("발행", "매주 1편 · PDF · 한국어"),
            "length": ("분량", "편당 {a}–{b}쪽"),
            "price": ("가격", "편당 {krw}"),
            "price_usd": " · 해외 결제 {usd}",
            "pay": ("결제·발송", "국내: 카드·간편결제·계좌이체, 확인 후 영업일 24시간 이내 이메일 발송"),
            "pay_usd": ". 해외: 카드·PayPal, 결제 즉시 자동 발송",
            "account": ("회원가입", "없음. 결제할 때 적은 이메일로 PDF를 보냅니다"),
            "samples": ("무료 샘플", "{n}편 공개"),
            "b2b": ("기업·기관", "여러 부서 라이선스, 정기 구매, 별도 결제 방식"),
        },
        "samples_link": "샘플 보기",
        "b2b_cta": "구매 문의",
        "b2b_subject": "[LIMEN RESEARCH] 기업·기관 구매 문의",
        "thresholds": "문턱 일정",
        "thresholds_home": "다가오는 문턱",
        "thresholds_note": "보고서가 추적하는 표준·규제·예산·출시 일정",
        "as_of": "{d} 기준",
        "archive_title": "보고서 목록",
        "archive_sub": "지금까지 발행한 보고서 {n}편. 분야별로 걸러 볼 수 있습니다.",
        "filter_all": "전체",
        "empty": "아직 발행된 보고서가 없습니다.",
        "pages_unit": "{n}쪽",
        "lang_ko": "한국어",
        "lang_en": "영어",
        "buy": "구매하기",
        "buy_soon": "판매 준비 중",
        "sample": "무료 샘플 PDF",
        "details": "보고서 소개·목차",
        "f_date": "발행일",
        "f_length": "분량",
        "f_format": "형식",
        "f_sector": "분야",
        "overview": "개요",
        "key_findings": "핵심 내용",
        "toc": "목차",
        "quote_label": "핵심 문장",
        "numbers_title": "숫자로 보는 이 보고서",
        "features_title": "이 보고서의 특징",
        "figures_title": "그림 미리보기",
        "for_whom_title": "이런 분께 권합니다",
        "author_title": "지은이",
        "info_title": "보고서 정보",
        "i_title": "제목",
        "i_author": "지은이",
        "i_date": "등록일",
        "i_price": "가격",
        "purchase": "구매",
        "price_global": "해외 결제 US${usd}",
        "pay_kr": "국내 결제하기",
        "pay_kr_apply": "국내 구매 신청",
        "pay_global": "해외 카드·PayPal 결제",
        "order_subject": "[LIMEN RESEARCH] 구매 신청 - {report}",
        "order_body": ("보고서: {report}\n가격: {price}\n\n"
                       "이름(회사명):\nPDF를 받을 이메일:\n"
                       "결제 방법 (카드 결제 링크 / 계좌이체):\n입금자명 (계좌이체 시):\n"
                       "증빙 필요 여부 (현금영수증 등):\n"),
        "order_terms": [
            ("국내 결제", "카드·간편결제·계좌이체. 결제 확인 후 영업일 24시간 이내 이메일로 PDF 발송"),
            ("해외 결제", "해외 카드·PayPal(USD). 결제 즉시 이메일로 PDF 자동 발송"),
            ("회원가입", "필요 없음"),
            ("청약철회", "디지털 상품 특성상 발송 후에는 제한됩니다"),
        ],
        "refund_link": "환불정책",
        "b2b_title": "기업·기관 구매",
        "samples_title": "무료 샘플",
        "samples_sub": "보고서의 일부를 미리 읽어 보세요. 구매 전에 분석의 깊이와 형식을 확인할 수 있습니다.",
        "samples_empty": "공개된 샘플이 아직 없습니다.",
        "example": "예시",
        "terms": "이용약관",
        "refund": "환불정책",
        "privacy": "개인정보처리방침",
        "contact": "문의",
        "not_found_title": "페이지를 찾을 수 없습니다",
        "not_found_text": "주소가 바뀌었거나 삭제된 페이지입니다.",
        "home": "홈으로",
        "biz": {
            "name": "상호", "owner": "대표", "reg_no": "사업자등록번호",
            "mail_order_no": "통신판매업 신고번호", "address": "주소",
        },
    },
    "en": {
        "html_lang": "en",
        "descriptor": "Weekly technology industry reports",
        "nav_reports": "Reports",
        "nav_samples": "Free samples",
        "nav_about": "About",
        "switch_label": "한국어",
        "latest": "This issue",
        "recent": "Past issues",
        "view_all": "All {n} reports",
        "col_cover": "Cover",
        "col_report": "Report",
        "col_pages": "Length",
        "col_price": "Price",
        "col_sector": "Sector",
        "col_count": "Issues",
        "coverage_title": "Coverage by sector",
        "coverage_note": "Last {n} issues",
        "spec_title": "Publication details",
        "spec_rows": {
            "cadence": ("Frequency", "One report a week · PDF"),
            "length": ("Length", "{a}–{b} pages per report"),
            "price": ("Price", "{usd} per report"),
            "price_usd": "",
            "pay": ("Payment", "Card or PayPal. The PDF link is emailed right after payment"),
            "pay_usd": "",
            "account": ("Account", "None needed"),
            "samples": ("Free samples", "{n} available"),
            "b2b": ("Teams", "Multi-team licences, recurring purchases, other payment methods"),
        },
        "samples_link": "See samples",
        "b2b_cta": "Contact us",
        "b2b_subject": "[LIMEN RESEARCH] Team purchase inquiry",
        "thresholds": "Threshold dates",
        "thresholds_home": "Upcoming thresholds",
        "thresholds_note": "Standards, regulation, budget and launch dates our reports track",
        "as_of": "as of {d}",
        "archive_title": "Report archive",
        "archive_sub": "{n} reports published so far. Filter by sector.",
        "filter_all": "All",
        "empty": "No reports published yet.",
        "pages_unit": "{n} pp.",
        "lang_ko": "Korean",
        "lang_en": "English",
        "buy": "Buy now",
        "buy_soon": "Coming soon",
        "sample": "Free sample (PDF)",
        "details": "Overview and contents",
        "f_date": "Published",
        "f_length": "Length",
        "f_format": "Format",
        "f_sector": "Sector",
        "overview": "Overview",
        "key_findings": "Key findings",
        "toc": "Contents",
        "quote_label": "In one sentence",
        "numbers_title": "By the numbers",
        "features_title": "How this report works",
        "figures_title": "Figure previews",
        "for_whom_title": "Who it is for",
        "author_title": "Author",
        "info_title": "Report details",
        "i_title": "Title",
        "i_author": "Author",
        "i_date": "Published",
        "i_price": "Price",
        "teaser_title": "English edition in preparation",
        "teaser_lead": ("LIMEN RESEARCH publishes one in-depth report a week on the points where technology "
                        "crosses into industry: mobility, telecom, semiconductors, defense, finance and software. "
                        "Reports are currently published in Korean."),
        "teaser_contact": "For English-language inquiries, team licences, or to hear when the English edition launches, email",
        "teaser_list": "Current reports (Korean edition)",
        "teaser_open": "Korean edition",
        "purchase": "Purchase",
        "order_terms": [
            ("Checkout", "Card or PayPal, in US dollars"),
            ("Delivery", "PDF download link emailed right after payment"),
            ("Account", "Not needed"),
            ("Refunds", "Sales are final once the PDF is delivered"),
        ],
        "refund_link": "Refund policy",
        "b2b_title": "Team purchases",
        "samples_title": "Free samples",
        "samples_sub": "Read part of a report before you buy to see the depth and format of our analysis.",
        "samples_empty": "No samples published yet.",
        "example": "Example",
        "terms": "Terms",
        "refund": "Refunds",
        "privacy": "Privacy",
        "contact": "Contact",
        "not_found_title": "Page not found",
        "not_found_text": "The page may have moved or been removed.",
        "home": "Back to home",
        "biz": {
            "name": "Company", "owner": "Representative", "reg_no": "Business reg. no.",
            "mail_order_no": "Mail-order reg. no.", "address": "Address",
        },
    },
}

DOC_PAGES = ["about", "terms", "refund", "privacy", "thanks"]
HIDDEN_PAGES = {"thanks"}          # 주소로만 들어가는 페이지 (목록·검색 제외)


# ---------------------------------------------------------------------------
# 읽기
# ---------------------------------------------------------------------------
def load_toml(path):
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_site():
    site = load_toml(CONTENT / "site.toml")
    env = os.environ.get("LIMEN_LANGS")
    if env:
        site["languages"] = [x.strip() for x in env.split(",") if x.strip()]
    site["sector_map"] = {s["key"]: s for s in site.get("sectors", [])}
    site["base_path"] = urlparse(site["site_url"]).path.rstrip("/") + "/"
    return site


def load_reports(site):
    reports = []
    for path in sorted((CONTENT / "reports").glob("*.toml")):
        r = load_toml(path)
        if r.get("draft"):
            continue
        r["slug"] = path.stem
        for key in r.get("sectors", []):
            if key not in site["sector_map"]:
                raise SystemExit(f"{path.name}: 알 수 없는 분야 '{key}' (site.toml의 sectors 확인)")
        sample = r.get("sample", "")
        if sample and not sample.startswith("http") and not (CONTENT / "samples" / sample).exists():
            raise SystemExit(f"{path.name}: 샘플 파일 content/samples/{sample} 이 없습니다")
        cover_img = r.get("cover_image", "")
        if cover_img and not cover_img.startswith("http") and not (CONTENT / "covers" / cover_img).exists():
            raise SystemExit(f"{path.name}: 표지 이미지 content/covers/{cover_img} 이 없습니다")
        for lang in ("ko", "en"):
            for line in r.get(lang, {}).get("thresholds", []):
                parse_period(line.partition("|")[0], path.name)
            for fig in r.get(lang, {}).get("figures", []):
                if not (CONTENT / "figures" / fig["image"]).exists():
                    raise SystemExit(f"{path.name}: 그림 파일 content/figures/{fig['image']} 이 없습니다")
        reports.append(r)
    # 호수가 곧 발행 순서다. 가장 큰 호수가 '이번 호'.
    reports.sort(key=lambda r: (r.get("issue", 0), r["date"]), reverse=True)
    return reports


# ---------------------------------------------------------------------------
# 작은 마크다운 변환기 (문단, ##/### 제목, - 목록, 1. 목록, **굵게**, [링크](주소))
# ---------------------------------------------------------------------------
def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md(text):
    out = []
    for block in re.split(r"\n\s*\n", (text or "").strip()):
        lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
        if not lines:
            continue
        if lines[0].startswith("### "):
            out.append(f"<h3>{inline(lines[0][4:])}</h3>")
            lines = lines[1:]
        elif lines[0].startswith("## "):
            out.append(f"<h2>{inline(lines[0][3:])}</h2>")
            lines = lines[1:]
        if not lines:
            continue
        if all(l.startswith("- ") for l in lines):
            out.append("<ul>" + "".join(f"<li>{inline(l[2:])}</li>" for l in lines) + "</ul>")
        elif all(re.match(r"\d+\.\s", l) for l in lines):
            items = [inline(re.sub(r"^\d+\.\s", "", l)) for l in lines]
            out.append("<ol>" + "".join(f"<li>{x}</li>" for x in items) + "</ol>")
        else:
            out.append(f"<p>{inline(' '.join(lines))}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 표시 도우미
# ---------------------------------------------------------------------------
def fmt_date(d, lang):
    return d.strftime("%Y.%m.%d") if lang == "ko" else d.strftime("%b %d, %Y").replace(" 0", " ")


def issue_no(r):
    return f"No. {r.get('issue', 0):03d}"


def num(s):
    """숫자·호수·날짜·가격: 고정폭 숫자(tabular). Plex Sans KR은 기본 숫자가 고정폭이다."""
    return f'<span class="num">{s}</span>'


def sector_label(site, key, lang):
    return site["sector_map"][key][lang]


def sector_code(site, key):
    return site["sector_map"][key].get("code") or key[:3].upper()


def korea_on(ctx, r):
    """이 화면에서 국내 결제(원화)를 보여줄지. 한국어 화면 + [korea] 켜짐 + 원화 가격이 있을 때."""
    return (ctx.lang == "ko" and ctx.site.get("korea", {}).get("enabled", False)
            and bool(r.get("price_krw")))


def price_html(ctx, r, big=False, ref=True):
    usd = r.get("price_usd")
    if korea_on(ctx, r):
        main = f"₩{r['price_krw']:,}"
        ref_html = ""
        if ref and usd and r.get("pay_global"):
            ref_html = f'<span class="price-ref">{esc(ctx.t["price_global"].format(usd=format(usd, ",")))}</span>'
    elif usd:
        main, ref_html = f"US${usd:,}", ""
    else:
        return ""
    cls = "price price-big" if big else "price"
    return f'<span class="{cls}"><span class="price-main">{main}</span>{ref_html}</span>'


def mailto(site, subject, body=""):
    url = f"mailto:{site['email']}?subject={quote(subject)}"
    return url + (f"&body={quote(body)}" if body else "")


def file_size(r):
    """샘플 PDF 용량 표시 (예: 373 KB). 외부 링크면 빈 문자열."""
    s = r.get("sample", "")
    if not s or s.startswith("http"):
        return ""
    n = (CONTENT / "samples" / s).stat().st_size
    return f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{max(1, round(n / 1024))} KB"


PERIOD = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2}))?|-Q([1-4]))?$")


def parse_period(s, where=""):
    """'2027-06', '2027-06-30', '2027-Q2', '2027' → (시작일, 끝날, 표시 문자열)"""
    m = PERIOD.match(s.strip())
    if not m:
        raise SystemExit(f"{where}: 문턱 일정 날짜 '{s.strip()}' 형식 오류 (예: 2027-06, 2027-06-30, 2027-Q2)")
    y, mo, d, q = m.groups()
    y = int(y)

    def month_end(yy, mm):
        return dt.date(yy + mm // 12, mm % 12 + 1, 1) - dt.timedelta(days=1)

    if q:
        q = int(q)
        return dt.date(y, 3 * q - 2, 1), month_end(y, 3 * q), f"{y} Q{q}"
    if d:
        day = dt.date(y, int(mo), int(d))
        return day, day, f"{y}.{mo}.{d}"
    if mo:
        return dt.date(y, int(mo), 1), month_end(y, int(mo)), f"{y}.{mo}"
    return dt.date(y, 1, 1), dt.date(y, 12, 31), str(y)


def thresholds_of(ctx, r):
    items = []
    for line in r.get(ctx.lang, {}).get("thresholds", []):
        when, _, what = line.partition("|")
        start, end, label = parse_period(when)
        items.append({"start": start, "end": end, "label": label, "text": what.strip(), "r": r})
    return sorted(items, key=lambda x: (x["start"], x["end"]))


class Ctx:
    """페이지 하나를 그릴 때 필요한 정보. 모든 링크는 상대 경로로 만든다."""

    def __init__(self, site, lang, path):
        self.site, self.lang, self.path = site, lang, path   # path: 언어 폴더 안 경로, 예 "reports/abc/"
        self.t = T[lang]
        self.prefix = "" if lang == site["languages"][0] else f"{lang}/"
        depth = len([p for p in (self.prefix + path).split("/") if p])
        self.root = "../" * depth or "./"

    def url(self, target="", lang=None):
        """사이트 안 링크. target은 언어 폴더 기준 경로."""
        lang = lang or self.lang
        if lang not in self.site["languages"]:
            lang = self.site["languages"][0]
        prefix = "" if lang == self.site["languages"][0] else f"{lang}/"
        return self.root + prefix + target

    def asset(self, name):
        return self.root + "assets/" + name

    def sample_url(self, r):
        s = r.get("sample", "")
        return s if s.startswith("http") else self.root + "samples/" + s


# ---------------------------------------------------------------------------
# 공통 조각
# ---------------------------------------------------------------------------
def report_url(ctx, r):
    return ctx.url(f"reports/{r['slug']}/")


def sectors_text(ctx, r, sep=" · "):
    return sep.join(sector_label(ctx.site, k, ctx.lang) for k in r.get("sectors", []))


def example_mark(ctx, r):
    return f'<span class="example">[{ctx.t["example"]}]</span>' if r.get("example") else ""


def docline(ctx, r, lead="", pages=False):
    """'이번 호  No. 004  2026.10.05  종합  72쪽' — 문서 머리 한 줄. 구분 기호 대신 간격."""
    parts = []
    if lead:
        parts.append(f'<span class="now">{esc(lead)}</span>')
    parts.append(f'<span class="num id">{issue_no(r)}</span>')
    parts.append(num(fmt_date(r["date"], ctx.lang)))
    parts.append(f"<span>{esc(sectors_text(ctx, r))}</span>")
    if pages and r.get("pages"):
        parts.append(f"<span>{esc(ctx.t['pages_unit'].format(n=r['pages']))}</span>")
    return f'<p class="docline">{"".join(parts)}{example_mark(ctx, r)}</p>'


def cover(ctx, r, cls=""):
    """보고서 앞표지 (A4 비율). 실제 PDF 첫 장 이미지가 있으면(cover_image) 그걸 쓴다.
    이미지 없이 그릴 때: 머리띠 · 제목 · 문턱선 위에 선 호수 · 7칸 분야 색인 · 발행일/쪽수."""
    lo = r.get(ctx.lang) or r.get(ctx.site["languages"][0], {})
    img = r.get("cover_image", "")
    if img:
        src = img if img.startswith("http") else ctx.root + "covers/" + img
        return f'<div class="cover {cls}"><img src="{esc(src)}" alt="" loading="lazy"></div>'
    title = lo.get("cover_title") or lo.get("title", "")
    on = set(r.get("sectors", []))
    cells = "".join(f'<span class="{"on" if k in on else ""}">{esc(sector_code(ctx.site, k))}</span>'
                    for k in ctx.site["sector_map"])
    pages = ctx.t["pages_unit"].format(n=r["pages"]) if r.get("pages") else ""
    return f"""<div class="cover {cls}" aria-hidden="true">
  <div class="cv-head"><span>LIMEN RESEARCH</span><span class="num">{issue_no(r)}</span></div>
  <div class="cv-title">{esc(title)}</div>
  <div class="cv-no">{r.get('issue', 0):03d}</div>
  <div class="cv-sill"></div>
  <div class="cv-cells">{cells}</div>
  <div class="cv-foot"><span>{fmt_date(r["date"], ctx.lang)}</span><span>{esc(pages)}</span></div>
</div>"""


def korea_order(ctx, r):
    """국내 결제 버튼이 갈 곳: 결제 링크 > 구매 신청서 > 이메일 신청 순서로 쓴다."""
    if r.get("pay_korea"):
        return r["pay_korea"], ctx.t["pay_kr"]
    report = f"{issue_no(r)} {r['ko']['title']}"
    form = ctx.site.get("korea", {}).get("order_form_url", "")
    if form:
        return form.replace("{report}", quote(report)), ctx.t["pay_kr_apply"]
    subject = ctx.t["order_subject"].format(report=report)
    body = ctx.t["order_body"].format(report=report, price=f"₩{r['price_krw']:,}")
    return mailto(ctx.site, subject, body), ctx.t["pay_kr_apply"]


def buy_buttons(ctx, r, block=False, primary_only=False):
    """구매 버튼. 한국어: 국내 결제(주) + 해외 결제(보조). 그 밖의 언어: 해외 결제만."""
    b = " btn-block" if block else ""
    out = []
    if korea_on(ctx, r):
        href, label = korea_order(ctx, r)
        new_tab = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a class="btn{b}" href="{esc(href)}"{new_tab}>{label}</a>')
        if r.get("pay_global") and not primary_only:
            out.append(f'<a class="btn btn-line{b} lemonsqueezy-button" href="{esc(r["pay_global"])}">'
                       f'{ctx.t["pay_global"]}</a>')
    elif r.get("pay_global"):
        out.append(f'<a class="btn{b} lemonsqueezy-button" href="{esc(r["pay_global"])}">{ctx.t["buy"]}</a>')
    else:
        out.append(f'<span class="btn{b} is-disabled" aria-disabled="true">{ctx.t["buy_soon"]}</span>')
    return "".join(out)


def sample_button(ctx, r, block=False):
    if not r.get("sample"):
        return ""
    size = file_size(r)
    size_html = f' <span class="num size">{size}</span>' if size else ""
    b = " btn-block" if block else ""
    return f'<a class="btn btn-line{b}" href="{esc(ctx.sample_url(r))}">{ctx.t["sample"]}{size_html}</a>'


def nav_links(ctx, alt_path):
    site, lang = ctx.site, ctx.lang
    if lang not in site["languages"]:              # 영문 안내 페이지: 메뉴는 한국어 사이트로 가는 링크 하나
        return f'<a class="lang" href="{ctx.url()}" hreflang="ko">{T[lang]["switch_label"]}</a>'
    nav = [("reports/", ctx.t["nav_reports"]), ("samples/", ctx.t["nav_samples"]), ("about/", ctx.t["nav_about"])]
    current = ' aria-current="page"'
    links = "".join(f'<a href="{ctx.url(p)}"{current if ctx.path.startswith(p) else ""}>{esc(label)}</a>'
                    for p, label in nav)
    if len(site["languages"]) > 1 and alt_path is not None:
        other = [l for l in site["languages"] if l != lang][0]
        links += f'<a class="lang" href="{ctx.url(alt_path, other)}" hreflang="{other}">{T[lang]["switch_label"]}</a>'
    elif "en" not in site["languages"]:            # 영어 사이트 준비 중: 영문 안내 페이지로
        links += f'<a class="lang" href="{ctx.root}en/" hreflang="en">EN</a>'
    return links


def header(ctx, alt_path):
    """모든 페이지 같은 한 줄 머리. 큰 제호 없음."""
    return f"""<header class="site-head">
  <div class="wrap head-inner">
    <a class="brand" href="{ctx.url()}"><span class="brand-name">LIMEN RESEARCH</span><span class="brand-desc">{esc(ctx.t['descriptor'])}</span></a>
    <nav class="nav">{nav_links(ctx, alt_path)}</nav>
  </div>
</header>"""


def footer(ctx):
    site, tt = ctx.site, ctx.t
    biz = site.get("business", {})
    rows = "".join(f"<p>{esc(tt['biz'][k])} {esc(str(v))}</p>" for k, v in biz.items() if v and k in tt["biz"])
    year = TODAY.year
    return f"""<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <a class="brand" href="{ctx.url()}"><span class="brand-name">LIMEN RESEARCH</span></a>
      <p>{esc(site[ctx.lang]["tagline"])}</p>
    </div>
    <nav class="foot-nav">
      <a href="{ctx.url('about/')}">{tt['nav_about']}</a>
      <a href="{ctx.url('terms/')}">{tt['terms']}</a>
      <a href="{ctx.url('refund/')}">{tt['refund']}</a>
      <a href="{ctx.url('privacy/')}">{tt['privacy']}</a>
    </nav>
    <div class="foot-contact">
      <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a>
      {rows}
      <p class="num">© {year} LIMEN RESEARCH</p>
    </div>
  </div>
</footer>"""


FONTS = "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap"


def page(ctx, title, body, description="", alt_path=None, checkout=False, noindex=False):
    """완성된 HTML 문서. alt_path: 다른 언어의 같은 페이지 경로 (없으면 None)."""
    site = ctx.site
    full_title = f"{title} | LIMEN RESEARCH" if title else f"LIMEN RESEARCH | {site[ctx.lang]['tagline']}"
    desc = description or site[ctx.lang]["description"]
    canonical = site["site_url"].rstrip("/") + "/" + ctx.prefix + ctx.path
    alts = ""
    if len(site["languages"]) > 1 and alt_path is not None:
        for l in site["languages"]:
            p = alt_path if l != ctx.lang else ctx.path
            pre = "" if l == site["languages"][0] else f"{l}/"
            alts += f'\n<link rel="alternate" hreflang="{l}" href="{esc(site["site_url"].rstrip("/") + "/" + pre + p)}">'
    lemon = '\n<script src="https://app.lemonsqueezy.com/js/lemon.js" defer></script>' if checkout else ""
    robots = '\n<meta name="robots" content="noindex">' if noindex else ""
    return f"""<!doctype html>
<html lang="{ctx.t['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">{alts}{robots}
<meta property="og:type" content="website">
<meta property="og:site_name" content="LIMEN RESEARCH">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101316" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{ctx.asset('favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{ctx.asset('site.css')}">
<script src="{ctx.asset('site.js')}" defer></script>{lemon}
</head>
<body>
{header(ctx, alt_path)}
<main>
{body}
</main>
{footer(ctx)}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 페이지들
# ---------------------------------------------------------------------------
def entry(ctx, r):
    """목록 한 줄: 표지 | 문서 머리 · 제목 · 요약 | 분량 | 가격"""
    lo = r[ctx.lang]
    pages = ctx.t["pages_unit"].format(n=r["pages"]) if r.get("pages") else ""
    return f"""<li class="entry" data-sectors="{' '.join(r.get('sectors', []))}">
  <a class="entry-cover" href="{report_url(ctx, r)}" tabindex="-1" aria-hidden="true">{cover(ctx, r, 'cover-xs')}</a>
  <div class="entry-main">
    {docline(ctx, r)}
    <h3><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h3>
    <p class="entry-sum">{esc(lo.get('summary', ''))}</p>
  </div>
  <p class="entry-pages num">{esc(pages)}</p>
  <p class="entry-price">{price_html(ctx, r, ref=False)}</p>
</li>"""


def entries_head(ctx):
    t = ctx.t
    return (f'<div class="entries-head" aria-hidden="true"><span>{t["col_cover"]}</span><span>{t["col_report"]}</span>'
            f'<span>{t["col_pages"]}</span><span>{t["col_price"]}</span></div>')


def threshold_list(ctx, items, home=False):
    """문턱 일정 표. 기준일(빌드한 날) 자리에 '지금' 선을 끼워 지난 일정과 다가올 일정을 가른다."""
    now = f'<li class="th-now"><span class="num">{ctx.t["as_of"].format(d=fmt_date(TODAY, ctx.lang))}</span></li>'
    rows, placed = [], False
    for it in items:
        if not placed and it["end"] >= TODAY:
            rows.append(now)
            placed = True
        past = " is-past" if it["end"] < TODAY else ""
        extra = ""
        if home:
            r = it["r"]
            first = r["sectors"][0] if r.get("sectors") else ""
            extra = (f'<span class="th-sector">{esc(sector_label(ctx.site, first, ctx.lang)) if first else ""}</span>')
            ref = f'<a class="th-ref num" href="{report_url(ctx, r)}">{issue_no(r)}</a>'
        else:
            ref = ""
        rows.append(f'<li class="th{past}"><span class="th-date num">{esc(it["label"])}</span>{extra}'
                    f'<span class="th-text">{inline(it["text"])}</span>{ref}</li>')
    if not placed:
        rows.append(now)
    cls = "thresholds thresholds-home" if home else "thresholds"
    return f'<ol class="{cls}">{"".join(rows)}</ol>'


def coverage_matrix(ctx, reports, limit=8):
    """분야 × 최근 호 표. 채운 칸 = 그 호가 다룬 분야."""
    cols = sorted(reports, key=lambda r: (r.get("issue", 0), r["date"]))[-limit:]
    head = "".join(f'<th scope="col"><a class="num" href="{report_url(ctx, r)}" '
                   f'title="{esc(issue_no(r) + " " + r[ctx.lang]["title"])}">{r.get("issue", 0):03d}</a></th>'
                   for r in cols)
    rows = []
    for k, sec in ctx.site["sector_map"].items():
        n = sum(k in r.get("sectors", []) for r in reports)
        if not n:                       # 아직 다룬 적 없는 분야는 빈 줄로 보여 주지 않는다
            continue
        cells = "".join('<td><span class="on" role="img" aria-label="' + esc(issue_no(r)) + '"></span></td>'
                        if k in r.get("sectors", []) else '<td><span class="off"></span></td>' for r in cols)
        rows.append(f'<tr><th scope="row"><a href="{ctx.url("reports/")}?sector={k}">{esc(sec[ctx.lang])}</a></th>'
                    f'{cells}<td class="count num">{n}</td></tr>')
    return (f'<table class="matrix"><thead><tr><th scope="col">{ctx.t["col_sector"]}</th>{head}'
            f'<th scope="col" class="count">{ctx.t["col_count"]}</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


def pub_spec(ctx, reports):
    """발행 안내 표 (예전의 '구매 안내'·'기업·기관 구매' 단을 대신한다). 숫자는 데이터에서 계산."""
    t, rows = ctx.t, []
    S = t["spec_rows"]
    rows.append(S["cadence"])
    pages = [r["pages"] for r in reports if r.get("pages")]
    if pages:
        rows.append((S["length"][0], S["length"][1].format(a=min(pages), b=max(pages))))
    latest = reports[0] if reports else {}
    krw, usd = latest.get("price_krw"), latest.get("price_usd")
    global_ok = any(r.get("pay_global") for r in reports)      # 해외 결제 링크가 실제로 있을 때만 적는다
    if krw or usd:
        v = S["price"][1].format(krw=f"₩{krw:,}" if krw else "", usd=f"US${usd:,}" if usd else "")
        if global_ok and usd and S["price_usd"]:
            v += S["price_usd"].format(usd=f"US${usd:,}")
        rows.append((S["price"][0], v))
    rows.append((S["pay"][0], S["pay"][1] + (S["pay_usd"] if global_ok else "")))
    rows.append(S["account"])
    n = sum(1 for r in reports if r.get("sample"))
    if n:
        rows.append((S["samples"][0], f'{esc(S["samples"][1].format(n=n))} · '
                                      f'<a href="{ctx.url("samples/")}">{t["samples_link"]}</a>'))
    rows.append((S["b2b"][0], f'{esc(S["b2b"][1])} · <a href="{esc(mailto(ctx.site, t["b2b_subject"]))}">{t["b2b_cta"]}</a>'))
    body = "".join(f"<dt>{esc(k)}</dt><dd>{v if '<a ' in v else esc(v)}</dd>" for k, v in rows)
    return f'<dl class="spec">{body}</dl>'


def render_home(ctx, reports):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    mine = [r for r in reports if lang in r]
    lead = ""
    if mine:
        r = mine[0]
        lo = r[lang]
        points = lo.get("key_findings") or [f["title"] for f in lo.get("features", [])]
        findings = "".join(f"<li><span>{inline(x)}</span></li>" for x in points[:3])
        findings_html = (f'<p class="mini-label">{tt["key_findings"]}</p><ol class="findings">{findings}</ol>'
                         if findings else "")
        lead = f"""<section class="lead wrap" aria-labelledby="lead-title">
  <div class="lead-text">
    {docline(ctx, r, tt['latest'], pages=True)}
    <h1 class="lead-title" id="lead-title"><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h1>
    <p class="dek">{esc(lo.get('subtitle', ''))}</p>
    <div class="lead-findings">{findings_html}</div>
    <div class="buy-line">
      {price_html(ctx, r, big=True)}
      <div class="btn-row">{buy_buttons(ctx, r, primary_only=True)}{sample_button(ctx, r)}</div>
    </div>
    <p class="more"><a href="{report_url(ctx, r)}">{tt['details']} →</a></p>
  </div>
  <a class="lead-cover" href="{report_url(ctx, r)}" tabindex="-1" aria-hidden="true">{cover(ctx, r, 'cover-lg')}</a>
</section>"""
    past = ""
    if len(mine) > 1:
        rows = "".join(entry(ctx, r) for r in mine[1:7])
        past = f"""<section class="wrap section" aria-labelledby="past-h">
  <header class="section-head"><h2 id="past-h">{tt['recent']}</h2><a href="{ctx.url('reports/')}">{tt['view_all'].format(n=len(mine))} →</a></header>
  {entries_head(ctx)}
  <ol class="entries">{rows}</ol>
</section>"""
    upcoming = [it for r in mine for it in thresholds_of(ctx, r) if it["end"] >= TODAY]
    upcoming.sort(key=lambda x: (x["start"], x["end"]))
    ths = ""
    if len(upcoming) >= 3:
        ths = f"""<section class="wrap section" aria-labelledby="th-h">
  <header class="section-head"><h2 id="th-h">{tt['thresholds_home']}</h2><p class="section-note">{tt['thresholds_note']}</p></header>
  {threshold_list(ctx, upcoming[:6], home=True)}
</section>"""
    facts = ""
    if mine:
        n_cols = min(8, len(mine))
        facts = f"""<section class="wrap section facts-grid">
  <div>
    <header class="section-head"><h2>{tt['coverage_title']}</h2><p class="section-note">{tt['coverage_note'].format(n=n_cols)}</p></header>
    {coverage_matrix(ctx, mine)}
  </div>
  <div>
    <header class="section-head"><h2>{tt['spec_title']}</h2></header>
    {pub_spec(ctx, mine)}
  </div>
</section>"""
    body = f"{lead}\n{past}\n{ths}\n{facts}"
    return page(ctx, "", body, checkout=True, alt_path="")


def render_archive(ctx, reports):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    mine = [r for r in reports if lang in r]
    used = [k for k in site["sector_map"] if any(k in r.get("sectors", []) for r in mine)]
    count = lambda k: sum(k in r.get("sectors", []) for r in mine)
    chips = (f'<button class="chip" data-filter="" aria-pressed="true">{tt["filter_all"]} {num(len(mine))}</button>'
             + "".join(f'<button class="chip" data-filter="{k}" aria-pressed="false">'
                       f'{esc(sector_label(site, k, lang))} {num(count(k))}</button>' for k in used))
    listing = (f'{entries_head(ctx)}<ol class="entries">{"".join(entry(ctx, r) for r in mine)}</ol>' if mine
               else f'<p class="muted">{tt["empty"]}</p>')
    body = f"""<section class="page-head wrap">
  <h1>{tt['archive_title']}</h1>
  <p class="dek">{tt['archive_sub'].format(n=len(mine))}</p>
  <div class="filters" role="group">{chips}</div>
</section>
<section class="wrap section">{listing}</section>"""
    return page(ctx, tt["archive_title"], body, alt_path="reports/")


def toc_html(lines):
    if not any(l.startswith("# ") for l in lines):
        items = "".join(f"<li><span>{inline(x)}</span></li>" for x in lines)
        return f'<ol class="toc">{items}</ol>'
    groups, cur = [], (None, [])
    for l in lines:
        if l.startswith("# "):
            if cur[0] is not None or cur[1]:
                groups.append(cur)
            cur = (l[2:].strip(), [])
        else:
            cur[1].append(l)
    groups.append(cur)
    out = []
    for title, items in groups:
        head = f'<h3 class="toc-part">{inline(title)}</h3>' if title else ""
        lis = "".join(f"<li>{inline(x)}</li>" for x in items)
        out.append(f'<div class="toc-group">{head}' + (f'<ul class="toc toc-plain">{lis}</ul>' if lis else "") + "</div>")
    return f'<div class="toc-parts">{"".join(out)}</div>'


def render_report(ctx, r, has_alt):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    lo = r[lang]
    facts = [(tt["f_date"], num(fmt_date(r["date"], lang)))]
    if r.get("pages"):
        facts.append((tt["f_length"], esc(tt["pages_unit"].format(n=r["pages"]))))
    facts.append((tt["f_format"], esc("PDF · " + tt["lang_" + r.get("language", "ko")])))
    facts.append((tt["f_sector"], esc(sectors_text(ctx, r))))
    facts_html = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in facts)
    terms = list(tt["order_terms"])          # 실제로 가능한 결제 방법만 적는다
    if lang == "ko":
        if not korea_on(ctx, r):
            terms = [t for t in terms if t[0] != "국내 결제"]
        if not r.get("pay_global"):
            terms = [t for t in terms if t[0] != "해외 결제"]
    elif not r.get("pay_global"):          # 영어 화면은 해외 결제뿐: 링크가 없으면 결제·발송 안내도 뺀다
        terms = [t for t in terms if t[0] not in ("Checkout", "Delivery")]
    terms_html = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in terms)
    def clause(title, inner, cls=""):
        return f'<section class="clause{cls}"><h2>{title}</h2>{inner}</section>'

    clauses = []
    if lo.get("quote"):
        src = f'<p class="quote-source">{esc(lo["quote_source"])}</p>' if lo.get("quote_source") else ""
        clauses.append(clause(f'<span class="sr-only">{tt["quote_label"]}</span>',
                              f'<blockquote class="quote"><p>{inline(lo["quote"])}</p>{src}</blockquote>', " clause-quote"))
    if lo.get("body"):
        clauses.append(clause(tt["overview"], f'<div class="prose">{md(lo["body"])}</div>'))
    if lo.get("numbers"):
        cells = "".join(
            f'<div><dt>{esc(n.get("label", ""))}</dt><dd><span class="num">{esc(n["value"])}</span>'
            f'<span class="unit">{esc(n.get("unit", ""))}</span></dd></div>' for n in lo["numbers"])
        clauses.append(clause(tt["numbers_title"], f'<dl class="numbers">{cells}</dl>'))
    if lo.get("features"):
        items = "".join(f'<li><h3>{esc(f["title"])}</h3><p>{inline(f.get("text", ""))}</p></li>' for f in lo["features"])
        clauses.append(clause(tt["features_title"], f'<ul class="features">{items}</ul>'))
    if lo.get("key_findings"):
        items = "".join(f"<li><span>{inline(x)}</span></li>" for x in lo["key_findings"])
        clauses.append(clause(tt["key_findings"], f'<ol class="findings">{items}</ol>'))
    if lo.get("figures"):
        figs = "".join(
            f'<figure class="fig"><figcaption>{esc(f.get("title", ""))}</figcaption>'
            f'<img src="{ctx.root}figures/{esc(f["image"])}" alt="{esc(f.get("title", ""))}" loading="lazy">'
            + (f'<p class="fig-note">{esc(f["note"])}</p>' if f.get("note") else "") + "</figure>"
            for f in lo["figures"])
        clauses.append(clause(tt["figures_title"], f'<div class="figs">{figs}</div>'))
    ths = thresholds_of(ctx, r)
    if ths:
        clauses.append(clause(tt["thresholds"], threshold_list(ctx, ths)))
    if lo.get("toc"):
        clauses.append(clause(tt["toc"], toc_html(lo["toc"])))
    if lo.get("for_whom"):
        items = "".join(f"<li>{inline(x)}</li>" for x in lo["for_whom"])
        clauses.append(clause(tt["for_whom_title"], f'<ul class="for-whom">{items}</ul>'))
    if lo.get("author"):
        clauses.append(clause(tt["author_title"], f'<div class="prose">{md(lo["author"])}</div>'))
    info = [(tt["i_title"], esc(lo["title"]))]
    info.append((tt["i_author"], "LIMEN RESEARCH"))
    info.append((tt["i_date"], num(fmt_date(r["date"], lang))))
    if r.get("pages"):
        info.append((tt["f_length"], esc(tt["pages_unit"].format(n=r["pages"]))))
    info.append((tt["f_format"], esc("PDF · " + tt["lang_" + r.get("language", "ko")])))
    info.append((tt["f_sector"], esc(sectors_text(ctx, r))))
    info += [(esc(k), esc(v)) for k, v in lo.get("info", [])]
    price = price_html(ctx, r, ref=False)
    if price:
        info.append((tt["i_price"], price))
    rows = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in info)
    clauses.append(clause(tt["info_title"], f'<dl class="spec">{rows}</dl>'))
    b2b = esc(mailto(site, tt["b2b_subject"] + " - " + issue_no(r)))
    series = f'<p class="series">{esc(r["series"])}</p>' if r.get("series") else ""
    body = f"""<article class="wrap report">
  <p class="crumbs"><a href="{ctx.url('reports/')}">{tt['archive_title']}</a> / {num(issue_no(r))}</p>
  <header class="report-head">
    <div class="report-head-text">
      {series}
      {docline(ctx, r, pages=True)}
      <h1>{esc(lo['title'])}</h1>
      <p class="dek">{esc(lo.get('subtitle', ''))}</p>
    </div>
    <div class="report-head-cover">{cover(ctx, r, 'cover-md')}</div>
  </header>
  <div class="buy-inline">{price_html(ctx, r, big=True)}<div class="btn-row">{buy_buttons(ctx, r, primary_only=True)}</div></div>
  <div class="report-body">
    <div class="report-main">{''.join(clauses)}</div>
    <aside class="order" aria-label="{tt['purchase']}">
      <dl class="order-facts">{facts_html}</dl>
      <div class="order-price">{price_html(ctx, r, big=True)}</div>
      <div class="order-buttons">{buy_buttons(ctx, r, block=True)}{sample_button(ctx, r, block=True)}</div>
      <dl class="order-terms">{terms_html}</dl>
      <p class="order-links"><a href="{ctx.url('refund/')}">{tt['refund_link']}</a><a href="{b2b}">{tt['b2b_title']}</a></p>
    </aside>
  </div>
</article>"""
    return page(ctx, lo["title"], body, description=lo.get("summary", ""), checkout=True,
                alt_path=f"reports/{r['slug']}/" if has_alt else None, noindex=bool(r.get("unlisted")))


def render_samples(ctx, reports):
    tt, lang = ctx.t, ctx.lang
    items = []
    for r in reports:
        if lang not in r or not r.get("sample"):
            continue
        lo = r[lang]
        items.append(f"""<li class="entry entry-sample">
  <a class="entry-cover" href="{esc(ctx.sample_url(r))}" tabindex="-1" aria-hidden="true">{cover(ctx, r, 'cover-xs')}</a>
  <div class="entry-main">
    {docline(ctx, r)}
    <h3><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h3>
    <p class="entry-sum">{esc(lo.get('summary', ''))}</p>
    <div class="btn-row">{sample_button(ctx, r)}<a class="more-link" href="{report_url(ctx, r)}">{tt['details']} →</a></div>
  </div>
</li>""")
    listing = f'<ol class="entries">{"".join(items)}</ol>' if items else f'<p class="muted">{tt["samples_empty"]}</p>'
    body = f"""<section class="page-head wrap"><h1>{tt['samples_title']}</h1><p class="dek">{tt['samples_sub']}</p></section>
<section class="wrap section">{listing}</section>"""
    return page(ctx, tt["samples_title"], body, alt_path="samples/")


def render_doc(ctx, name, text, has_alt):
    text = text.replace("{email}", ctx.site["email"])
    title = text.strip().splitlines()[0].lstrip("# ").strip()
    rest = "\n".join(text.strip().splitlines()[1:])
    body = f"""<section class="page-head wrap"><h1>{esc(title)}</h1></section>
<section class="wrap section"><div class="prose doc">{md(rest)}</div></section>"""
    return page(ctx, title, body, alt_path=f"{name}/" if has_alt else None, noindex=name in HIDDEN_PAGES)


def render_404(site):
    lang = site["languages"][0]
    ctx = Ctx(site, lang, "")
    ctx.root = site["base_path"]          # 404는 아무 주소에서나 뜨므로 절대 경로 사용
    tt = ctx.t
    body = f"""<section class="page-head wrap">
  <h1>{tt['not_found_title']}</h1><p class="dek">{tt['not_found_text']}</p>
  <p class="more"><a href="{ctx.url()}">{tt['home']} →</a></p>
</section>"""
    return page(ctx, tt["not_found_title"], body)


def render_en_teaser(site, reports):
    """영어 사이트를 열기 전에 두는 영문 안내 페이지 (/en/). 보고서 링크는 한국어 페이지로 간다."""
    ctx = Ctx(site, "en", "")
    tt = ctx.t
    rows = []
    for r in reports:
        lo = r.get("en") or r[site["languages"][0]]
        rows.append(f"""<li class="entry entry-sample">
  <a class="entry-cover" href="{report_url(ctx, r)}" tabindex="-1" aria-hidden="true">{cover(ctx, r, 'cover-xs')}</a>
  <div class="entry-main">
    {docline(ctx, r, pages=True)}
    <h3><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h3>
    <p class="more"><a href="{report_url(ctx, r)}">{tt['teaser_open']} →</a></p>
  </div>
</li>""")
    body = f"""<section class="page-head wrap">
  <h1>{tt['teaser_title']}</h1>
  <p class="dek">{tt['teaser_lead']}</p>
  <p class="more">{tt['teaser_contact']} <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a>.</p>
</section>
<section class="wrap section">
  <header class="section-head"><h2>{tt['teaser_list']}</h2></header>
  <ol class="entries">{''.join(rows)}</ol>
</section>"""
    return page(ctx, tt["teaser_title"], body, description=tt["teaser_lead"])


# ---------------------------------------------------------------------------
# 빌드
# ---------------------------------------------------------------------------
def write(rel, content):
    path = OUT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return rel


def build():
    site = load_site()
    reports = load_reports(site)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT / "assets")
    if (CONTENT / "samples").exists():
        shutil.copytree(CONTENT / "samples", OUT / "samples", ignore=shutil.ignore_patterns(".*"))
    for folder in ("covers", "figures"):
        if (CONTENT / folder).exists():
            shutil.copytree(CONTENT / folder, OUT / folder, ignore=shutil.ignore_patterns(".*"))

    listed = [r for r in reports if not r.get("unlisted")]   # 목록·홈·샘플에 나오는 보고서
    written, hidden = [], []                                   # hidden: 사이트맵에서 빼는 페이지
    langs = site["languages"]
    for lang in langs:
        pre = "" if lang == langs[0] else f"{lang}/"
        C = lambda p: Ctx(site, lang, p)
        written.append(write(pre + "index.html", render_home(C(""), listed)))
        written.append(write(pre + "reports/index.html", render_archive(C("reports/"), listed)))
        written.append(write(pre + "samples/index.html", render_samples(C("samples/"), listed)))
        for r in reports:
            if lang in r:
                has_alt = all(l in r for l in langs)
                p = f"reports/{r['slug']}/"
                html_ = render_report(C(p), r, has_alt)
                (hidden if r.get("unlisted") else written).append(write(pre + p + "index.html", html_))
        for name in DOC_PAGES:
            src = CONTENT / "pages" / f"{name}.{lang}.md"
            if src.exists():
                has_alt = all((CONTENT / "pages" / f"{name}.{l}.md").exists() for l in langs)
                html_ = render_doc(C(f"{name}/"), name, src.read_text(encoding="utf-8"), has_alt)
                (hidden if name in HIDDEN_PAGES else written).append(write(pre + f"{name}/index.html", html_))
    if "en" not in langs:                     # 영어 사이트를 열기 전: 메뉴의 EN 버튼이 가는 안내 페이지
        written.append(write("en/index.html", render_en_teaser(site, listed)))
    write("404.html", render_404(site))

    base = site["site_url"].rstrip("/") + "/"
    urls = "".join(f"<url><loc>{esc(base + w.removesuffix('index.html'))}</loc></url>" for w in written)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n'
                         f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n")
    extra = f" (비공개 {len(hidden)}개 별도)" if hidden else ""
    print(f"완료: 페이지 {len(written)}개{extra}, 보고서 {len(listed)}편, 언어 {', '.join(langs)} → {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    build()
