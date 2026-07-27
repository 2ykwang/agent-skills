[English](README.md) | **한국어**

# docs

코드 문서를 쓰고 관리합니다. 코드를 그대로 붙여넣는 대신 `[symbol](file-path)` 형태로 코드를 가리키기 때문에, 구현이 바뀌어도 문서가 쉽게 낡지 않습니다.

## 설치

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install docs@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill docs
```

## 언제 사용하나요

- 방금 만든 기능을 왜 그렇게 설계했는지 남겨둘 때
- 프로젝트의 아키텍처 결정을 기록할 때
- 기존 문서가 아직 코드와 맞는지 점검할 때

## 사용법

```
# 주제를 주고 문서 작성
/docs write "auth flow design"

# 참고할 코드 경로까지 함께 지정
/docs write "payment module architecture" src/payment/

# 깨진 참조와 오래된 내용, 인덱스에 빠진 문서 전체 점검
/docs check
```

## 동작 방식

**write.** 같은 주제의 문서가 이미 있는지 먼저 찾습니다. 있으면 새로 만드는 대신 갱신할지 물어봅니다. 그다음 지정한 코드 경로나 지금 나눈 대화에서 맥락을 읽고, 이미 있는 폴더 중에서 카테고리를 고릅니다. 맞는 카테고리가 없으면 새로 만들자고 제안합니다. 문서는 `docs/generated/<카테고리>/<슬러그>.md`에 쓰고 `INDEX.md`를 갱신합니다.

**check.** 생성된 문서의 frontmatter를 모두 읽고 네 가지를 알려줍니다.

| 점검 항목 | 무엇을 잡아내나요 |
|---|---|
| 오래된 문서 | `updated`가 90일을 넘긴 문서 |
| 깨진 코드 참조 | `code_refs`에 적혀 있지만 프로젝트에 더 이상 없는 경로 |
| 깨진 문서 링크 | `related`에 적혀 있지만 실제 문서가 없는 슬러그 |
| 인덱스에 빠진 문서 | `INDEX.md`에서 링크되지 않은 문서 |

## 결과물

문서에는 frontmatter가 붙습니다. `title`, `category`, `created`, `updated`, `code_refs`, `related` 여섯 항목이고, 나중에 `check`가 이 값들을 근거로 검증합니다. 본문에는 설계 의도를 적고, 코드 조각을 붙여넣는 대신 `[symbol](file-path)` 링크로 실제 코드를 가리킵니다.

서브커맨드 없이 `/docs`만 실행하면 사용법 요약을 보여주고 멈춥니다.

## 알아두면 좋은 점

- 처음 실행할 때 `docs/generated/`와 `INDEX.md`를 만들어도 되는지 먼저 물어봅니다.
- 문서는 `docs/generated/` 아래에 카테고리별로 정리됩니다.
- `docs/generated/` 밖에 직접 쓴 문서는 절대 건드리지 않습니다.
