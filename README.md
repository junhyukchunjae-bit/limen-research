# LIMEN RESEARCH 웹사이트

매주 발행하는 테크 산업 보고서(PDF)를 소개하고 판매하는 사이트입니다.
회원가입 없이 비회원 결제만 받으며, 운영비는 월 0원을 목표로 합니다.

- 호스팅: GitHub Pages (무료)
- 국내 결제: 페이앱·토스페이먼츠 등 결제 링크, 또는 구매 신청 후 계좌이체
- 해외 결제: Lemon Squeezy (해외 카드·PayPal, 결제 즉시 PDF 자동 발송, 해외 세금 대행)

> ⚠️ **유료 보고서 원본 PDF는 이 저장소에 절대 올리지 마세요.**
> 저장소와 사이트는 누구나 볼 수 있습니다. 원본은 Lemon Squeezy에만 올리고,
> 국내 결제 건은 메일로 직접 보냅니다. 저장소에는 **무료 샘플만** 둡니다.

## 폴더 구조

```
content/
  site.toml          사이트 설정 (이메일, 문구, 분야, 국내 결제, 사업자 정보)
  reports/           보고서 1편 = 파일 1개 (.toml). 파일 이름이 주소가 됩니다
  samples/           무료 샘플 PDF
  pages/             소개·이용약관·환불정책·개인정보처리방침 (.ko.md / .en.md)
static/              디자인(CSS), 스크립트, 아이콘
build.py             content/ 를 읽어 _site/ 에 사이트를 만드는 프로그램
.github/workflows/   main 에 올라오면 자동으로 사이트를 만들어 배포
```

## 처음 한 번 할 일

1. **저장소 공개 전환**: 무료 GitHub Pages는 공개 저장소에서만 됩니다.
   Settings → General → 맨 아래 Danger Zone → Change visibility → Public
2. **Pages 켜기**: Settings → Pages → Build and deployment → Source 를 **GitHub Actions** 로 선택
3. **main 에 합치기**: 작업 브랜치를 main 에 합치면 몇 분 뒤
   `https://junhyukchunjae-bit.github.io/claude-test/` 에 사이트가 열립니다.
4. **이메일 바꾸기**: `content/site.toml` 의 `email` 을 실제 주소로
5. **예시 보고서 정리**: `content/reports/` 의 예시 3편(`example = true`)을 지우거나 `draft = true`

## 결제 연결

| | 어디서 | 보고서 파일에 넣을 곳 |
|---|---|---|
| 해외 결제 | Lemon Squeezy에서 상품(PDF) 등록 → Share → 결제 링크 복사 | `pay_global` |
| 국내 결제 | 페이앱·토스페이먼츠 등에서 만든 결제 링크 | `pay_korea` |

- `pay_korea` 를 비워 두면 한국어 화면의 버튼이 **국내 구매 신청**으로 바뀝니다.
  `site.toml` 의 `order_form_url` 에 구글 폼 주소를 넣으면 신청서로, 없으면 이메일 신청으로 연결됩니다.
- 국내 결제는 PDF 자동 발송이 없습니다. 결제(입금) 알림을 받으면 신청서의 이메일로 PDF를 보내 주세요.
  사이트에는 "영업일 24시간 이내 발송"으로 안내되어 있습니다.

## 매주 보고서 올리기

Claude에게 이렇게 부탁하면 됩니다.

> 이번 주 보고서 올려줘. 제목 ○○, 분야 모빌리티, 48쪽, 가격 30만원 / 220달러,
> 요약·목차는 첨부 참고. 샘플 PDF 첨부. 해외 결제 링크 https://...

직접 할 때는 `content/reports/` 의 파일 하나를 복사해 `2026-10-05-주제.toml` 처럼 이름을 바꾸고 내용을 고친 뒤 main 에 올리면 됩니다.

## 나중에

- **영어 사이트 열기**: `site.toml` 에서 `languages = ["ko", "en"]`. 각 보고서에 `[en]` 부분이 있으면 `/en/` 에 영어 페이지가 생깁니다.
- **도메인 연결**: 도메인 구입 후 `site.toml` 의 `site_url` 을 바꾸고 Settings → Pages → Custom domain 에 입력
- **사업자 정보**: 사업자등록·통신판매업 신고 후 `site.toml` 의 `[business]` 를 채우면 하단에 표시됩니다.
- **약관 3종**은 초안입니다. 판매 시작 전에 한 번 검토하세요.

## 내 컴퓨터에서 미리 보기 (선택)

```
python3 build.py                  # _site/ 생성
python3 -m http.server -d _site   # http://localhost:8000 에서 확인
LIMEN_LANGS=ko,en python3 build.py   # 영어까지 켜서 미리 보기
```
