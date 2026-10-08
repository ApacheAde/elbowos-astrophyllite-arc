#!/usr/bin/env python3
"""Astrophyllite Arc — bronze asteroid arcade for ElbowOS. Python 3 + pygame.

Steer a copper dart around a central starburst crystal. Shatter orbiting
shards. A/D rotate, W/S radial thrust, Space fire, R restart.
"""
import math
import os
import random
import subprocess
import sys

PLAY = "--play" in sys.argv
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get(
    "ELBOWOS_MP4", "/workspace/artifacts/ASTROPHYLLITE_ARC_ElbowOS.mp4"
)
TITLE, HANDLE = "ASTROPHYLLITE ARC", "x.com/ElbowOS"
CX, CY = 540, 1040
INK = (10, 6, 18)
COPPER = (224, 122, 61)
GOLD = (255, 210, 96)
LIME = (190, 255, 70)
CREAM = (255, 236, 214)
PLUM = (120, 48, 92)


def wrap_ang(a):
    while a > math.pi:
        a -= math.tau
    while a < -math.pi:
        a += math.tau
    return a


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 42, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 32, bold=True)
        self.stars = [
            (random.randrange(W), random.randrange(H), random.choice((1, 2, 2, 3)))
            for _ in range(90)
        ]
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.ang = -1.2
        self.rad = 520
        self.facing = 0.4
        self.cool = 0
        self.flash = 0
        self.parts = []
        self.bullets = []
        self.shards = []
        rings = (240, 360, 500, 640)
        for i, rad in enumerate(rings):
            for k in range(3):
                self.shards.append(
                    {
                        "ang": k * math.tau / 3 + i * 0.4,
                        "rad": rad + random.randint(-18, 18),
                        "spin": random.choice((-1, 1)) * (0.012 + i * 0.003),
                        "size": 3 if i < 2 else 2,
                        "rot": random.random() * math.tau,
                        "hue": i % 3,
                    }
                )

    def spawn_burst(self, x, y, col, n=10):
        for _ in range(n):
            a = random.random() * math.tau
            s = random.uniform(2, 8)
            self.parts.append([x, y, math.cos(a) * s, math.sin(a) * s, col, 18])

    def fire(self):
        if self.cool > 0:
            return
        x = CX + math.cos(self.ang) * self.rad
        y = CY + math.sin(self.ang) * self.rad
        self.bullets.append(
            [x, y, math.cos(self.facing) * 26, math.sin(self.facing) * 26, 48]
        )
        self.cool = 6

    def nearest(self):
        sx = CX + math.cos(self.ang) * self.rad
        sy = CY + math.sin(self.ang) * self.rad
        best, bd = None, 1e9
        for sh in self.shards:
            x = CX + math.cos(sh["ang"]) * sh["rad"]
            y = CY + math.sin(sh["ang"]) * sh["rad"]
            d = (x - sx) ** 2 + (y - sy) ** 2
            if d < bd:
                best, bd = (x, y, sh), d
        return best

    def auto(self):
        hit = self.nearest()
        if not hit:
            self.ang += 0.02
            return
        x, y, sh = hit
        sx = CX + math.cos(self.ang) * self.rad
        sy = CY + math.sin(self.ang) * self.rad
        want = math.atan2(y - sy, x - sx)
        diff = wrap_ang(want - self.facing)
        self.facing += max(-0.14, min(0.14, diff))
        # slide along the orbit toward the shard's angle
        gap = wrap_ang(sh["ang"] - self.ang)
        self.ang += max(-0.03, min(0.03, gap * 0.35))
        self.rad += max(-7, min(7, (sh["rad"] - self.rad) * 0.08))
        self.rad = max(180, min(760, self.rad))
        if abs(diff) < 0.22:
            self.fire()
        # dodge if a shard is on top of the dart
        if math.hypot(x - sx, y - sy) < 70:
            self.ang += 0.08

    def update(self, keys=None):
        self.t += 1
        self.cool = max(0, self.cool - 1)
        self.flash = max(0, self.flash - 1)
        if keys is not None:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.facing -= 0.08
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.facing += 0.08
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.rad = max(160, self.rad - 6)
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.rad = min(780, self.rad + 6)
            self.ang += 0.012
        else:
            self.auto()
        if len(self.shards) < 6:
            self.shards.append(
                {
                    "ang": random.random() * math.tau,
                    "rad": random.choice((280, 420, 560, 680)),
                    "spin": random.choice((-1, 1)) * 0.016,
                    "size": 3,
                    "rot": random.random() * math.tau,
                    "hue": random.randrange(3),
                }
            )
        for sh in self.shards:
            sh["ang"] += sh["spin"]
            sh["rot"] += 0.03
        sx = CX + math.cos(self.ang) * self.rad
        sy = CY + math.sin(self.ang) * self.rad
        for sh in list(self.shards):
            x = CX + math.cos(sh["ang"]) * sh["rad"]
            y = CY + math.sin(sh["ang"]) * sh["rad"]
            if math.hypot(x - sx, y - sy) < 28 + sh["size"] * 14:
                self.flash = 8
                self.score = max(0, self.score - 15)
                self.ang += 0.5
                self.spawn_burst(sx, sy, COPPER, 8)
        alive = []
        for b in self.bullets:
            b[0] += b[2]
            b[1] += b[3]
            b[4] -= 1
            if b[4] <= 0 or not (0 < b[0] < W and 0 < b[1] < H):
                continue
            hit = None
            for sh in self.shards:
                x = CX + math.cos(sh["ang"]) * sh["rad"]
                y = CY + math.sin(sh["ang"]) * sh["rad"]
                if math.hypot(b[0] - x, b[1] - y) < 18 + sh["size"] * 16:
                    hit = sh
                    break
            if hit:
                self.shards.remove(hit)
                self.score += 40 * hit["size"]
                self.spawn_burst(b[0], b[1], GOLD if hit["size"] > 1 else LIME, 14)
                if hit["size"] > 1:
                    for sign in (-1, 1):
                        self.shards.append(
                            {
                                "ang": hit["ang"] + sign * 0.18,
                                "rad": max(160, min(760, hit["rad"] + sign * 36)),
                                "spin": hit["spin"] * -1.3,
                                "size": hit["size"] - 1,
                                "rot": hit["rot"],
                                "hue": (hit["hue"] + 1) % 3,
                            }
                        )
                continue
            alive.append(b)
        self.bullets = alive
        nxt = []
        for p in self.parts:
            p[0] += p[2]
            p[1] += p[3]
            p[5] -= 1
            if p[5] > 0:
                nxt.append(p)
        self.parts = nxt

    def draw(self, surf):
        surf.fill(INK)
        for i in range(8):
            c = 16 + i * 3
            pygame.draw.circle(surf, (c, 8 + i, 22 + i * 2), (CX, CY), 860 - i * 70, 2)
        for i, (x, y, r) in enumerate(self.stars):
            yy = (y + self.t * (1 + r)) % H
            pygame.draw.circle(surf, (180, 150, 90), (x, int(yy)), r)
        spin = self.t * 0.02
        crystal = []
        for i in range(12):
            a = spin + i * math.tau / 12
            rad = 78 if i % 2 == 0 else 36
            crystal.append((CX + math.cos(a) * rad, CY + math.sin(a) * rad))
        pygame.draw.polygon(surf, GOLD, crystal)
        pygame.draw.polygon(surf, COPPER, crystal, 4)
        hues = (COPPER, GOLD, LIME)
        for sh in self.shards:
            x = CX + math.cos(sh["ang"]) * sh["rad"]
            y = CY + math.sin(sh["ang"]) * sh["rad"]
            pts = []
            n = 5 + sh["size"]
            for i in range(n):
                a = sh["rot"] + i * math.tau / n
                wob = 1.0 if i % 2 == 0 else 0.62
                pts.append(
                    (x + math.cos(a) * sh["size"] * 18 * wob,
                     y + math.sin(a) * sh["size"] * 18 * wob)
                )
            col = hues[sh["hue"]]
            pygame.draw.polygon(surf, col, pts, 4)
            pygame.draw.circle(surf, CREAM, (int(x), int(y)), 3)
        sx = CX + math.cos(self.ang) * self.rad
        sy = CY + math.sin(self.ang) * self.rad
        nose = (sx + math.cos(self.facing) * 36, sy + math.sin(self.facing) * 36)
        left = (
            sx + math.cos(self.facing + 2.5) * 22,
            sy + math.sin(self.facing + 2.5) * 22,
        )
        right = (
            sx + math.cos(self.facing - 2.5) * 22,
            sy + math.sin(self.facing - 2.5) * 22,
        )
        if self.t % 4 < 2:
            tail = (
                sx - math.cos(self.facing) * 28,
                sy - math.sin(self.facing) * 28,
            )
            pygame.draw.line(surf, LIME, (sx, sy), tail, 4)
        body = LIME if self.flash else COPPER
        pygame.draw.polygon(surf, body, (nose, left, right))
        pygame.draw.polygon(surf, CREAM, (nose, left, right), 2)
        for b in self.bullets:
            pygame.draw.circle(surf, LIME, (int(b[0]), int(b[1])), 6)
        for p in self.parts:
            pygame.draw.circle(surf, p[4], (int(p[0]), int(p[1])), max(1, p[5] // 5))
        banner = pygame.Surface((W, 150), pygame.SRCALPHA)
        banner.fill((8, 4, 14, 170))
        surf.blit(banner, (0, 36))
        title = self.font.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        score = self.mid.render(f"SCORE  {self.score}", True, LIME)
        surf.blit(score, score.get_rect(center=(W // 2, 168)))
        foot = pygame.Surface((W, 110), pygame.SRCALPHA)
        foot.fill((8, 4, 14, 180))
        surf.blit(foot, (0, H - 140))
        tag = self.small.render(HANDLE, True, CREAM)
        surf.blit(tag, tag.get_rect(center=(W // 2, H - 84)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        running = False
                    elif ev.key == pygame.K_SPACE:
                        self.fire()
                    elif ev.key == pygame.K_r:
                        self.reset()
            self.update(keys)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        surf = pygame.Surface((W, H))
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart",
            OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                self.update()
                self.draw(surf)
                proc.stdin.write(pygame.image.tostring(surf, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        pygame.quit()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)


def main():
    g = Game()
    if PLAY:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
