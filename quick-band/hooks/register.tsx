import type { Register } from 'claude-code'

// 버튼 목록: 여기만 고치면 됩니다.
// command: 슬래시 명령어(빗금 없이) / prompt: 그대로 보낼 문장
type QuickButton = { key: string; label: string; command?: string; prompt?: string }

export const BUTTONS: QuickButton[] = [
  { key: 'compact', label: '압축', command: 'compact' },
  { key: 'context', label: '컨텍스트', command: 'context' },
  {
    key: 'handoff',
    label: '핸드오프',
    prompt:
      '지금까지의 작업을 다음 세션이 그대로 이어받을 수 있게 핸드오프 문서로 정리해줘. 목표, 완료한 일, 남은 일, 주의할 점, 관련 파일 경로를 넣어서 HANDOFF.md로 저장해줘.',
  },
  {
    key: 'save',
    label: '세션저장',
    prompt:
      '지금까지 대화의 핵심 결정사항과 진행 상황을 요약해서 sessions 폴더에 "날짜-주제.md" 파일명으로 저장해줘.',
  },
]

export const register: Register = on => {
  on('ui.render', { component: 'AbovePrompt' }, ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }

    const { Box, Button } = $.ui.resolve(e)

    return (
      <Box flexDirection="row" gap={1}>
        {BUTTONS.map((b, i) => (
          <Button
            key={b.key}
            label={b.label}
            hotkey={String(i + 1)}
            onPress={async () => {
              try {
                if (b.command) {
                  await $.command.run({ command: b.command, args: '' })
                } else if (b.prompt) {
                  await $.prompt.submit({ text: b.prompt })
                }
              } catch {
                $.ui.toast(`'${b.label}' 실행 실패: 명령어 이름을 확인하세요`)
              }
            }}
          />
        ))}
      </Box>
    )
  })
}
