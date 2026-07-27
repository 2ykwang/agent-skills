[English](README.md) | **한국어**

# quick-pr

작업하던 변경에서 사소한 수정 하나만 떼어내 별도 worktree로 옮기고 PR을 엽니다. 지금 브랜치를 벗어나지 않아도 되고, stash하고 checkout하고 브랜치 만들고 push하는 과정을 거치지 않아도 됩니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install quick-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill quick-pr
```

## 언제 사용하나요

- 기능 작업 도중 상관없는 작은 수정을 발견했을 때(오타, 낡은 설정, 빠진 린트 규칙)
- 지금 브랜치 작업을 끊지 않고 그 수정만 따로 내보내고 싶을 때

## 사용법

```
# 특정 파일에 이미 들어간 수정에서 떼어내기
/quick-pr .eslintrc.json

# 무엇을 고칠지 설명해서
/quick-pr "CI 설정의 Node 버전을 18에서 20으로 올려줘"

# 맥락을 보고 알아서 판단하게 두기
/quick-pr
```

## 동작 방식

1. **무엇을 떼어낼지 정합니다.** 파일에 이미 들어간 수정을 옮길지, 설명대로 새로 고칠지 결정합니다.
2. **브랜치 이름과 커밋 메시지를 고릅니다.** 프로젝트의 기존 스타일에 맞춘 후보를 보여주고 그중에서 고르게 합니다.
3. **worktree를 만듭니다.** 고른 베이스 브랜치를 기준으로, 지금 브랜치와 분리된 작업 공간이 생깁니다.
4. **반영하고 PR을 엽니다.** 커밋하고 푸시한 뒤 프로젝트 템플릿에 맞춰 PR을 만듭니다.
5. **정리합니다.** PR을 확인한 다음 worktree를 지울지 물어봅니다.

모든 단계에서 확인을 거칩니다. 승인 없이 푸시하는 일은 없습니다.

## 필요한 것

- Claude Code (`EnterWorktree`, `ExitWorktree`, `AskUserQuestion`을 씁니다)
- `gh` CLI
- 원격이 연결된 git 저장소
