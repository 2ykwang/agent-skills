[English](README.md) | **한국어**

# html-visual

설명하는 대신 보여줘야 할 때 씁니다. UI 목업, ERD, 플로우차트, 데이터 차트, 프레젠테이션을 HTML 파일 한 장으로 만들고, 클릭하고 끌어볼 수 있게 합니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install html-visual@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill html-visual
```

## 언제 사용하나요

- UI 목업이나 와이어프레임이 필요할 때
- 데이터베이스 스키마를 ERD로 보고 싶을 때
- 비즈니스 로직을 플로우차트로 정리할 때
- 데이터 차트나 아키텍처 다이어그램, 대시보드를 만들 때
- 가지고 있는 내용으로 빠르게 발표 자료를 만들 때

## 지원하는 타입

`mockup`, `wireframe`, `erd`, `flow`, `chart`, `slides`, `arch`, `dashboard`, `timeline`, `mindmap`, `kanban`, `table`

## 사용법

```
# 타입을 직접 지정
/html-visual mockup 로그인 페이지
/html-visual erd schema.prisma
/html-visual chart 2024년 월별 매출

# 타입 없이 요청하면 내용을 보고 판단합니다
/html-visual 사용자 가입 플로우를 다이어그램으로

# 이미 만든 파일을 지정해 수정
/html-visual erd-orders.html 에 refunds 테이블 추가
```

## 동작 방식

1. 첫 단어에서 타입을 읽거나, 요청 내용을 보고 판단합니다. 판단이 서지 않으면 물어봅니다.
2. 입력이 있으면 먼저 읽습니다. 파일 경로를 주면 그 파일을 분석하고(Prisma 스키마라면 ERD로), 기존 HTML 파일을 주면 새로 만들지 않고 그 자리에서 고칩니다.
3. 요청이 프로젝트 사정을 알아야 하는 내용이면 코드를 먼저 읽습니다. "우리", "현재", "이 프로젝트의" 같은 말이 붙으면 실제 코드나 스키마, API를 확인한 다음에 그립니다.
4. 다크와 라이트 모드 전환, 드래그되는 노드, 화면 크기에 맞춰지는 레이아웃을 갖춘 HTML 파일 하나를 만듭니다.
5. 결과를 점검합니다. 닫히지 않은 태그, 속성에 들어간 곡선 따옴표, 서로 겹친 요소를 찾아 고칩니다.
6. 파일을 여는 명령을 알려줍니다.

## 결과물

프로젝트 루트에 HTML 파일 하나가 생깁니다. 이름은 `<타입>-<대상>.html` 형식입니다(`mockup-login-form.html`, `erd-orders.html`, `flow-payment.html`). 타입을 직접 주지 않아 추론한 경우에는 앞에 `visual-`이 붙습니다. 코드는 모두 파일 안에 들어가지만 라이브러리는 CDN에서 가져오므로, 차트와 슬라이드는 처음 열 때 네트워크가 필요합니다.
