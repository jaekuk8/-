// 사용법: node render.js stills <출력폴더> 1.8 6.3 18.5   (시안용 정지 화면)
//        node render.js video  <출력.mp4> [길이초]       (화면 + 효과음/배경음악까지 합친 완성본)
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 글꼴이 없으면 Google Fonts에서 받음 (저장소에는 글꼴 파일을 올리지 않음)
const FONTS = {
  'Jua.ttf': 'https://fonts.gstatic.com/s/jua/v18/co3KmW9ljjAjcw.ttf',
  'BlackHanSans.ttf': 'https://fonts.gstatic.com/s/blackhansans/v24/ea8Aad44WunzF9a-dL6toA8r8nqV.ttf',
  'GowunDodum.ttf': 'https://fonts.gstatic.com/s/gowundodum/v12/3Jn5SD_00GqwlBnWc1TUJF0F.ttf',
};
fs.mkdirSync(path.join(__dirname, 'fonts'), { recursive: true });
for (const [name, url] of Object.entries(FONTS)) {
  const p = path.join(__dirname, 'fonts', name);
  if (!fs.existsSync(p)) execFileSync('curl', ['-sSfL', '-o', p, url]);
}

(async () => {
  const [, , mode, out, ...rest] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => console.error('페이지 오류:', e.message));
  await page.goto('file://' + path.join(__dirname, 'makjju.html'));
  await page.waitForFunction(() => window.READY === true);

  if (mode === 'stills') {
    for (const ts of rest) {
      await page.evaluate(t => render(t), +ts);
      await page.screenshot({ path: path.join(out, `still_${ts}.png`) });
    }
  } else {
    // 거품 터지는 시점을 소리 합성용으로 저장
    const bubbles = await page.evaluate(() => BUB.map(x => +(R0[x.round] + x.d + .95 * .82).toFixed(3)).sort((a, b) => a - b));
    fs.writeFileSync(path.join(__dirname, 'bubbles.json'), JSON.stringify(bubbles));

    const silent = out.replace(/\.mp4$/, '') + '_silent.mp4';
    const wav = out.replace(/\.mp4$/, '') + '_sound.wav';
    const fps = 30, dur = +(rest[0] || 20);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', silent],
      { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = 0; f < fps * dur; f++) {
      await page.evaluate(t => render(t), f / fps);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));

    // 소리는 항상 함께: 효과음+배경음악 합성 후 영상에 합침
    execFileSync('python3', [path.join(__dirname, 'sound.py'), wav], { stdio: 'inherit' });
    execFileSync('ffmpeg', ['-y', '-v', 'error', '-i', silent, '-i', wav, '-c:v', 'copy',
      '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
      '-shortest', '-movflags', '+faststart', out], { stdio: 'inherit' });
    fs.unlinkSync(silent);
    fs.unlinkSync(wav);
    console.log('완성:', out);
  }
  await browser.close();
})();
