[English](README.md) | **한국어**

# commit-split

미커밋 변경을 맥락에 따라 여러 커밋으로 나눕니다. 한 파일에 두 맥락이 섞여 있으면 hunk 단위까지 나눕니다. 맥락 분류를 직접 하지 않아도 되고, 나눈 뒤에는 내용이 그대로임을 검증해서 보여줍니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install commit-split@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill commit-split
```

## 언제 사용하나요

- 기능 추가, 버그 수정, 설정 변경이 뒤섞인 채로 미커밋 변경이 쌓였을 때
- 원자적으로 커밋하고 싶지만 diff를 일일이 그룹으로 나누기는 싫을 때
- 상관없는 두 변경이 같은 파일에 들어가 있어서 서로 다른 커밋으로 보내야 할 때

이미 커밋된 히스토리를 재작성하는 작업에는 쓰지 않습니다. 맥락이 하나뿐이라 단일 커밋으로 충분한 변경에도 쓰지 않습니다.

## 사용법

```
/commit-split
```

## 동작 방식

1. **상태를 확인합니다.** 시작 시점의 HEAD와 전체 diff의 `git patch-id` 지문을 기록합니다.
2. **변경을 분석합니다.** 파일명이 아니라 diff 내용을 읽어서 논리 단위와 "한 파일에 두 맥락이 섞인" 경우를 찾습니다.
3. **계획을 제안합니다.** 레포의 커밋 컨벤션에 맞춘 메시지 초안이 담긴 표와 함께, 더 굵게/더 잘게 나눈 대안도 같이 제시합니다.
4. **확정을 받습니다.** 분할 굵기를 고르고 경계를 조정할 수 있습니다.
5. **실행합니다.** 그룹별로 스테이징하고, 파일을 쪼개야 하면 hunk 단위까지 나눕니다.
6. **검증합니다.** patch-id를 처음 기록한 지문과 비교해 내용이 하나도 달라지지 않았음을 증명합니다.

`add`와 `commit`만 실행합니다. push, reset, stash, checkout은 하지 않습니다. 문제가 생기면 자동 복구를 시도하지 않고 현재 상태를 보고한 뒤 멈추며, working tree 파일은 건드리지 않습니다.

## 필요한 것

- 미커밋 변경이 있는 git 저장소
- `python3` (hunk 단위 스테이징에 사용)
