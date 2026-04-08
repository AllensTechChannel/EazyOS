import pyxel
from random import randint, choice


class DVDLogo:
    def __init__(self, screen_w, screen_h):
        self.w = 18
        self.h = 13

        self.x = randint(0, screen_w - self.w)
        self.y = randint(0, screen_h - self.h)

        self.vx = choice([-2, 2])
        self.vy = choice([-2, 2])

        # Random color bank offset (optional)
        self.u = 0
        self.v = 0


class Game:
    def __init__(self):
        self.W = 160
        self.H = 120
        self.LOGO_COUNT = 6

        pyxel.init(self.W, self.H, title="DVD Screensaver")
        pyxel.fullscreen(True)

        pyxel.load("assets/dvd.pyxres")

        self.logos = [
            DVDLogo(self.W, self.H)
            for _ in range(self.LOGO_COUNT)
        ]

        pyxel.run(self.update, self.draw)

    def update(self):
        for logo in self.logos:
            logo.x += logo.vx
            logo.y += logo.vy

            if logo.x <= 0 or logo.x + logo.w >= self.W:
                logo.vx *= -1

            if logo.y <= 0 or logo.y + logo.h >= self.H:
                logo.vy *= -1

    def draw(self):
        pyxel.cls(0)

        for logo in self.logos:
            pyxel.blt(
                logo.x,
                logo.y,
                0,          # image bank
                logo.u,
                logo.v,
                logo.w,
                logo.h
            )


Game()
