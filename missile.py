# Missile command in 100 lines of Python using Pygame!
# Comments added for clarity.
from __future__ import division # Use floating-point division on ints
import sys, pygame
from collections import namedtuple
from random import randint, choice

# It would be save a line to use regular tuples for points and index x and y
# using point[0] and point[1], but I think this is much clearer.
Point = namedtuple('Point', 'x y')

# Distance formula. For best performance we could use distance squared
# instead of distance, but we're not doing much work so let's go for clarity.
dist = lambda a,b: ((a.x-b.x)**2+(a.y-b.y)**2)**.5

# Snap-to-grid
snap = lambda x: map(int, x)

# Explosion radius as a function of time. I chose this function after playing
# around in Wolfram|Alpha for a while. It increases sharply from f(0) = 0 to a
# max at f(11) ~= 53, then slowly back down to f(28) ~= 0
radius = lambda age: (6375*age)/616-(2875*age**2)/4928+(75*age**3)/9856

# Utility function to add a vector times a constant to a position.
add_scaled_vector = lambda pos, v, s: Point(pos.x + s * v.x, pos.y + s * v.y)

# Given a start s, target t, and arrival time, return the velocity vector.
aim_at = lambda s, t, time: Point((t.x - s.x) / time, (t.y - s.y) / time)

# Screen size
size = width, height = 900, 600

# On my laptop, the game runs at about 12 fps without hardware acceleration and
# easily runs at 60 with hardware acceleration.
screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.HWSURFACE)
clock = pygame.time.Clock()

# A pretty hacky way to save lines. We want to assign properties of generic
# objects using keyword arguments in the constructor, because actual
# constructors use a lot of lines. To make things a little clearer, we'll
# pretend like there are separate classes for Base, Missile, etc. but really
# everything is just a bunch of AttributeHack objects.
class AttributeHack(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs, alive=1)
Base = Missile = Explosion = AttributeHack


pygame.init()
scorefont = pygame.font.SysFont("monospace", 15)
titlefont = pygame.font.SysFont("monospace", 100)
round_num = 0
score = 0

# Allocate our array of bases. When this array is empty, the game ends.
bases = [Base(pos=Point(250+100*x, height), armed_in=30*x) for x in xrange(5)]

# We allocate the explosions and missiles arrays here so that they will persist
# between rounds. If we allocated them per-round then the user might see one of
# their missiles suddenly disappear when the round ends.
explosions = []
missiles = []
while bases:
    round_num += 1

    # Each round lasts a little longer than the previous one.
    end_frame = 250 + round_num * 50

    # Number of missiles goes up about 20% per round.
    for x in xrange(round_num - 1 +int(1.2**round_num)):
        # For each missile, we randomly pick a target, time of impact, and
        # horizontal speed. The vertical speed is the same for all incoming
        # missiles. We then compute the origin of the missile based on those
        # parameters. We let pygame handle all of the clipping -- at the start
        # of the round, we're drawing every missile for that round, but they're
        # all off-screen.
        dest = choice(bases).pos
        time = randint(200, end_frame-5)
        v = Point(randint(-3, 3), 3)
        start = add_scaled_vector(dest, v, -time)
        # Each missile has an "ICBM elevation". When it hits that y position,
        # the missile will split into N missiles, one per base. Note that
        # because we allow any y position in the range, but missiles always
        # have vertical velocity of 3, there's only a 1/3 chance that a
        # missile will actually be an ICBM.
        missiles.append(Missile(pos=start, dest=dest, color=(250,0,0), v=v,
                tail=25, icbm=randint(50, 350) if x+7<round_num else 999))
    for t in xrange(end_frame):
        screen.fill((0,0,5))
        # Render the round number. To save lines, we reuse the explosion radius
        # formula to make the text fade in and out.
        if t < 55:
            x = int(3*radius(t / 2))
            label = titlefont.render("Round " + str(round_num), 1, (x, x, x))
            screen.blit(label, (450-label.get_width()/2, 200))
        label = scorefont.render("Score " + str(score), 1, (255,255,255))
        screen.blit(label, (0, 0))
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and
                    e.key in (pygame.K_q, pygame.K_ESCAPE)):
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                # only bases that are armed can fire. Bases take a while to
                # re-arm themselves after they fire. This is to prevent the
                # player from being invincible by just spamming defensive
                # missiles super fast. It's also an incentive to save all of
                # your bases instead of just saving one.
                armed = [b for b in bases if b.armed_in == 0]
                if armed:
                    dest = Point(*pygame.mouse.get_pos())
                    # Choose the armed base closest to the destination.
                    base = sorted(armed, cmp=lambda a,b: \
                            int(dist(a.pos, dest) - dist(b.pos, dest)))[0]
                    pos = Point(base.pos.x, height-20)
                    base.armed_in = 25
                    # create a new defenesive missile.
                    missiles.append(Missile(pos=pos, dest=dest, tail=1, icbm=0,
                            v=aim_at(pos, dest, 5), color=(160, 255, 220)))
        for base in bases:
            base.armed_in = max(0, base.armed_in - 1)
            pygame.draw.circle(screen, (0, 0, 255), base.pos, 20)
            pygame.draw.circle(screen, (0, 255, 99),
                    (base.pos.x, base.pos.y-20+base.armed_in), 5)
        new_explosions = []
        new_missiles = []
        for m in missiles:
            m.pos = add_scaled_vector(m.pos, m.v, 1)
            pygame.draw.aaline(screen, m.color, m.pos,
                    add_scaled_vector(m.pos, m.v, -m.tail), 8)
            # Missiles turn into explosions when they reach their destinations
            if dist(m.pos, m.dest) < 5:
                m.alive = 0
                new_explosions.append(Explosion(pos=m.pos, age=1))
            elif m.icbm == m.pos.y and len(bases) > 1 and 0 < m.pos.x < 900:
                m.alive = 0
                for base in bases:
                    new_missiles.append(Missile(pos=m.pos, dest=base.pos,
                            v=aim_at(m.pos, base.pos, (600-m.pos.y)/3),
                            color=(250, 0, 0), tail=5, icbm=0))
        missiles += new_missiles
        for ex in explosions:
            r = int(radius(ex.age))
            # Only explosions can collide with anything. Check for
            # collisions with bases and missiles here.
            for base in bases:
                # We allow explosions to be pretty close to bases because
                # it's lame to accidentally blow up your own base.
                if dist(base.pos, ex.pos) < r * 2/3:
                    base.alive = 0
                    new_explosions.append(Explosion(pos=base.pos, age=1))
            for m in missiles:
                if m.alive and dist(m.pos, ex.pos) <= r:
                    m.alive = 0
                    # To save lines, use the red component of the missile color
                    # to give points for killing incoming missiles without
                    # giving points for killing our own missiles. Incoming
                    # missiles have red=250 while defensive missiles have
                    # red=0.
                    score += m.color[0] * (len(bases) if m.icbm > 0 else 1)
                    new_explosions.append(Explosion(pos=m.pos, age=1))
            pygame.draw.circle(screen, (200, 0, 0), snap(ex.pos), r)
            ex.age += 1
        for ex in explosions: # paint inner part in separate pass, looks better
            r = int(radius(ex.age) * (30-ex.age) / 30)
            pygame.draw.circle(screen, (255, 150, 0), snap(ex.pos), r)
        # Remove old explosions, dead bases and missiles.
        explosions = [x for x in explosions + new_explosions if x.age < 29]
        bases[:] = [x for x in bases if x.alive]
        missiles[:] = [x for x in missiles if x.alive]
        clock.tick(30)
        pygame.display.flip()
    score += round_num * 1000 + len(bases) * 2500
