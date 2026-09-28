# LIMEN RESEARCH 사이트 작업 안내

- `build.py` 가 `content/` 를 읽어 `_site/` 에 정적 사이트를 만든다. 외부 패키지 없이 Python 3.11+ 표준 라이브러리만 쓴다.
- 보고서 추가: `content/reports/YYYY-MM-DD-slug.toml`. 기존 파일 형식을 따르고, `issue` 는 이전 호 +1, `sectors` 는 `content/site.toml` 의 key 만 쓴다.
- `content/samples/` 에는 무료 샘플만 둔다. 유료 보고서 원본 PDF는 절대 커밋하지 않는다 (공개 저장소).
- 결제 링크: 해외(Lemon Squeezy) `pay_global`, 국내(페이앱·토스페이먼츠 등) `pay_korea`. 국내 링크가 없으면 구매 신청(신청서 또는 이메일)으로 연결된다.
- 보고서 파일에 `unlisted = true` 를 넣으면 페이지는 만들어지지만 목록·홈·샘플·사이트맵에서 빠진다 (결제 테스트, 공개 전 미리보기용). `draft = true` 는 아예 만들지 않는다.
- 모든 실제 보고서에는 무료 샘플(`sample`)을 붙인다. 환불정책의 청약철회 제한이 '구매 전 샘플 제공'을 근거로 한다.
- 문턱 일정: 보고서 `[ko]` 에 `thresholds = ["2027-06 | 설명", "2027-Q2 | 설명"]` (날짜는 YYYY, YYYY-MM, YYYY-MM-DD, YYYY-Qn). 보고서 원문에서 가져온 실제 일정만 쓴다. 기준일(지금 선)은 빌드한 날(한국 시간).
- 표지: 기본은 CSS로 그린다. 실제 PDF 첫 장 이미지를 쓰려면 `content/covers/` 에 넣고 보고서에 `cover_image = "파일명.png"`.
- 디자인 규칙: 글꼴은 IBM Plex Sans KR 하나. 강조색(`--signal`, 청록)은 문턱선·'이번 호'·초점 표시에만 쓴다. 카드·그림자·둥근 모서리·장식용 괘선을 넣지 않는다 (선은 표에만).
- 호수(`issue`)가 발행 순서다. 가장 큰 호수가 홈의 '이번 호'가 된다.
- 상세 페이지 선택 항목(예시: `content/reports/2026-09-28-sdv-to-aidv.toml`): `series`, `[ko]` 의 `quote`·`quote_source`, `numbers`(값·단위·이름), `features`(제목·설명), `figures`(`content/figures/` 이미지·제목·출처), `toc` 의 `# ` 줄(부·장 제목), `for_whom`, `author`, `info`(추가 정보 행).
- 원본 PDF는 이 세션의 임시 폴더에서만 다룬다 (구글 드라이브 커넥터로 받기). 저장소에는 표지(`content/covers/`), 그림 미리보기(`content/figures/`), 무료 샘플(`content/samples/`)만 넣는다.
- `languages` 에 `en` 이 없으면 메뉴의 EN 버튼이 영문 안내 페이지(`/en/`)로 간다.
- 수정 후 `python3 build.py` 가 오류 없이 끝나는지 확인한다. 영어 페이지도 확인하려면 `LIMEN_LANGS=ko,en python3 build.py`.
- 사이트 운영자는 GitHub 초보다. 설명은 한국어로, 클릭 위치까지 구체적으로 안내한다.
