from pico2d import *

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720


def handle_events():
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False


def reset_world():
    global running

    running = True


def update_world():
    pass


def render_world():
    pass


open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
reset_world()

while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

close_canvas()
