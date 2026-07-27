[English](README.md) | **한국어**

# commit-fixup

미커밋 수정사항을 각각이 속해야 할 기존 커밋에 흡수시킵니다. fixup 커밋과 autosquash rebase로 처리하되, 어느 수정이 어느 커밋으로 갈지 매핑 표로 먼저 확인받고, 백업 브랜치를 남겨 언제든 되돌릴 수 있게 합니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install commit-fixup@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill commit-fixup
```

## 언제 사용하나요

- 리뷰 반영으로 생긴 수정들이 각각 브랜치의 이전 커밋에 들어가야 할 때
- 나중에 다듬은 내용이 이미 만든 커밋 여러 개에 흩어져 있을 때
- PR을 올리기 전에 히스토리를 정리하고 싶지만 interactive rebase를 직접 몰고 가긴 싫을 때

이미 커밋된 것들의 순서를 바꾸거나 기존 커밋 하나를 쪼개는 작업에는 쓰지 않습니다.

## 사용법

```
/commit-fixup
```

## 동작 방식

1. **안전을 확인합니다.** 이미 push된 브랜치, 범위 안의 merge 커밋, 2.44 미만 git이면 멈춥니다.
2. **매핑합니다.** 수정된 파일마다 브랜치 안에서 그 파일을 마지막으로 만진 커밋을 찾습니다. 이 규칙 덕분에 rebase가 충돌 없이 끝납니다.
3. **확인받습니다.** 매핑 표를 보여주고 동의를 받은 뒤에야 히스토리를 건드립니다. 어느 커밋에도 매핑되지 않은 파일은 따로 처리를 물어봅니다.
4. **실행합니다.** 대상 커밋별로 fixup 커밋을 만들고, 백업 브랜치를 남긴 뒤 `git rebase --autosquash`를 돌립니다.
5. **검증합니다.** 백업과 HEAD의 diff가 비어 있는지, `fixup!` 커밋이 남지 않았는지 확인하고, 테스트 스위트가 있으면 돌립니다.

force-push는 하지 않습니다. rebase 도중 충돌이 나면 매핑이 틀렸다는 신호이므로, 즉시 abort하고 보고합니다.

## 필요한 것

- Git 2.44 이상 (비대화식 `rebase --autosquash`)
- base보다 앞선 커밋이 있는 브랜치
