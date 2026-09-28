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

esc = html.escape

# ---------------------------------------------------------------------------
# 화면 문구 (언어별)
# ---------------------------------------------------------------------------
T = {
    "ko": {
        "html_lang": "ko",
        "nav_reports": "보고서",
        "nav_samples": "무료 샘플",
        "nav_about": "소개",
        "switch_label": "EN",
        "cta_latest": "최신 보고서 보기",
        "cta_samples": "무료 샘플 받기",
        "latest": "이번 호",
        "recent": "지난 호",
        "view_all": "전체 목록",
        "coverage": "다루는 분야",
        "reports_count": "{n}편",
        "how_title": "구매 안내",
        "how_items": [
            ("국내 결제.", "카드·간편결제·계좌이체. 결제 확인 후 영업일 24시간 이내에 이메일로 PDF를 보내 드립니다."),
            ("해외 결제.", "해외 카드·PayPal. 결제 즉시 이메일로 PDF가 발송됩니다."),
            ("회원가입은 없습니다.", "모든 보고서는 무료 샘플로 먼저 확인할 수 있습니다."),
        ],
        "b2b_title": "기업·기관 구매",
        "b2b_text": "여러 부서가 함께 보는 라이선스, 정기 구매, 별도 결제 방식이 필요하면 문의해 주세요.",
        "b2b_cta": "구매 문의하기",
        "b2b_subject": "[LIMEN RESEARCH] 기업·기관 구매 문의",
        "archive_title": "보고서 목록",
        "archive_sub": "지금까지 발행한 모든 보고서입니다. 분야별로 걸러 볼 수 있습니다.",
        "filter_all": "전체",
        "empty": "아직 발행된 보고서가 없습니다.",
        "pages_unit": "{n}쪽",
        "lang_ko": "한국어",
        "lang_en": "영어",
        "buy": "구매하기",
        "buy_soon": "판매 준비 중",
        "sample": "무료 샘플 PDF",
        "details": "보고서 소개",
        "f_date": "발행일",
        "f_length": "분량",
        "f_format": "형식",
        "overview": "개요",
        "key_findings": "핵심 내용",
        "toc": "목차",
        "purchase": "구매 정보",
        "price_global": "해외 결제 US${usd}",
        "pay_kr": "국내 결제하기",
        "pay_kr_apply": "국내 구매 신청",
        "pay_global": "해외 카드·PayPal 결제",
        "order_subject": "[LIMEN RESEARCH] 구매 신청 - {report}",
        "order_body": ("보고서: {report}\n가격: {price}\n\n"
                       "이름(회사명):\nPDF를 받을 이메일:\n"
                       "결제 방법 (카드 결제 링크 / 계좌이체):\n입금자명 (계좌이체 시):\n"
                       "증빙 필요 여부 (현금영수증 등):\n"),
        "purchase_notes": [
            "회원가입 없이 구매합니다",
            "국내 결제: 카드·간편결제·계좌이체. 결제 확인 후 영업일 24시간 이내 이메일로 PDF 발송",
            "해외 결제: 해외 카드·PayPal(USD). 결제 즉시 이메일로 PDF 자동 발송",
            "디지털 상품 특성상 발송 후에는 청약철회가 제한됩니다",
        ],
        "refund_link": "환불정책 보기",
        "samples_title": "무료 샘플",
        "samples_sub": "보고서의 일부를 미리 읽어 보세요. 구매 전에 분석의 깊이와 형식을 확인할 수 있습니다.",
        "samples_empty": "공개된 샘플이 아직 없습니다.",
        "sample_of": "{title} 샘플",
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
        "nav_reports": "Reports",
        "nav_samples": "Free samples",
        "nav_about": "About",
        "switch_label": "한국어",
        "cta_latest": "See the latest report",
        "cta_samples": "Get a free sample",
        "latest": "This issue",
        "recent": "Past issues",
        "view_all": "All reports",
        "coverage": "Coverage",
        "reports_count": "{n} reports",
        "how_title": "How to buy",
        "how_items": [
            ("Checkout.", "Pay by card or PayPal. No account needed."),
            ("Delivery.", "A PDF download link is emailed right after payment."),
            ("Samples.", "Every report has a free sample to read first."),
        ],
        "b2b_title": "Team & enterprise purchases",
        "b2b_text": "Need a license for several teams, recurring purchases or another payment method? Get in touch.",
        "b2b_cta": "Contact us",
        "b2b_subject": "[LIMEN RESEARCH] Team purchase inquiry",
        "archive_title": "Report archive",
        "archive_sub": "Every report we have published. Filter by sector.",
        "filter_all": "All",
        "empty": "No reports published yet.",
        "pages_unit": "{n} pages",
        "lang_ko": "Korean",
        "lang_en": "English",
        "buy": "Buy now",
        "buy_soon": "Coming soon",
        "sample": "Free sample (PDF)",
        "details": "About this report",
        "f_date": "Published",
        "f_length": "Length",
        "f_format": "Format",
        "overview": "Overview",
        "key_findings": "Key findings",
        "toc": "Contents",
        "purchase": "Purchase",
        "purchase_notes": [
            "No account needed, just your email",
            "PDF download link sent right after payment",
            "Prices are charged in US dollars",
            "As a digital product, sales are final once delivered",
        ],
        "refund_link": "Refund policy",
        "samples_title": "Free samples",
        "samples_sub": "Read part of a report before you buy to see the depth and format of our analysis.",
        "samples_empty": "No samples published yet.",
        "sample_of": "Sample of {title}",
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
        reports.append(r)
    reports.sort(key=lambda r: (r["date"], r.get("issue", 0)), reverse=True)
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


def sector_label(site, key, lang):
    return site["sector_map"][key][lang]


def korea_on(ctx, r):
    """이 화면에서 국내 결제(원화)를 보여줄지. 한국어 화면 + [korea] 켜짐 + 원화 가격이 있을 때."""
    return (ctx.lang == "ko" and ctx.site.get("korea", {}).get("enabled", False)
            and bool(r.get("price_krw")))


def price_html(ctx, r, big=False):
    usd = r.get("price_usd")
    if korea_on(ctx, r):
        main = f"₩{r['price_krw']:,}"
        ref = ""
        if usd and r.get("pay_global"):
            ref = f'<span class="price-ref">{esc(ctx.t["price_global"].format(usd=format(usd, ",")))}</span>'
    elif usd:
        main, ref = f"US${usd:,}", ""
    else:
        return ""
    cls = "price price-big" if big else "price"
    return f'<span class="{cls}"><span class="price-main">{main}</span>{ref}</span>'


def mailto(site, subject, body=""):
    url = f"mailto:{site['email']}?subject={quote(subject)}"
    return url + (f"&body={quote(body)}" if body else "")


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


def sectors_text(ctx, r, sep=" / "):
    return sep.join(sector_label(ctx.site, k, ctx.lang) for k in r.get("sectors", []))


def example_mark(ctx, r):
    return f' <span class="example">[{ctx.t["example"]}]</span>' if r.get("example") else ""


def kicker(ctx, r, lead=""):
    """'이번 호 · No. 003 · 2026.09.28 · 모빌리티' 같은 한 줄 머리글."""
    parts = [lead, issue_no(r), fmt_date(r["date"], ctx.lang), sectors_text(ctx, r)]
    return f'<p class="kicker">{" · ".join(esc(p) for p in parts if p)}{example_mark(ctx, r)}</p>'


def cover(ctx, r, cls=""):
    """보고서 앞표지. 이미지 없이 CSS로 그린다."""
    lo = r.get(ctx.lang, {})
    first = r["sectors"][0] if r.get("sectors") else None
    color = ctx.site["sector_map"][first]["color"] if first else "#888888"
    title = lo.get("cover_title") or lo.get("title", "")
    return f"""<div class="cover {cls}" style="--sector:{esc(color)}" aria-hidden="true">
  <div class="cover-head"><span>LIMEN RESEARCH</span><span>{issue_no(r)}</span></div>
  <div class="cover-title">{esc(title)}</div>
  <div class="cover-foot"><span>{esc(sectors_text(ctx, r, " · "))}</span><span>{fmt_date(r["date"], ctx.lang)}</span></div>
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


def nav_links(ctx, alt_path):
    site, lang = ctx.site, ctx.lang
    nav = [("reports/", ctx.t["nav_reports"]), ("samples/", ctx.t["nav_samples"]), ("about/", ctx.t["nav_about"])]
    current = ' aria-current="page"'
    links = "".join(f'<a href="{ctx.url(p)}"{current if ctx.path.startswith(p) else ""}>{esc(label)}</a>'
                    for p, label in nav)
    if len(site["languages"]) > 1 and alt_path is not None:
        other = [l for l in site["languages"] if l != lang][0]
        links += f'<a class="lang" href="{ctx.url(alt_path, other)}" hreflang="{other}">{T[lang]["switch_label"]}</a>'
    return links


def header(ctx, alt_path, edition=None):
    """edition 이 있으면 홈용 큰 제호(마스트헤드), 없으면 한 줄 머리."""
    nav = nav_links(ctx, alt_path)
    if edition is not None:
        return f"""<header class="masthead">
  <div class="wrap">
    <div class="mast-bar"><span>{esc(edition)}</span><nav class="nav">{nav}</nav></div>
    <a class="mast-brand" href="{ctx.url()}">LIMEN RESEARCH</a>
    <p class="mast-tag">{esc(ctx.site[ctx.lang]["tagline"])}</p>
  </div>
</header>"""
    return f"""<header class="topbar">
  <div class="wrap topbar-inner">
    <a class="brand" href="{ctx.url()}">LIMEN RESEARCH</a>
    <nav class="nav">{nav}</nav>
  </div>
</header>"""


def footer(ctx):
    site, tt = ctx.site, ctx.t
    biz = site.get("business", {})
    rows = [f"{esc(tt['biz'][k])} {esc(str(v))}" for k, v in biz.items() if v and k in tt["biz"]]
    biz_html = f'<p>{" · ".join(rows)}</p>' if rows else ""
    year = dt.date.today().year
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <a class="brand" href="{ctx.url()}">LIMEN RESEARCH</a>
      <nav class="foot-nav">
        <a href="{ctx.url('terms/')}">{tt['terms']}</a>
        <a href="{ctx.url('refund/')}">{tt['refund']}</a>
        <a href="{ctx.url('privacy/')}">{tt['privacy']}</a>
        <a href="mailto:{esc(site['email'])}">{esc(site['email'])}</a>
      </nav>
    </div>
    <div class="foot-bottom">{biz_html}<p>© {year} LIMEN RESEARCH. {esc(site[ctx.lang]["tagline"])}</p></div>
  </div>
</footer>"""


FONTS = ("https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700;900&display=swap",
         "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css")


def page(ctx, title, body, description="", alt_path=None, checkout=False, edition=None, noindex=False):
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
    fonts = "".join(f'\n<link rel="stylesheet" href="{f}">' for f in FONTS)
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
<meta name="theme-color" content="#f5f2ea">
<link rel="icon" href="{ctx.asset('favicon.svg')}" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>{fonts}
<link rel="stylesheet" href="{ctx.asset('site.css')}">
<script src="{ctx.asset('site.js')}" defer></script>{lemon}
</head>
<body>
{header(ctx, alt_path, edition)}
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
    """목록 한 줄: 호수 · 날짜 | 분야 · 제목 · 요약 | 가격"""
    lo = r[ctx.lang]
    return f"""<li class="entry" data-sectors="{' '.join(r.get('sectors', []))}">
  <div class="entry-no"><span>{issue_no(r)}</span><span>{fmt_date(r['date'], ctx.lang)}</span></div>
  <div class="entry-main">
    <p class="entry-sectors">{esc(sectors_text(ctx, r))}{example_mark(ctx, r)}</p>
    <h3><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h3>
    <p>{esc(lo.get('summary', ''))}</p>
  </div>
  <div class="entry-price">{price_html(ctx, r)}</div>
</li>"""


def render_home(ctx, reports):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    mine = [r for r in reports if lang in r]
    edition = site[lang]["eyebrow"]
    lead = ""
    if mine:
        r = mine[0]
        lo = r[lang]
        edition = f"{issue_no(r)} · {fmt_date(r['date'], lang)}"
        sample = (f'<a class="text-link" href="{esc(ctx.sample_url(r))}">{tt["sample"]} →</a>'
                  if r.get("sample") else "")
        lead = f"""<section class="lead wrap">
  <div class="lead-text">
    {kicker(ctx, r, tt['latest'])}
    <h1 class="lead-title"><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h1>
    <p class="dek">{esc(lo.get('subtitle', ''))}</p>
    <p class="lead-summary">{esc(lo.get('summary', ''))}</p>
    <div class="buy-line">
      {price_html(ctx, r, big=True)}
      <div class="btn-row">{buy_buttons(ctx, r, primary_only=True)}</div>
    </div>
    <p class="more-links"><a class="text-link" href="{report_url(ctx, r)}">{tt['details']} →</a>{sample}</p>
  </div>
  <a class="lead-cover" href="{report_url(ctx, r)}" tabindex="-1">{cover(ctx, r)}</a>
</section>"""
    past = ""
    if len(mine) > 1:
        rows = "".join(entry(ctx, r) for r in mine[1:8])
        past = f"""<section class="wrap block">
  <div class="block-head"><h2 class="label">{tt['recent']}</h2><a class="text-link" href="{ctx.url('reports/')}">{tt['view_all']} →</a></div>
  <ol class="entries">{rows}</ol>
</section>"""
    counts = {k: sum(k in r.get("sectors", []) for r in mine) for k in site["sector_map"]}
    sectors = "".join(
        f'<li><a href="{ctx.url("reports/")}?sector={k}">{esc(sec[lang])}</a><span>{counts[k]}</span></li>'
        for k, sec in site["sector_map"].items())
    how = "".join(f"<p><strong>{esc(h)}</strong> {esc(p)}</p>" for h, p in tt["how_items"])
    body = f"""{lead}
{past}
<section class="wrap block columns">
  <div>
    <h2 class="label">{tt['coverage']}</h2>
    <ul class="sector-list">{sectors}</ul>
  </div>
  <div>
    <h2 class="label">{tt['how_title']}</h2>
    {how}
  </div>
  <div>
    <h2 class="label">{tt['b2b_title']}</h2>
    <p>{tt['b2b_text']}</p>
    <p><a class="text-link" href="{esc(mailto(site, tt['b2b_subject']))}">{tt['b2b_cta']} →</a></p>
  </div>
</section>"""
    return page(ctx, "", body, checkout=True, alt_path="", edition=edition)


def render_archive(ctx, reports):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    mine = [r for r in reports if lang in r]
    used = [k for k in site["sector_map"] if any(k in r.get("sectors", []) for r in mine)]
    chips = f'<button class="chip" data-filter="" aria-pressed="true">{tt["filter_all"]}</button>' + "".join(
        f'<button class="chip" data-filter="{k}" aria-pressed="false">{esc(sector_label(site, k, lang))}</button>'
        for k in used)
    listing = (f'<ol class="entries">{"".join(entry(ctx, r) for r in mine)}</ol>' if mine
               else f'<p class="muted">{tt["empty"]}</p>')
    body = f"""<section class="page-head wrap">
  <h1>{tt['archive_title']}</h1>
  <p class="dek">{tt['archive_sub']}</p>
  <div class="filters" role="group">{chips}</div>
</section>
<section class="wrap block-tight">{listing}</section>"""
    return page(ctx, tt["archive_title"], body, alt_path="reports/")


def render_report(ctx, r, has_alt):
    site, tt, lang = ctx.site, ctx.t, ctx.lang
    lo = r[lang]
    facts = [(tt["f_date"], fmt_date(r["date"], lang))]
    if r.get("pages"):
        facts.append((tt["f_length"], tt["pages_unit"].format(n=r["pages"])))
    facts.append((tt["f_format"], "PDF · " + tt["lang_" + r.get("language", "ko")]))
    facts_html = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in facts)
    sample = (f'<a class="btn btn-line btn-block" href="{esc(ctx.sample_url(r))}">{tt["sample"]}</a>'
              if r.get("sample") else "")
    notes = "".join(f"<li>{esc(n)}</li>" for n in tt["purchase_notes"])
    sections = []
    if lo.get("body"):
        sections.append(f'<section><h2 class="label">{tt["overview"]}</h2>{md(lo["body"])}</section>')
    if lo.get("key_findings"):
        items = "".join(f"<li><span>{inline(x)}</span></li>" for x in lo["key_findings"])
        sections.append(f'<section><h2 class="label">{tt["key_findings"]}</h2><ol class="findings">{items}</ol></section>')
    if lo.get("toc"):
        items = "".join(f"<li><span>{inline(x)}</span></li>" for x in lo["toc"])
        sections.append(f'<section><h2 class="label">{tt["toc"]}</h2><ol class="toc">{items}</ol></section>')
    body = f"""<article class="wrap report">
  <p class="crumbs"><a href="{ctx.url('reports/')}">{tt['archive_title']}</a> / {issue_no(r)}</p>
  <header class="report-head">
    {kicker(ctx, r)}
    <h1>{esc(lo['title'])}</h1>
    <p class="dek">{esc(lo.get('subtitle', ''))}</p>
  </header>
  <div class="report-body">
    <div class="prose">{''.join(sections)}</div>
    <aside class="buy-box">
      {cover(ctx, r, 'cover-sm')}
      <dl class="facts">{facts_html}</dl>
      <div class="buy-price">{price_html(ctx, r, big=True)}</div>
      {buy_buttons(ctx, r, block=True)}
      {sample}
      <ul class="notes">{notes}</ul>
      <p class="small"><a href="{ctx.url('refund/')}">{tt['refund_link']}</a> · <a href="{esc(mailto(site, tt['b2b_subject'] + ' - ' + issue_no(r)))}">{tt['b2b_title']}</a></p>
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
        items.append(f"""<li class="sample">
  <a href="{esc(ctx.sample_url(r))}" tabindex="-1">{cover(ctx, r, 'cover-xs')}</a>
  <div>
    {kicker(ctx, r)}
    <h3><a href="{report_url(ctx, r)}">{esc(lo['title'])}</a></h3>
    <p>{esc(lo.get('summary', ''))}</p>
    <p class="more-links"><a class="text-link" href="{esc(ctx.sample_url(r))}">{tt['sample']} →</a><a class="text-link" href="{report_url(ctx, r)}">{tt['details']} →</a></p>
  </div>
</li>""")
    listing = f'<ul class="samples">{"".join(items)}</ul>' if items else f'<p class="muted">{tt["samples_empty"]}</p>'
    body = f"""<section class="page-head wrap"><h1>{tt['samples_title']}</h1><p class="dek">{tt['samples_sub']}</p></section>
<section class="wrap block-tight">{listing}</section>"""
    return page(ctx, tt["samples_title"], body, alt_path="samples/")


def render_doc(ctx, name, text, has_alt):
    text = text.replace("{email}", ctx.site["email"])
    title = text.strip().splitlines()[0].lstrip("# ").strip()
    rest = "\n".join(text.strip().splitlines()[1:])
    body = f"""<section class="page-head wrap narrow"><h1>{esc(title)}</h1></section>
<section class="wrap narrow block-tight prose doc">{md(rest)}</section>"""
    return page(ctx, title, body, alt_path=f"{name}/" if has_alt else None, noindex=name in HIDDEN_PAGES)


def render_404(site):
    lang = site["languages"][0]
    ctx = Ctx(site, lang, "")
    ctx.root = site["base_path"]          # 404는 아무 주소에서나 뜨므로 절대 경로 사용
    tt = ctx.t
    body = f"""<section class="page-head wrap narrow">
  <h1>{tt['not_found_title']}</h1><p class="dek">{tt['not_found_text']}</p>
  <p><a class="text-link" href="{ctx.url()}">{tt['home']} →</a></p>
</section>"""
    return page(ctx, tt["not_found_title"], body)


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
