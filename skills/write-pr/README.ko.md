[English](README.md) | **한국어**

# write-pr

git diff와 커밋 이력을 읽고, 프로젝트가 쓰던 방식에 맞춰 PR 제목과 본문 초안을 써줍니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install write-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill write-pr
```

## 언제 사용하나요

- PR을 올리기 직전이라 제목과 설명을 제대로 갖춰야 할 때
- 변경이 많아 손으로 요약하기 버거울 때
- PR이 프로젝트의 기존 템플릿과 제목 스타일을 따르길 바랄 때

## 사용법

```
# 기본 베이스 브랜치 기준으로(자동으로 찾습니다)
/write-pr

# 베이스 브랜치를 직접 지정
/write-pr develop
```

## 동작 방식

1. 베이스 브랜치를 찾습니다. 직접 지정한 값이 있으면 그것을 씁니다.
2. 커밋과 diff를 읽습니다. 변경이 크면(파일 20개나 변경 500줄을 넘으면) 전체를 읽지 않고, 디렉터리마다 가장 많이 바뀐 파일만 골라서 봅니다.
3. 프로젝트의 PR 템플릿을 찾습니다. `.github/PULL_REQUEST_TEMPLATE.md`를 비롯해 흔히 쓰이는 경로를 훑습니다. 구조는 그대로 두고, 채울 수 없는 항목(스크린샷, 관련 이슈)에 들어 있던 HTML 주석도 지우지 않습니다.
4. 머지된 PR 제목(`gh pr list`)에서 이 프로젝트가 쓰던 제목 방식을 파악합니다. 가져올 수 없으면 최근 커밋 메시지를 봅니다.
5. 어떤 파일이 바뀌었는지보다 왜 바꿨는지에 무게를 둡니다. 호환성을 깨는 변경이나 새로 추가된 의존성, 구조 변경은 따로 짚어줍니다.

## 결과물

붙여넣기만 하면 되는 PR 제목과 본문입니다.

- **제목.** 프로젝트가 이미 쓰던 방식을 따릅니다. 방식이 섞여 있거나 분명하지 않으면 하나 대신 후보 두세 개를 이름을 붙여 보여주고, 그마저 어려우면 Conventional Commits로 씁니다(예: `feat(auth): add OAuth2 login support`).
- **본문.** 프로젝트 템플릿을 채운 형태입니다. 템플릿을 찾지 못하면 Summary, Changes, Test Plan 구조로 씁니다.
- 마지막 줄에 베이스 브랜치와 현재 브랜치, 커밋 수, 바뀐 파일 수를 요약합니다.

## 알아두면 좋은 점

- 읽기만 합니다. PR을 만들지도, 푸시하지도 않습니다. 나온 내용을 복사해서 직접 올리면 됩니다.
