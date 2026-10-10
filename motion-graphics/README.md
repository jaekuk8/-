# 모션그래픽

대화로 기획한 세로 쇼츠(1080×1920) 모션그래픽입니다. **영상을 뽑으면 효과음과 배경음악이 자동으로 합쳐집니다.**

## 구성 (`makjju/` = 크라운 × 국순당 막쮸 20초 영상)
| 파일 | 하는 일 |
|---|---|
| `makjju.html` | 그림과 움직임. `render(t)`가 t초의 화면을 그림 |
| `sound.py` | 효과음 + 배경음악 합성 (numpy만 사용, 외부 음원 없음) |
| `render.js` | 화면 캡처 → 소리 합성 → 합치기까지 한 번에 |

## 사용법 (Claude Code 클라우드 세션 기준)
```
cd motion-graphics/makjju
node render.js stills out 1.8 6.3 18.5     # 시안용 정지 화면
node render.js video out/완성본.mp4 20      # 소리 포함 완성본
```
- 필요한 것: Node + Playwright, Python3 + numpy, ffmpeg (클라우드 세션에는 기본으로 있음)
- 글꼴(주아, 블랙한산스, 고운돋움)은 처음 실행할 때 자동으로 받습니다.

## 다른 제품 영상 만들기
`makjju/` 폴더를 복사한 뒤 문구·색·장면을 바꾸고, `sound.py`의 효과음 시점도 바뀐 장면에 맞춥니다.
