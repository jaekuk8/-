# 막쮸 모션그래픽용 효과음 + 배경음악 합성 (numpy만 사용, 외부 음원 없음)
# 사용법: python3 sound.py <출력.wav>
import json, sys, wave
from pathlib import Path
import numpy as np

SR, DUR = 44100, 20.0
N = int(SR * DUR)
rng = np.random.default_rng(5)
here = Path(__file__).parent
sfx = np.zeros((N, 2))
mus = np.zeros((N, 2))

def tt(d): return np.arange(int(d * SR)) / SR
def place(bus, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    bus[i:i + len(sig), 0] += sig * np.sqrt((1 - pan) / 2)
    bus[i:i + len(sig), 1] += sig * np.sqrt((1 + pan) / 2)
def osc(freq, d):
    f = np.broadcast_to(np.asarray(freq, float), (int(d * SR),))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))
def fade(x, a=0.004, r=0.01):
    n = len(x); e = np.ones(n)
    ai, ri = min(int(a * SR), n), min(int(r * SR), n)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return x * e
NOTE = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
def hz(n): return 440 * 2 ** ((NOTE[n[0]] + 12 * (int(n[1:]) - 4)) / 12)

# ---------- 효과음 재료 ----------
def pop(f0=700, d=0.12):
    t = tt(d); f = f0 * (1 + 1.2 * np.exp(-t * 60))
    s = osc(f, d) * np.exp(-t * 38)
    n = band(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 300) * 0.4
    return fade(s + n, 0.001)
def blip(f, d=0.09):
    t = tt(d); return fade((osc(f, d) + 0.3 * osc(f * 4, d)) * np.exp(-t * 45), 0.001)
def bell(f, d=1.2):
    t = tt(d); return fade(sum(a * osc(f * m, d) * np.exp(-t * k) for m, a, k in [(1, 1, 3), (2.76, .4, 7), (5.4, .2, 14)]), 0.001)
def slide(f0, f1, d, vib=0.0, curve=1.0):
    t = tt(d); p = (t / d) ** curve; f = f0 * (f1 / f0) ** p * (1 + vib * np.sin(2 * np.pi * 7 * t))
    return fade(osc(f, d) * np.sin(np.pi * t / d) ** 0.5, 0.01, 0.03)
def plop(f0=300, f1=1300, d=0.12):
    t = tt(d); f = f0 + (f1 - f0) * (1 - np.exp(-t * 40))
    return fade(osc(f, d) * np.exp(-t * 30), 0.001)
def thud(d=0.35):
    t = tt(d); f = 55 + 70 * np.exp(-t * 25)
    s = osc(f, d) * np.exp(-t * 12) + band(rng.standard_normal(len(t)), 80, 900) * np.exp(-t * 60) * 0.5
    return fade(s + 0.35 * osc(820, d) * np.exp(-t * 70), 0.001)
def clack(d=0.08):
    t = tt(d); return fade(band(rng.standard_normal(len(t)), 900, 2600) * np.exp(-t * 90) + 0.5 * osc(1050, d) * np.exp(-t * 80), 0.001)
def noise_swell(d, lo, hi, shape='up'):
    t = tt(d); e = (t / d) ** 2 if shape == 'up' else np.sin(np.pi * t / d)
    return fade(band(rng.standard_normal(len(t)), lo, hi) * e, 0.01, 0.03)
def rubber(f0, f1, d):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d) * (1 + 0.04 * np.sin(2 * np.pi * 9 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = sum(np.sin(k * ph) / k ** 1.3 for k in range(1, 7))
    return fade(s * np.sin(np.pi * t / d) ** 0.6, 0.02, 0.05)
def boing(f0=260, d=0.9):
    t = tt(d); f = f0 * (1 + 0.55 * np.sin(2 * np.pi * 11 * t) * np.exp(-t * 5))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return fade((np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-t * 4), 0.002)
def smack(d=0.07):
    t = tt(d); return fade(band(rng.standard_normal(len(t)), 1800, 5000) * np.exp(-t * 160) + 0.6 * osc(1800 + 2000 * t / d, d) * np.exp(-t * 60), 0.0005)

PENTA = [hz(n) for n in ['C6', 'D6', 'E6', 'G6', 'A6', 'C7', 'D7', 'E7', 'G7']]

# ---------- 효과음 배치 (화면 타이밍과 동일) ----------
place(sfx, 0.32, pop(520), .5)                                   # 상단 알약 라벨
place(sfx, 0.55, slide(260, 760, .3, curve=.6), .3)               # 쌀알 등장
place(sfx, 0.82, boing(420, .5), .25)
def ticks(t0, n, stagger, gain=.18, base=0):
    for i in range(n): place(sfx, t0 + i * stagger + .06, blip(PENTA[(base + i) % len(PENTA)] / 2), gain, (i / max(n - 1, 1) - .5) * .6)
ticks(0.8, 9, .05)                                                 # 100% 국내산 쌀
place(sfx, 2.5, pop(300, .1), .3)                                  # 웅크림
place(sfx, 2.7, slide(450, 1500, .5, curve=1.6), .18)               # 점프(위로)
place(sfx, 3.3, slide(1500, 380, .65, vib=.03, curve=.7), .17)     # 떨어짐
place(sfx, 3.95, plop(), .7); place(sfx, 4.05, plop(400, 1700, .1), .35, .3)  # 퐁당
place(sfx, 4.0, noise_swell(.3, 300, 2500, 'up'), .25)             # 뚜껑 낙하 바람
place(sfx, 4.3, thud(), .9)                                        # 뚜껑 '툭'
ticks(4.3, 6, .05, base=1)                                         # 세 번의 발효로
for k, r0 in enumerate([4.7, 6.1, 7.5]):
    place(sfx, r0 - .05, bell(hz(['G5', 'B5', 'D6'][k])), .35)    # 회차 배지 '띵'
    for j in (1, 2, 3): place(sfx, r0 + 1.3 * j / 4, clack(), .5 * (1 - j / 4) + .1, (-1) ** j * .3)  # 뚜껑 달그락
    for _ in range(16):                                            # 보글보글 바닥음
        place(sfx, r0 + rng.uniform(0, 1.2), plop(rng.uniform(150, 260), rng.uniform(450, 800), .06), .12, rng.uniform(-.5, .5))
for b in json.loads((here / 'bubbles.json').read_text()):          # 거품 터짐
    place(sfx, b, pop(rng.uniform(1100, 1900), .05), .14, rng.uniform(-.6, .6))
place(sfx, 8.9, noise_swell(.35, 40, 400, 'up') + .6 * slide(50, 70, .35), .7)  # 부글부글 기 모으기
place(sfx, 9.25, pop(380, .25), 1.0); place(sfx, 9.25, thud(.25), .5)            # '뽕!'
place(sfx, 9.27, noise_swell(.5, 1500, 7000, 'mid'), .22, .3)      # 뚜껑 날아감
for i, f in enumerate([hz('C6'), hz('E6'), hz('G6'), hz('C7')]):   # 캔디 등장 반짝
    place(sfx, 9.35 + i * .06, bell(f, .6), .16, -.4 + i * .27)
place(sfx, 9.8, noise_swell(.38, 3000, 12000, 'up'), .3)           # 번쩍
ticks(10.4, 6, .05, base=2)                                        # 부드러운 풍미
place(sfx, 10.6, rubber(170, 430, .75), .32)                       # 쭈~욱
place(sfx, 11.5, boing(300, .9), .45)                              # 탱~
place(sfx, 12.85, noise_swell(.45, 600, 4000, 'mid'), .15)         # 다가오기
ticks(13.15, 6, .05, base=3)                                       # 막 끌리는 맛,
for i, f in enumerate([520, 600, 700]): place(sfx, 14.3 + i * .09 + .05, pop(f, .14), .6)  # 막 쮸 ~
place(sfx, 14.36, smack(), .55); place(sfx, 14.42, slide(1500, 950, .38), .2)  # 쪽 + 쮸~
for i in range(8): place(sfx, 14.38 + i * .16, bell(PENTA[(i * 3) % 9], .5), .1, (-1) ** i * .4)  # 하트
place(sfx, 15.85, noise_swell(.6, 300, 3000, 'up'), .3)            # 포장 올라옴
place(sfx, 16.5, thud(.25), .35); place(sfx, 16.5, pop(450), .3)
place(sfx, 16.72, pop(620), .45)                                   # 발효쌀 츄잉캔디 라벨
for i in range(7): place(sfx, 17.0 + i * .1, bell(PENTA[i + 1], .5), .1, -.6 + i * .2)  # 포장 반짝
for f in [hz('C5'), hz('E5'), hz('G5'), hz('C6')]: place(sfx, 17.25, bell(f, 2.2), .16)  # 마무리 '딩~'

# ---------- 배경음악 (C - Am - F - G, 120BPM, 우쿨렐레+마림바 느낌) ----------
def pluck(f, d=0.9):
    t = tt(d); return fade(sum((1 / k) * osc(f * k, d) * np.exp(-t * (3 + k * 2.2)) for k in range(1, 7)), 0.002)
def marimba(f, d=0.6):
    t = tt(d); return fade(osc(f, d) * np.exp(-t * 6) + .35 * osc(f * 4, d) * np.exp(-t * 18), 0.001)
def bass(f, d=0.45):
    t = tt(d); return fade((osc(f, d) + .3 * osc(2 * f, d)) * np.exp(-t * 4), 0.003, 0.05)
def kick():
    t = tt(.18); return fade(osc(45 + 90 * np.exp(-t * 30), .18) * np.exp(-t * 18), 0.001)
def shaker():
    t = tt(.05); return fade(band(rng.standard_normal(len(t)), 6000, 14000) * np.exp(-t * 70), 0.003)
CH = {'C': ['C4', 'E4', 'G4', 'C5'], 'Am': ['A3', 'E4', 'A4', 'C5'], 'F': ['F3', 'C4', 'F4', 'A4'], 'G': ['G3', 'D4', 'G4', 'B4']}
ROOT = {'C': 'C3', 'Am': 'A2', 'F': 'F2', 'G': 'G2'}
prog = ['C', 'Am', 'F', 'G'] * 2 + ['C', 'Am', 'F', 'G']
def level(t):  # 구간별 음악 크기
    if 8.9 <= t < 10.15: return 0.15   # '뽕!' 앞뒤는 잠깐 비워 둠
    return 1.0
for bar, ch in enumerate(prog):
    b0 = bar * 2.0
    if b0 >= 17.0: break
    for off in (0, .75, 1.0, 1.5):                                  # 스트럼 리듬
        t0 = b0 + off
        if t0 >= 17.0 or level(t0) < 1: continue
        for j, n in enumerate(CH[ch]): place(mus, t0 + j * .012, pluck(hz(n)), .11 * (1 if off in (0, 1.0) else .7), -.25 + j * .15)
    for off in (0, 1.0):
        t0 = b0 + off
        if t0 < 3.0 or t0 >= 17.0 or level(t0) < 1: continue
        place(mus, t0, bass(hz(ROOT[ch])), .32); place(mus, t0, kick(), .35)
    for k in range(8):
        t0 = b0 + k * .25
        if t0 < 17.0 and level(t0) == 1: place(mus, t0, shaker(), .05 if k % 2 == 0 else .09, .4)
MEL = [(0, 'E5'), (.5, 'G5'), (1, 'A5'), (1.5, 'G5'), (2, 'E5'), (3, 'C5'), (3.5, 'D5'),
       (4, 'E5'), (4.5, 'E5'), (5, 'D5'), (5.5, 'C5'), (6, 'A4'), (7, 'C5'),
       (8, 'F5'), (8.5, 'A5'), (9, 'G5'), (9.5, 'F5'), (10, 'E5'), (11, 'D5'), (11.5, 'E5'),
       (12, 'D5'), (12.5, 'G5'), (13, 'B5')]
for beat, n in MEL: place(mus, 10.15 + beat * .5 * (6.85 / 7.0), marimba(hz(n)), .2, .2)
for j, n in enumerate(['C3', 'C4', 'E4', 'G4', 'C5', 'E5']):       # 마지막 화음
    place(mus, 17.0 + j * .02, pluck(hz(n), 3.0), .13);
place(mus, 17.0, bass(hz('C2'), 1.5), .3)

# ---------- 공간감(리버브) + 마스터 ----------
def reverb(x, d=1.4, wet=.18):
    t = tt(d); ir = rng.standard_normal((len(t), 2)) * np.exp(-t * 4.5)[:, None]
    L = len(x) + len(t); out = np.zeros_like(x)
    for c in range(2):
        out[:, c] = np.fft.irfft(np.fft.rfft(x[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:len(x)]
    return x + out / np.abs(out).max() * np.abs(x).max() * wet
mix = reverb(sfx, wet=.12) + reverb(mus, wet=.22)
env = np.ones(N); fo = int(1.2 * SR); env[-fo:] = np.linspace(1, 0, fo) ** 1.5
mix *= env[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.3) / np.tanh(1.3) * 0.89   # 부드럽게 눌러 최대 -1dB
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('저장:', sys.argv[1])
