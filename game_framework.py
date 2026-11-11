import time

running = None
stack = None
frame_time = 0.0


def change_mode(mode):
    global stack
    if (len(stack) > 0):
        # 현재 모드의 finish 호출
        stack[-1].finish()
        # 현재 모드 제거
        stack.pop()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    global stack
    if (len(stack) > 0):
        # 현재 모드의 finish 호출
        stack[-1].finish()
        # 현재 모드 제거
        stack.pop()

    # 이전 모드의 resume 호출
    if (len(stack) > 0):
        stack[-1].resume()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    start_mode.init()

    global frame_time
    frame_time = 0.0
    current_time = time.time()
    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()
        frame_time = time.time() - current_time
        current_time += frame_time

    # 스택에 남아 있는 모드들을 위에서부터 차례로 종료하고 제거
    while (len(stack) > 0):
        stack[-1].finish()
        stack.pop()
