[English](README.md) | **한국어**

# ralph-loop-template

구현 계획을 [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)이 한 번에 한 단계씩 처리할 수 있는 체크리스트 PROMPT 파일로 바꿔줍니다. 계획 파일을 주거나, 지금 나눈 대화를 그대로 재료로 쓸 수 있습니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install ralph-loop-template@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill ralph-loop-template
```

## 언제 사용하나요

- 구현 계획이 있고, 이를 단계별로 검증해가며 자동으로 진행시키고 싶을 때
- 큰 작업을 Ralph Loop이 소화할 만한 크기로 쪼개야 할 때
- 플래그까지 채워진 `/ralph-loop` 실행 명령을 바로 받고 싶을 때

## 사용법

```
# 계획 파일을 지정해서
/ralph-loop-template PLAN.md

# 계획 파일을 알아서 찾거나(PLAN.md, TODO.md 등) 지금 대화를 사용
/ralph-loop-template
```

## 동작 방식

1. 먼저 계획을 찾습니다. 인자로 준 파일, 프로젝트에 있는 계획 파일(`PLAN.md`, `TODO.md`, `PRD.md` 등), 또는 지금 나눈 대화 순으로 봅니다.
2. `CLAUDE.md`나 `.cursorrules`, `AGENTS.md`, 빌드 파일에서 프로젝트의 빌드와 테스트, 린트 명령을 찾아 하나의 검증 명령으로 엮습니다.
3. 목표와 하지 않을 일, 단계를 뽑아냅니다. 하지 않을 일이 특히 중요합니다. 루프가 시키지도 않은 작업을 만들어내는 걸 막는 장치이기 때문에, 계획에 적힌 것 외에 범위 밖 리팩터링이나 요청하지 않은 테스트와 문서 수정 같은 항목을 추론해서 덧붙입니다.
4. 계획을 한 번의 반복에 들어갈 크기로 쪼갭니다. 한 반복은 정확히 한 단계만 처리하고, 각 단계는 그 자체로 검증을 통과할 수 있을 만큼 작아야 합니다.
5. `PROMPT-<이름>.md` 파일과 복사해서 바로 쓸 수 있는 `/ralph-loop` 명령을 만듭니다. `--max-iterations`는 단계 수에 2를 더한 값입니다. 하나는 검증에 실패했을 때 다시 시도할 몫이고, 하나는 마지막에 완료를 알리는 몫입니다.

## 결과물

```
### Generated File
`PROMPT-auth-refactor.md`

### Ralph Loop Execution Command
/ralph-loop "Read PROMPT-auth-refactor.md and implement the next unchecked phase." --max-iterations 7 --completion-promise "AUTH REFACTOR DONE"
```

실행하기 전에 만들어진 PROMPT 파일을 한 번 읽어보는 편이 좋습니다. 특히 검증 명령과 단계를 나눈 방식 두 가지가 그렇습니다. 루프는 매 반복마다 이 파일을 그대로 다시 읽기 때문에, 검증 명령이 틀리면 모든 반복에서 틀립니다.

## 필요한 것

- [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) 플러그인. `/ralph-loop` 명령을 제공합니다

## 알아두면 좋은 점

- 직접 호출해야 합니다. 이 저장소의 다른 스킬과 달리 모델이 알아서 실행하지 않습니다.
- 완료 기준은 기계가 판정할 수 있어야 합니다. 즉 종료 코드 0을 내는 명령이어야 합니다. "잘 동작한다", "깔끔해 보인다" 같은 기준은 쓸 수 없습니다.
