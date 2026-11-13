# 레이어 0: 배경 객체 (배경, 바닥)
# 레이어 1: 앞쪽 객체 (선수, 공, 골대, 이펙트)
# 레이어 2: UI (점수, 타이머)

world = [[], [], []]


def add_object(o, depth=0):
    world[depth].append(o)


def add_objects(ol, depth=0):
    world[depth] += ol


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return

    raise ValueError('Cannot delete non existing object')


def update():
    for layer in world:
        for o in layer:
            o.update()


def render():
    for layer in world:
        for o in layer:
            o.draw()
