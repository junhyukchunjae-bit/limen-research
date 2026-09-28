# LIMEN RESEARCH 사이트 작업 안내

- `build.py` 가 `content/` 를 읽어 `_site/` 에 정적 사이트를 만든다. 외부 패키지 없이 Python 3.11+ 표준 라이브러리만 쓴다.
- 보고서 추가: `content/reports/YYYY-MM-DD-slug.toml`. 기존 파일 형식을 따르고, `issue` 는 이전 호 +1, `sectors` 는 `content/site.toml` 의 key 만 쓴다.
- `content/samples/` 에는 무료 샘플만 둔다. 유료 보고서 원본 PDF는 절대 커밋하지 않는다 (공개 저장소).
- 결제 링크: 해외(Lemon Squeezy) `pay_global`, 국내(페이앱·토스페이먼츠 등) `pay_korea`. 국내 링크가 없으면 구매 신청(신청서 또는 이메일)으로 연결된다.
- 수정 후 `python3 build.py` 가 오류 없이 끝나는지 확인한다. 영어 페이지도 확인하려면 `LIMEN_LANGS=ko,en python3 build.py`.
- 사이트 운영자는 GitHub 초보다. 설명은 한국어로, 클릭 위치까지 구체적으로 안내한다.
