from __future__ import division # Use floating-point division on ints
import sys, pygame, random as rand
from collections import namedtuple
Point = namedtuple('Point', 'x y')
dist = lambda a,b: ((a.x-b.x)**2+(a.y-b.y)**2)**.5
radius = lambda age: (6375*age)/616-(2875*age**2)/4928+(75*age**3)/9856
add_scaled_vector = lambda pos, v, s: Point(pos.x + s * v.x, pos.y + s * v.y)
aim_at = lambda s, t, time: Point((t.x - s.x) / time, (t.y - s.y) / time)
size = width, height = 900, 600
screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWSURFACE)
clock = pygame.time.Clock()
class AttributeHack(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs, alive=1)
Base = Missile = Explosion = AttributeHack
pygame.init()
scorefont = pygame.font.SysFont("monospace", 15)
titlefont = pygame.font.SysFont("monospace", 100)
round_num = 0
score = 0
bases = [Base(pos=Point(250+100*x, height), armed_in=30*x) for x in xrange(5)]
explosions = []
missiles = []
def text(font, string, position, color):
    screen.blit(font.render(string, 1, color), position)
while bases:
    round_num += 1
    end_frame = 250 + round_num * 50
    for x in xrange(round_num - 1 +int(1.2**round_num)):
        dest = Point(rand.randint(200, width-200), height)
        time = rand.randint(200, end_frame-5)
        v = Point(rand.randint(-3, 3), 3)
        start = add_scaled_vector(dest, v, -time)
        missiles.append(Missile(pos=start, dest=dest, color=(250, 0, 0), v=v,
                tail=25, icbm=rand.randint(50, 350) if x+7<round_num else 999))
    for t in xrange(end_frame):
        screen.fill((0, 0, 0))
        if t < 55:
            x = int(3*radius(t / 2))
            text(titlefont, "Round %d" % round_num, (250, 200), (x, x, x))
        text(scorefont, "Score %d" % score, (0, 0), (255, 255, 255))
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and
                    e.key in (pygame.K_q, pygame.K_ESCAPE)):
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONUP:
                armed = [b for b in bases if b.armed_in == 0]
                if armed:
                    dest = Point(*pygame.mouse.get_pos())
                    base = min(armed, key=lambda b: dist(b.pos, dest))
                    pos = Point(base.pos.x, height-20)
                    base.armed_in = 25
                    missiles.append(Missile(pos=pos, dest=dest, tail=1, icbm=0,
                            v=aim_at(pos, dest, 5), color=(160, 255, 220)))
        for base in bases:
            base.armed_in = max(0, base.armed_in - 1)
            pygame.draw.circle(screen, (0, 0, 255), base.pos, 20)
            pygame.draw.circle(screen, (0, 255, 99),
                    (base.pos.x, base.pos.y-20+base.armed_in), 5)
        for m in missiles[:]:
            m.pos = add_scaled_vector(m.pos, m.v, 1)
            pygame.draw.aaline(screen, m.color, m.pos,
                    add_scaled_vector(m.pos, m.v, -m.tail), 8)
            if dist(m.pos, m.dest) < 5:
                m.alive = 0
                explosions.append(Explosion(pos=m.pos, age=0))
            elif m.icbm == m.pos.y and len(bases) > 1 and 0 < m.pos.x < 900:
                m.alive = 0
                for base in bases:
                    missiles.append(Missile(pos=m.pos, dest=base.pos,
                            v=aim_at(m.pos, base.pos, (600-m.pos.y)/3),
                            color=(250, 0, 0), tail=5, icbm=0))
        for ex in explosions[:]:
            r = int(radius(ex.age))
            for base in bases:
                if dist(base.pos, ex.pos) < r * 2/3:
                    base.alive = 0
                    explosions.append(Explosion(pos=base.pos, age=1))
            for m in missiles:
                if m.alive and dist(m.pos, ex.pos) <= r:
                    m.alive = 0
                    score += m.color[0] * (len(bases) if m.icbm > 0 else 1)
                    explosions.append(Explosion(pos=m.pos, age=1))
            pygame.draw.circle(screen, (200, 0, 0), map(int, ex.pos), r)
            ex.age += 1
        for ex in explosions: # paint inner part in separate pass, looks better
            r = int(radius(ex.age) * (30-ex.age) / 30)
            pygame.draw.circle(screen, (255, 150, 0), map(int, ex.pos), r)
        explosions = [x for x in explosions if x.age < 29]
        bases[:] = [x for x in bases if x.alive]
        missiles[:] = [x for x in missiles if x.alive]
        clock.tick(30)
        pygame.display.flip()
    score += round_num * 1000 + len(bases) * 2500
