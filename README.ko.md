[English](README.md) | **한국어**

## 설치

- **Skills CLI**: `npx skills add 2ykwang/agent-skills`
- **Plugin Marketplace**: `claude plugin marketplace add 2ykwang/agent-skills`

---

| 스킬 | |
|---|---|
| [code-history](skills/code-history/README.ko.md) | **특정 코드가 언제 들어왔고 어떻게 바뀌었는지 git 이력에서 찾아내고, 각 변경이 무엇을 노린 것이었는지 설명합니다.** |
| | `npx skills add 2ykwang/agent-skills --skill code-history` |
| | `claude plugin install code-history@2ykwang-agent-skills` |
| [code-review-report](skills/code-review-report/README.ko.md) | **코드 변경을 HTML 리포트 한 장으로 정리합니다. diff에 더해 설계 결정과 트레이드오프, 남은 작업, 우선순위를 매긴 리뷰 포인트까지 담습니다.** |
| | `npx skills add 2ykwang/agent-skills --skill code-review-report` |
| | `claude plugin install code-review-report@2ykwang-agent-skills` |
| [commit-fixup](skills/commit-fixup/README.ko.md) | **미커밋 수정사항을 각각이 속해야 할 기존 커밋에 흡수시킵니다. fixup 커밋과 autosquash rebase로 처리합니다.** |
| | `npx skills add 2ykwang/agent-skills --skill commit-fixup` |
| | `claude plugin install commit-fixup@2ykwang-agent-skills` |
| [commit-split](skills/commit-split/README.ko.md) | **미커밋 변경을 맥락에 따라 여러 커밋으로 나눕니다. 한 파일 안의 hunk 단위까지 나눌 수 있습니다.** |
| | `npx skills add 2ykwang/agent-skills --skill commit-split` |
| | `claude plugin install commit-split@2ykwang-agent-skills` |
| [create-qa-list](skills/create-qa-list/README.ko.md) | **코드나 스펙, 지금 나눈 대화를 개발자가 아닌 사람도 따라 할 수 있는 QA 테스트 케이스 목록으로 만듭니다. 코드 용어 없이 동작과 상황으로만 쓰고, CSV나 HTML로 내보냅니다.** |
| | `npx skills add 2ykwang/agent-skills --skill create-qa-list` |
| | `claude plugin install create-qa-list@2ykwang-agent-skills` |
| [decision-board](skills/decision-board/README.ko.md) | **비슷한 형태의 선택지 여러 개를 미리보기와 함께 한 화면에 띄우고 고르게 합니다. 결과는 에이전트가 바로 적용할 수 있는 JSON으로 돌아옵니다.** |
| | `npx skills add 2ykwang/agent-skills --skill decision-board` |
| | `claude plugin install decision-board@2ykwang-agent-skills` |
| [docs](skills/docs/README.ko.md) | **프로젝트 문서를 쓰고 관리합니다. `/docs write`로 문서를 만들거나 갱신하고, `/docs check`로 오래된 내용과 깨진 코드 참조, 인덱스에 빠진 문서를 찾아냅니다.** |
| | `npx skills add 2ykwang/agent-skills --skill docs` |
| | `claude plugin install docs@2ykwang-agent-skills` |
| [django-ticket-triage](skills/django-ticket-triage/README.ko.md) | **Django Trac 티켓을 살펴보고 트리아지 판단에 필요한 것들을 모아 리포트로 만듭니다.** |
| | `npx skills add 2ykwang/agent-skills --skill django-ticket-triage` |
| | `claude plugin install django-ticket-triage@2ykwang-agent-skills` |
| [html-visual](skills/html-visual/README.ko.md) | **UI 목업, ERD, 플로우차트, 데이터 차트를 HTML 파일 한 장으로 만들고 클릭하고 끌어볼 수 있게 합니다.** |
| | `npx skills add 2ykwang/agent-skills --skill html-visual` |
| | `claude plugin install html-visual@2ykwang-agent-skills` |
| [instruction-eval](skills/instruction-eval/README.ko.md) | **에이전트가 놓인 조건 하나(규칙, 참조 문서, 훅)를 바꾸고 같은 프롬프트를 변경 전후에서 돌려 실제로 뭐가 달라지는지 봅니다. 두 답변을 나란히 놓은 HTML 리포트가 나옵니다. Claude Code 기반입니다.** |
| | `npx skills add 2ykwang/agent-skills --skill instruction-eval` |
| | `claude plugin install instruction-eval@2ykwang-agent-skills` |
| [ralph-loop-template](skills/ralph-loop-template/README.ko.md) | **계획 파일에서 Ralph Loop이 한 번에 한 단계씩 처리할 체크리스트를 뽑아냅니다. `/ralph-loop`에 바로 넣을 수 있는 `PROMPT-*.md` 파일이 나옵니다.** |
| | `npx skills add 2ykwang/agent-skills --skill ralph-loop-template` |
| | `claude plugin install ralph-loop-template@2ykwang-agent-skills` |
| [quick-pr](skills/quick-pr/README.ko.md) | **작업하던 중 발견한 사소한 수정만 떼어내 별도 worktree에서 PR로 만듭니다. 지금 브랜치를 벗어나지 않습니다. Claude Code가 필요합니다.** |
| | `npx skills add 2ykwang/agent-skills --skill quick-pr` |
| | `claude plugin install quick-pr@2ykwang-agent-skills` |
| [worth-building](skills/worth-building/README.ko.md) | **무엇을 어느 수준까지 만들지 정해줍니다. 간단하게 끝낼지 제대로 갖출지 판단하고, 과하지도 부족하지도 않은 크기의 PoC 제안을 돌려줍니다.** |
| | `npx skills add 2ykwang/agent-skills --skill worth-building` |
| | `claude plugin install worth-building@2ykwang-agent-skills` |
| [write-pr](skills/write-pr/README.ko.md) | **git diff와 커밋 이력을 읽고, 프로젝트가 쓰던 방식에 맞춰 PR 제목과 본문 초안을 써줍니다.** |
| | `npx skills add 2ykwang/agent-skills --skill write-pr` |
| | `claude plugin install write-pr@2ykwang-agent-skills` |

---
