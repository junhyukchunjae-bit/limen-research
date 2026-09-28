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
- 수정 후 `python3 build.py` 가 오류 없이 끝나는지 확인한다. 영어 페이지도 확인하려면 `LIMEN_LANGS=ko,en python3 build.py`.
- 사이트 운영자는 GitHub 초보다. 설명은 한국어로, 클릭 위치까지 구체적으로 안내한다.
