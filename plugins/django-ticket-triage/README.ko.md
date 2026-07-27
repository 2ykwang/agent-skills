[English](README.md) | **한국어**

# django-ticket-triage

Django Trac 티켓 하나를 놓고 트리아지 판단에 필요한 것들을 모아 리포트로 만듭니다. 중복 티켓 검색, 관련 PR, 포럼 논의, 영향받는 소스 코드까지 확인합니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install django-ticket-triage@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill django-ticket-triage
```

## 언제 사용하나요

- Django 컨트리뷰터로서 티켓을 트리아지할 때
- 티켓이 유효한지, 이미 올라온 것과 겹치지 않는지, 관련 논의가 있었는지 확인할 때
- 새 티켓이든 기존 티켓이든 트리아지 리포트를 남겨야 할 때

## 사용법

```
/django-ticket-triage 36812
```

## 동작 방식

1. Trac에서 티켓 정보와 이력, 코멘트를 가져옵니다.
2. 키워드와 에러 메시지, 컴포넌트를 바꿔가며 Trac에서 중복 티켓을 찾습니다.
3. 해당 티켓을 언급한 GitHub PR을 찾습니다.
4. Django 포럼에 관련 스레드가 있는지 확인합니다.
5. 영향받는 소스 코드를 찾고 테스트가 얼마나 덮고 있는지 봅니다.
6. 버그와 기능 요청 각각의 체크리스트에 비춰 유효성을 판단합니다.
7. 트리아지 단계를 제안합니다(Unreviewed, Accepted, Ready for checkin 등).

## 결과물

전체 리포트는 `triage-reports/<ticket_id>.md`에 저장되고, 터미널에는 짧은 요약이 출력됩니다. 리포트에는 티켓 기본 정보와 중복 후보, 관련 PR과 포럼 스레드, 유효성 판단, 그리고 제안하는 트리아지 단계와 그렇게 본 이유가 담깁니다.

## 필요한 것

- `python3` (표준 라이브러리만 씁니다)
- `gh` CLI. 로그인까지 되어 있어야 합니다(`gh auth login`). 없으면 스킬이 바로 멈춥니다
- Django 소스 체크아웃(`git clone https://github.com/django/django.git`). 없어도 됩니다. 이 경우 소스 코드와 테스트를 보는 단계만 건너뛰고 나머지는 그대로 진행합니다
