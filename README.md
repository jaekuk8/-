# quick-band

Claude Code 채팅창 위 띠에 자주 쓰는 버튼(압축, 컨텍스트, 핸드오프, 세션저장)을 표시하는 모드입니다.

## 설치

PowerShell에서 `claude`를 실행한 뒤 아래를 입력합니다. (관리자 권한 불필요)

```
/plugin install quick-band --marketplace jaekuk8/-
```

`Add marketplace?`에 `y`, 설치 범위는 맨 위 사용자 범위(user)를 Enter로 고릅니다.

## 버튼 바꾸기

`quick-band/hooks/register.tsx` 맨 위 `BUTTONS` 목록만 고치면 됩니다.
- `command`: 슬래시 명령어 (빗금 없이, 예: `'handoff'`)
- `prompt`: 그대로 보낼 문장
