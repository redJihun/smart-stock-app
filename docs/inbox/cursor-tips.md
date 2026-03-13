- 원문 : https://www.stdy.blog/12-tips-for-smarter-cursor-usage/
- 긱뉴스 : https://news.hada.io/topic?id=21608

---

▲

**Cursor를 더 똑똑하게 사용하고 싶은 분들을 위한 팁 12개 (stdy.blog)**

99P by [spilist2](https://news.hada.io/user?id=spilist2) 8달전 | ★ favorite | [댓글 22개](https://news.hada.io/topic?id=21608)

6/23 기준이고, 제 경험 + 커서 레딧 + 커서 커뮤니티 + SNS + 여러 블로그 글들을 조합해 만들었습니다. 반박, 비판, 토론 환영합니다.

---

### 팁 1. 전략적으로 [모델을 선택](https://docs.cursor.com/guides/selecting-models?ref=stdy.blog)하자

- 모델마다 코딩 능력, 속도, 비용이 다르므로 상황에 맞게 선택하는 것이 중요함.
- Thinking 모델(Claude 4, Gemini 2.5 Pro 등)은 자율적이지만 속도가 느림.
- Non-Thinking 모델(GPT 4.1 등)은 명확한 지시를 잘 따르고 속도가 빠름.
- 작업 종류에 따라 추천 모델이 다름 (예: 단순 변경은 Sonnet, 복잡한 계획은 Opus).
- 'Auto-select' 기능은 신뢰도가 낮으므로, 여러 모델을 직접 써보고 자신만의 스타일을 찾는 것이 좋음.

### 팁 2. 복잡한 앱을 수정할 때는 먼저 [Ask 모드](https://docs.cursor.com/chat/ask?ref=stdy.blog)로 계획을 짜자

- Agent 모드는 코드를 직접 수정하므로 복잡한 앱에서는 기존 기능을 망가뜨릴 가능성이 있음.
- Ask 모드는 파일을 수정하지 않는 읽기 전용 모드로, 계획을 세울 때 매우 유용함.
- 먼저 Ask 모드에서 AI와 계획을 논의한 후, Agent 모드에서 실행하는 것이 안전함.
- "지금 당장 수정하지 마"처럼 프롬프트를 명확히 하면 Ask 모드의 불필요한 동작을 줄일 수 있음.
- Manual 모드는 참조할 파일을 직접 지정해야 해서 활용도가 낮은 편임.

### 팁 3. 디버깅할 때 바로 파일을 수정하게 하지 말고 테스트와 함께 원인을 파악하자

- AI에게 바로 버그 수정을 맡기면 반복적인 실패를 겪기 쉬움.
- 1단계 (Agent): 버그를 재현하는 '실패하는' 테스트 코드를 먼저 작성하게 함 (TDD 방식).
    - "X 페이지에서 Y를 누르면 A처럼 동작해야 하는데 B처럼 동작해. TDD 방식으로 고쳐보려고 하는데, 이 현상을 재현하는 테스트 코드를 작성해서 실행해줘. 현 시점에 테스트 코드는 일단 실패해야 한다는 걸 기억해. 내가 틀렸을 수도 있으니 재현이 안되면 알려주고. 내 명령 없이 문제를 고치기 시작하지 마."
- 2단계 (Ask): 가능한 원인과 확인 방법을 설명하게 하여 근본 원인을 파악함.
    - "버그의 근본 원인을 파악하려고 해. 이 현상이 왜, 어떨 때 일어나는지 가능한 옵션들을 제시해줘. 그리고 그 옵션들 중 무엇이 맞는지 확인하기 위한 방법도 같이 얘기해줘. 어떤 정보가 더 필요한지, 어떤 걸 로그로 찍어봐야 하는지 등. 그 방법을 실행할 필요는 없고 설명만 해줘. 만약 테스트 코드를 작성하면서 이미 원인이 파악됐다면 그걸 설명해줘."
- 3단계 (Agent): 테스트 코드는 `.cursorignore`로 잠근 뒤, 테스트가 통과될 때까지 코드 수정을 지시함.
    - "아까 만들어진 테스트 코드는 .cursorignore에 추가해줘. 그다음 네가 제시한대로 가능성 높은 것부터 근본 원인을 파악해가면서, 이상적인 작동 흐름을 플로우차트로 정리해줘. 그리고 그 이상적인 흐름을 활용해서 테스트 코드가 통과될 때까지 코드를 수정해줘. 내가 확인하거나 개입해야 할 게 있으면 알려주고."
- [테스트 코드 작성에 대한 룰](https://gist.github.com/greatSumini/4dd29297f9b41769a0252c34836c9ca5?ref=stdy.blog)도 만들어두면 좋음

### 팁 4. Cursor가 스스로 룰을 관리해서 점점 더 똑똑해지게 하자

- 채팅 세션에서 유의미한 대화가 오갔다면, [/Generate Cursor Rules](https://docs.cursor.com/context/rules?ref=stdy.blog#generating-rules) 기능을 활용할 수 있음.
- "이번 대화 내용을 기반으로 Rule을 만들거나 수정해줘"라고 요청하면 됨.
- 특히 디버깅 후, 버그의 원인을 파악했다면 같은 실수를 반복하지 않도록 Rule을 추가/수정하게 하면 유용함.
- 이를 통해 Cursor가 스스로 학습하고 유지보수하며 점점 더 똑똑해지게 만들 수 있음.

### 팁 5. [다중 탭](https://docs.cursor.com/chat/overview?ref=stdy.blog#tabs)과 Auto 옵션들을 이용해 생산성을 높이자

- Cursor에서는 여러 채팅 탭을 동시에 사용 가능. 한 탭에서 Agent가 코드를 수정하는 동안 다른 탭에서 Ask 모드로 다른 작업을 할 수 있음.
- 'Auto-run' 옵션을 켜두면 터미널 실행이나 파일 쓰기 등을 일일이 승인할 필요 없이 자동으로 진행함.
- 'Auto-Fix Lints' 옵션을 켜두면 타입 에러 등을 알아서 수정해줘서 편리함.

### 팁 6. 하나의 채팅 세션을 오래 지속하지 말자

- 채팅이 길어지면 컨텍스트 크기 한계로 인해 AI가 이전의 중요 정보를 잊어버릴 수 있음. (Cursor가 [자동으로 요약](https://docs.cursor.com/context/management?ref=stdy.blog#summarization)해버림)
- 하나의 작업이 끝나면 새 채팅 세션을 시작하는 것이 더 유리함.
- 새 채팅에서 `@Past Chats`를 이용해 이전 대화 요약을 컨텍스트로 주입할 수 있음.
- 유의미한 내용은 룰로 만들어두면(팁 4) 긴 채팅을 유지할 필요성이 줄어듦.

### 팁 7. 유의미한 변경이 완료되면 반드시 커밋하자

- 하나의 작업이 끝나면 반드시 Git에 커밋하는 습관이 중요함.
- 커밋은 AI가 코드를 잘못 수정했을 때 돌아갈 수 있는 최소한의 안전장치가 됨.
- Cursor 채팅을 통해 Git 초기 설정부터 커밋 메시지 작성까지 도움을 받을 수 있음.
    - "이 코드베이스를 GitHub에 업로드하고 싶어. 문제는 내가 Git과 GitHub에 대해 하나도 모르고 계정도 없어. Git이 설치되어있는지도 모르겠어. 스텝바이스텝으로 도와줘."
- AI Commit Message 기능을 사용하면 커밋 메시지를 자동으로 생성할 수도 있음.

### 팁 8. Cursor에게 코드 구조를 알려주고, 파일 길이와 파일명을 조절하자

- Cursor의 내부 Tools의 특성을 이해해두면 좋음
    - `List Directory`는 파일의 내용은 읽지 않고 디렉토리명과 파일명만 읽음
    - `Read File`은 파일의 내용을 한번에 최대 250줄까지만 읽음 (Max 모드에서는 750줄)
    - 참조한 파일이나 디렉토리의 크기가 너무 크면 전체가 들어가는 대신 함수 호출부와 같이 중요한 부분만 남고 압축됨
    - 한 채팅 세션에서 Tool 호출을 25번까지만 할 수 있고, 더 하려면 Continue 를 직접 눌러야 함 (Auto apply edit 옵션이 켜져 있어도 마찬가지. Max 모드에서는 Continue 없이 200번까지 가능)
- 따라서 역할이 명확하도록 파일과 디렉토리 이름을 짓고, 파일 길이는 500줄 이내로 유지하는 것이 좋음.
- 핵심 디렉토리 구조나 컴포넌트 정보는 `Always Applied` 룰로 추가해두면 AI가 매번 탐색할 필요가 없음.
- AI가 코드 구조를 파악할 수 있도록 문서를 만들어 룰로 추가해달라고 요청할 수 있음.
    - "이 코드베이스의 구조 및 중요 파일들을 네가 한눈에 파악할 수 있는 문서를 만들어줘. mermaid diagram을 쓰는 것도 좋아. 그리고 그걸 적절한 프로젝트 룰로 추가해줘. AlwaysApply: true로 만들어줘."

### 팁 9. 파일이 길어지면 Cursor가 모듈화하게 하자

- 파일이 너무 길어지면 AI에게 모듈화를 요청하는 것이 좋음.
- 1단계 (Ask): "이 프로젝트를 모듈화한다면 어떤 관점이나 전략에서 하는 게 좋을지 제안해줘. 예를 들면: 1) Layered Architecture 관점 2) AOP 관점 3) FSD 관점 4) 클린 아키텍처 관점"
- 2단계 (Ask): "네가 제시한 전략들을 종합하여 적절한 모듈화 계획을 세워줘."
- 3단계 (Agent): "그 계획을 문서화한 뒤 실행해줘."

### 팁 10. [@을 써서](https://docs.cursor.com/context/@-symbols/overview) 적극적으로 컨텍스트를 주입하자

- `@` 기호를 사용해 파일, 폴더 외에 다양한 컨텍스트를 직접 주입하면 AI가 더 일을 잘함.
- `@Code`: 코드의 특정 함수나 변수 등 일부만 참조할 수 있음.
- `@Docs`: 라이브러리 공식 문서를 참조하여 더 정확한 코드를 작성하게 함. Cursor가 이미 들고있는 docs도 있고 직접 URL을 통해 추가도 가능
- `@Git`: 특정 브랜치나 커밋 내용을 참조하게 하여 비교하거나 설명시킬 수 있음.
- `@Web`, `@Link`: 웹 검색을 하거나 특정 링크의 내용을 읽어오게 할 수 있음.
- `@Recent Change`: 최근 코드베이스 변경사항을 참조시킬 수 있음. 정확한 동작 방식은 찾지 못했으나 unstaged changes와 최근 커밋을 토대로 하는 걸로 보임. 커밋 관리를 빡세게 하지 않는 비개발자에게 유용할듯

### 팁 11. 보안이 중요하다면 Privacy 모드를 켜자

- Privacy 모드를 켜지 않으면 코드, 프롬프트 등 데이터가 수집되어 모델 학습에 사용될 수 있음.
- Privacy 모드를 켜면 코드 일부가 암호화되어 잠시 저장될 수는 있지만, 영구 저장되거나 학습에 사용되지 않음.
- 단, Privacy 모드에서는 백그라운드 에이전트 등 일부 최신 기능을 사용할 수 없음.
- 자세한 내용은 Cursor가 프라이버시 모드에 대해 설명하는 [문서](https://www.cursor.com/privacy-overview)를 참조

### 팁 12. 개발을 편하고 정확하게 만들어주는 MCP와 도구들을 사용하자

- 태스크 관리 측면에서는 메모리 뱅크, [TaskMaster](https://www.task-master.dev/), [Vooster](https://www.vooster.ai/) 추천
- Cursor [공식문서의 MCP](https://docs.cursor.com/tools)들은 딥링크로 한번에 설치 가능
    - Browserbase로 브라우저 실행, 클릭, 콘솔 읽기, 스크린샷 찍기 등
    - PlayWright로 E2E 테스트 추가하기
    - Sentry로 에러 모니터링하고 수정하기
    - Stripe와 Paypal로 결제하기
    - Netlify와 Heroku로 배포하기
    - Snyk와 Semgrep으로 보안 검사하기
    - Supabase로 DB 테이블 읽고 쓰기 → Cursor 공식 문서에는 나오지 않은 녀석이지만 바이브 코더라면 필수 설치라고 생각
- 회사 내에서 작업하는데, 회사의 상황이나 여러 제품에 대한 컨텍스트를 잘 알려줘야 한다면 직접 MCP를 개발해보는 것도 좋음. (참고: [Working with Documentation](https://docs.cursor.com/guides/advanced/working-with-documentation))
- [StageWise](https://stagewise.io/)와 같은 외부 도구를 활용해 UI의 특정 부분을 집어 버그 수정 등을 요청할 수도 있음.

### 그 외 자잘한 팁

- **Max 모드**: 요청이 아닌 토큰 기반 과금이며, 더 큰 컨텍스트와 더 많은 Tool 사용이 가능함.
- **모델 추가**: 설정에서 Claude 4 Opus 등 기본으로 숨겨진 모델을 활성화할 수 있음.
- **Custom API Key**: 자신의 LLM API 키를 연동하는 기능. 활용도는 낮은 편. 참고로 이걸 하더라도 Cursor 서버는 무조건 거쳐감
- **설정 동기화**: 여러 PC 간 설정 동기화는 아직 공식적으로 잘 지원되지 않음. Profile Export/Import는 잘 안 된다고 보고되고 있고, 몇주 전 [확장 프로그램](https://github.com/0x3at/synceverything)이 하나 나왔지만 6/23 현재 몇 가지 문제가 있음
    - [VSCode 마켓플레이스에는 뜨지만](https://marketplace.visualstudio.com/items?itemName=DunderDev.sync-everything) Cursor의 Extension 목록에서는 검색되지 않음
    - VSCode에서 설치한 뒤 Cursor의 `Import VSCode Settings and Extensions` 기능을 이용해 가져오는 건 가능. 그런데 실제로 확장 프로그램이 제대로 초기화되지 않음 ([관련 이슈](https://github.com/0x3at/synceverything/issues/4))
    - 괜찮아 보여서 개발자가 빨리 고쳐주길 기대

▲

[elddytbt](https://news.hada.io/user?id=elddytbt) [8달전](https://news.hada.io/comment?id=40601)  [-]

팁4, 팁6 좋습니다~~

궁금한게 있는데, 저는 한달 500개가 터무니없이 적던데 이 문제는 어떻게 해결하시나요?

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40606)  [-]

최근 제한이 없어지지 않았나요?

저는 클로드 코드를 같이 쓰고 있기도 하고, 주로 AI Studio에서 논의를 충분히 마친 채로 정제된 요청을 하려고 노력 + 룰 세팅 + 필요시 탭 자동완성으로 직접 구현 등등 때문인지 부족하다고 느낀 적은 별로 없네요.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[fanotify](https://news.hada.io/user?id=fanotify) [8달전](https://news.hada.io/comment?id=40566)  [-]

기본적으로 유료 구독을 해야 저 기능들을 사용할 수 있을까요? 아니면 사용량이 적다면 무료 기본 회원도 따라할 수 있을까요?

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40567)  [-]

제 경험상으로는 커서가 무료 플랜 기능과 제공량이 상당히 박해서 무료로는 사용하기 쉽지 않으실 것 같습니다.

공짜로 쓸 수 있는 모델들이 있지만 그만큼 코딩도 잘 못해서요.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[eususu](https://news.hada.io/user?id=eususu) [8달전](https://news.hada.io/comment?id=40561)  [-]

팁 너무 좋습니다.

감사합니다!

[답변달기](https://news.hada.io/topic?id=21608)

▲

[dnltmdwhd](https://news.hada.io/user?id=dnltmdwhd) [8달전](https://news.hada.io/comment?id=40540)  [-]

몇 가지 모르고 있었던 유용한 내용도 많네요~ 감사합니다!

[답변달기](https://news.hada.io/topic?id=21608)

▲

[jk34011](https://news.hada.io/user?id=jk34011) [8달전](https://news.hada.io/comment?id=40537)  [-]

좋은 팁 감사합니다~ 많이 배워갑니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[dkmin](https://news.hada.io/user?id=dkmin) [8달전](https://news.hada.io/comment?id=40535)  [-]

알찬 내용 공유 감사합니다. =b

"단, Privacy 모드에서는 백그라운드 에이전트 등 일부 최신 기능을 사용할 수 없음."

=> 구체적인 내용이 궁금합니다. 출처를 좀..

ref.

https://docs.cursor.com/background-agent

Background Agents are available in Privacy Mode. We will never train on your code, and we will only retain code for the purposes of running the agent. Learn more about Privacy mode

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40536)  [-]

앗 얼마 전까지만 해도 사용 불가였는데 바뀌었군요!! 감사합니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[baeba](https://news.hada.io/user?id=baeba) [8달전](https://news.hada.io/comment?id=40521)  [-]

저의 경우는

AI가 소스코드를 변경하기 전에 또는 prompt 질문을 하기 전에

소스코드를 통째로 로컬에 백업합니다.

./history/ 아래에

./hisrory/r0001/

./hisrory/r0002/ ...

이런 구조로 된 디렉토리를 생성하고 개발소스들을 백업하는 스크립트를 실행해요..

윈도우즈 개발 환경이라서 ps1 파일 입니다.

```bash
# backup.ps1
$base = "./src"
$history = "./history"

# 최신 rXXXX 폴더 찾기
$latest = Get-ChildItem -Path $history -Directory | Where-Object { $_.Name -match '^r\d{4}$' } | Sort-Object Name -Descending | Select-Object -First 1
if ($latest) {
    $num = [int]($latest.Name.Substring(1)) + 1
} else {
    $num = 1
}
$next = "r{0:D4}" -f $num
$dest = "$history/$next"

# 백업 폴더 생성
New-Item -ItemType Directory -Path "$dest" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/css" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/js" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/html" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/images" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/doc" -Force | Out-Null
New-Item -ItemType Directory -Path "$dest/server" -Force | Out-Null

# 파일/폴더 복사
Copy-Item "$base/SPA_index.html" "$dest/SPA_index.html"
Copy-Item "$base/css/*" "$dest/css/" -Recurse
Copy-Item "$base/js/*" "$dest/js/" -Recurse
Copy-Item "$base/images/*" "$dest/images/" -Recurse
Copy-Item "$base/doc/*" "$dest/doc/" -Recurse

# 서버 파일 복사: node_modules 제외
Copy-Item "$base/server/*" "$dest/server/" -Recurse -Exclude "node_modules"

Write-Host "백업 완료: $dest"
```

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40523)  [-]

깃을 쓰는 것과 이 방법에 어떤 장단점이 있을까요?

[답변달기](https://news.hada.io/topic?id=21608)

▲

[baeba](https://news.hada.io/user?id=baeba) [8달전](https://news.hada.io/comment?id=40543)  [-]

깃도 동시에 사용해요..

실질적으로 개발할때 AI가 소스코드를 변경을 많이 할 수 있기 때문에..

이것을 일일이 꼼꼼하게 Check하더라도 빌드했을때 오류 또는 버그가 발생할 수 있기

때문에..

이전 코드로 rollback 할때 편해요.

깃으로 코드를 rollback할 수도 있겠지만..

전체 코드가 전체 백업 되어 있어서

빨리 찾아서 코드 변경된 거 보면서 구현하는데 도움이 되었습니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[turastory](https://news.hada.io/user?id=turastory) [8달전](https://news.hada.io/comment?id=40604)  [-]

git subtree를 활용하시면 좋을 것 같네요.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[lux1024](https://news.hada.io/user?id=lux1024) [8달전](https://news.hada.io/comment?id=40607)  [-]

git worktree?

[답변달기](https://news.hada.io/topic?id=21608)

▲

[turastory](https://news.hada.io/user?id=turastory) [8달전](https://news.hada.io/comment?id=40639)  [-]

아 이름을 헷갈렸네요 ㅎㅎ worktree가 맞습니다

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40569)  [-]

답변 감사합니다!

[답변달기](https://news.hada.io/topic?id=21608)

▲

[joyoo](https://news.hada.io/user?id=joyoo) [8달전](https://news.hada.io/comment?id=40584)  [-]

아무런 장점이 없죠.. 저런 행위를 안하려고 나온게 버전 관리 시스템입니다.

제가 볼때는 git을 더 공부하시는게 좋아 보입니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[nakyup](https://news.hada.io/user?id=nakyup) [8달전](https://news.hada.io/comment?id=40520)  [-]

context7 이라는 mcp가 유용해서 라이브러리 사용법 물어볼때 자주 사용합니다

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40527)  [-]

아 이거 소개 깜빡했던 게 떠올라서 강의자료는 업데이트했는데 블로그 업데이트는 안했네요. 덕분에 추가했습니다. 감사합니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[aqqnucs](https://news.hada.io/user?id=aqqnucs) [8달전](https://news.hada.io/comment?id=40517)  [-]

팁 2 질문. ask 모드인데도 수정하지 말라고 일러주지 않으면 수정을 시도하나요?

[답변달기](https://news.hada.io/topic?id=21608)

▲

[spilist2](https://news.hada.io/user?id=spilist2) [8달전](https://news.hada.io/comment?id=40519)  [-]

넵 수정 시도하다가 타임아웃 지나서 edit_files 안되네? 하면서 다른 일 하는 경우가 있습니다.

[답변달기](https://news.hada.io/topic?id=21608)

▲

[kissdesty](https://news.hada.io/user?id=kissdesty) [8달전](https://news.hada.io/comment?id=40518)  [-]

실제 수정을 하진 않더라도, Ask 모드에서도 수정 직전까지 하는 불필요한 예비 행동을 줄여준다는 의미 같습니다.