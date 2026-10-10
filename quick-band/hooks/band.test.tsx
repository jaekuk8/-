import { test, expect } from 'claude-code/testing'

const props = {
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns: 80,
  scroll: { bodyRows: 10, offset: 0, contentRows: 1 },
  view: {},
} as any

test('버튼 4개가 그려지고 누르면 명령/문장이 실행된다', async ($, on) => {
  const commands: string[] = []
  const prompts: string[] = []
  on('command.run', async ($, e) => {
    commands.push(e.command)
    return { text: '' } as any
  })
  on('prompt.submit', async ($, e) => {
    prompts.push(e.text)
    return { drop: 'test' } as any
  })

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ plugin: 'quick-band', surface, component: 'AbovePrompt', props })
    for (const key of ['compact', 'context', 'handoff', 'save']) {
      expect(await ui.find({ key })).toBeDefined()
    }
    await ui.press({ key: 'compact' })
    await ui.press({ key: 'handoff' })
    await ui.unmount()
  }

  expect(commands).toEqual(['compact', 'compact'])
  expect(prompts.length).toBe(2)
  expect(prompts[0]).toContain('HANDOFF.md')
})
