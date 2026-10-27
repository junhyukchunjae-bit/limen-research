# LIMEN RESEARCH 사이트 작업 안내

- `build.py` 가 `content/` 를 읽어 `_site/` 에 정적 사이트를 만든다. 외부 패키지 없이 Python 3.11+ 표준 라이브러리만 쓴다.
- 보고서 추가: `content/reports/YYYY-MM-DD-slug.toml`. 기존 파일 형식을 따르고, `issue` 는 사이트에서만 쓰는 순서 번호(이전 보고서 +1, 출간 예정 포함), `sectors` 는 `content/site.toml` 의 key 만 쓴다.
- `content/samples/` 에는 무료 샘플만 둔다. 유료 보고서 원본 PDF는 절대 커밋하지 않는다 (공개 저장소).
- 사이트는 소개·샘플·구매 링크만 한다. 결제를 받지 않는다. 판매는 교보문고: 보고서의 `buy_url` 에 상품 주소, `price_krw` 에 교보문고 판매가. 판매처 이름은 `site.toml` 의 `store`. 판매 형태는 주문형 종이책(POD)이 기본이고, 보고서마다 다르면 `format` 으로 적는다 (예: `format = "전자책(PDF)"`).
- 출간 예정 보고서: `upcoming = true` 와 `expected = "2026-Q4"`(YYYY-Qn·YYYY-MM·YYYY-MM-DD). 파일 이름은 `YYYY-qN-slug.toml`. 홈 '출간 예정'에 나오고 구매 버튼은 잠긴다. `[ko].body` 가 없으면 상세 페이지 없이 목록에만 나온다. 제목이 확정 전이면 '(가칭)'을 붙인다.
- 보고서 파일에 `unlisted = true` 를 넣으면 페이지는 만들어지지만 목록·홈·샘플·사이트맵에서 빠진다 (공개 전 미리보기용). `draft = true` 는 아예 만들지 않는다.
- 모든 실제 보고서에는 무료 샘플(`sample`)을 붙인다. 샘플 PDF 제공이 사이트의 핵심 기능이다.
- 문턱 일정: 보고서 `[ko]` 에 `thresholds = ["2027-06 | 설명", "2027-Q2 | 설명"]` (날짜는 YYYY, YYYY-MM, YYYY-MM-DD, YYYY-Qn). 보고서 원문에서 가져온 실제 일정만 쓴다. 기준일(지금 선)은 빌드한 날(한국 시간).
- 표지: 기본은 CSS로 그린다. 실제 PDF 첫 장 이미지를 쓰려면 `content/covers/` 에 넣고 보고서에 `cover_image = "파일명.png"`.
- 디자인 규칙: 글꼴은 IBM Plex Sans KR 하나. 강조색(`--signal`, 청록)은 문턱선·'최신 리포트'·초점 표시에만 쓴다. 카드·그림자·둥근 모서리·장식용 괘선을 넣지 않는다 (선은 표에만).
- 로고: `static/brand/` 의 파일을 그대로 쓴다 (다시 그리거나 늘리지 않는다, 사용 규칙은 `static/brand/README.md`). 사이트 머리글·바닥은 `build.py` 의 `brand_svg()` 가 `logo-header.svg`(32px)·`logo-header-mobile.svg`(28px)를 인라인으로 넣고, 막대 색은 `--signal` 을 따른다. 로고 PNG·파비콘 PNG·`og.png` 를 다시 만들 때는 SVG에서 렌더링한다.
- 보고서는 정기 발행이 아니다(분기에 2~3권, 이슈가 있을 때). '주간'·'호' 같은 말을 쓰지 않는다. `issue` 가 가장 큰 발행된(출간 예정 아님) 보고서가 홈의 '최신 리포트'가 된다.
- 상세 페이지 선택 항목(예시: `content/reports/2026-10-27-sdv-to-aidv.toml`): `series`, `[ko]` 의 `quote`·`quote_source`, `numbers`(값·단위·이름), `features`(제목·설명), `figures`(`content/figures/` 이미지·제목·출처), `toc` 의 `# ` 줄(부·장 제목), `for_whom`, `author`, `info`(추가 정보 행).
- 원본 PDF는 이 세션의 임시 폴더에서만 다룬다 (구글 드라이브 커넥터로 받기). 저장소에는 표지(`content/covers/`), 그림 미리보기(`content/figures/`), 무료 샘플(`content/samples/`)만 넣는다.
- `languages` 에 `en` 이 없으면 메뉴의 EN 버튼이 영문 안내 페이지(`/en/`)로 간다.
- 수정 후 `python3 build.py` 가 오류 없이 끝나는지 확인한다. 영어 페이지도 확인하려면 `LIMEN_LANGS=ko,en python3 build.py`.
- 사이트 운영자는 GitHub 초보다. 설명은 한국어로, 클릭 위치까지 구체적으로 안내한다.
