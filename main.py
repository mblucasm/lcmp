from __future__ import annotations

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import bisect
import webbrowser

import modules.ig as ig
import modules.rgb as rgb

from urllib.parse import urlparse
from modules.gui import Scene, TextBox, Button, Rect, TextPos
from modules.ig import InstagramDir, Target, InvalidInstagramDir
from modules.utils import Unreachable, State, ErrorType, Method, get_uuid_if_needed

state = State()

FPS = 60
SIZE = (1280, 720)
ERRORLIFETIME = 5 * FPS
CAPTION = "lcmp | Inspect your instagram's followers & following (github.com/mblucasm/lcmp)"
LOGO_PATH = "assets/logo.svg"

WELCOME_SCENE = Scene(
    buttons = {},
    textboxes = {
        "main": TextBox(
            rect = Rect(0, 0, 1, 1),
            text = "To get started\nDrag & Drop\nYour folders here",
            size = 60,
            textpos = TextPos.CENTERED,
        ),
        "info": TextBox(
            rect = Rect(0, 0, 1, 0.1),
            text = "Folder's name must be: instagram-USERNAME-YEAR-MONTH-DAY-UUID",
            size = 10,
            textpos = TextPos.CENTERED,
        ),
    },
)

MAIN_SCENE = Scene(
    buttons = {
        "dir-list": Button(
            rect = Rect(0, 0, 0.2, 1),
            text = "",
            size = 30,
            rectcolor = rgb.LIGHT_GRAY,
            scrollbarcolor = rgb.WHITE,
            isscrollable = True,
        ),
        "user-list": Button(
            rect = Rect(0.2, 0.1, 0.7, 0.9),
            text = "",
            size = 15,
            isscrollable = True,
            scrollbarcolor = rgb.WHITE,
            isvisible = False,
        ),
        "switch-target": Button(
            rect = Rect(0.91, 0.6, 0.08, 0.09),
            text = "Click to switch target",
            size = 15,
            rectcolor = rgb.RED,
            textpos = TextPos.CENTERED,
            isvisible = False,
        ),
        "switch-method": Button(
            rect = Rect(0.91, 0.7, 0.08, 0.09),
            text = "Click to switch method",
            size = 15,
            rectcolor = rgb.BLUE,
            textpos = TextPos.CENTERED,
            isvisible = False,
        ),
    },
    textboxes = {
        "phrases": TextBox(
            rect = Rect(0.2, 0, 0.8, 0.1),
            text = "Select up to two folders from the left",
            size = 30,
            rectcolor = rgb.WHITE,
            textcolor = rgb.BLACK,
            textpos = TextPos.CENTERED,
        ),
        "n-users-displayed": TextBox(
            rect = Rect(0.91, 0.8, 0.08, 0.09),
            text = "",
            size = 15,
            isvisible = False,
            textpos = TextPos.CENTERED,
        ),
        "n-selections": TextBox(
            rect = Rect(0.91, 0.9, 0.08, 0.09),
            text = "Number of selections: 0",
            size = 15,
            textpos = TextPos.CENTERED,
        ),
    },
)

def create_new_error(etype: ErrorType, msg: str) -> None:

    global state
    assert len(ErrorType) == 3

    if etype == ErrorType.INFO:
        state.error.rectcolor = rgb.DARK_GREEN
    elif etype == ErrorType.WARNING:
        state.error.rectcolor = rgb.ORANGE
    elif etype == ErrorType.ERROR:
        state.error.rectcolor = rgb.RED
    else:
        raise Unreachable

    state.error.text = msg
    state.errortimer = ERRORLIFETIME

def issafeurl(url: str) -> bool:

    try:
        parsed = urlparse(url.strip())
    except Exception:
        create_new_error(ErrorType.ERROR, f"{url} is not valid")
        return False

    if parsed.scheme.lower() != "https":
        create_new_error(ErrorType.ERROR, f"{url} is not safe. Protocol needs to be https")
        return False

    host = parsed.hostname
    if host is None:
        create_new_error(ErrorType.ERROR, f"{url} is not safe. Instagram is not the host")
        return False

    host = host.lower()
    if host != "instagram.com" and not host.endswith(".instagram.com"):
        create_new_error(ErrorType.ERROR, f"{url} is not safe. Instagram is not the host")
        return False

    if not parsed.path or parsed.path == "/":
        create_new_error(ErrorType.ERROR, f"{url} is not valid. Doesn't point to anything")
        return False

    return True

def mainscene_update_visuals() -> None:

    global state
    assert state.scenename == "main"

    assert state.scenes[state.scenename].buttons.get("user-list") is not None
    assert state.scenes[state.scenename].buttons.get("switch-target") is not None
    assert state.scenes[state.scenename].buttons.get("switch-method") is not None
    assert state.scenes[state.scenename].textboxes.get("phrases") is not None
    assert state.scenes[state.scenename].textboxes.get("n-selections") is not None
    assert state.scenes[state.scenename].textboxes.get("n-users-displayed") is not None

    nos = int(state.selected[0] is not None) + int(state.selected[1] is not None)

    if state.selected[0] is None:
        state.scenes[state.scenename].buttons["user-list"].isvisible = False
        state.scenes[state.scenename].textboxes["n-users-displayed"].isvisible = False
    else:
        state.scenes[state.scenename].buttons["user-list"].isvisible = True
        state.scenes[state.scenename].buttons["user-list"].text = "\n".join(user for user in state.users.keys())
        state.scenes[state.scenename].textboxes["n-users-displayed"].isvisible = True
        state.scenes[state.scenename].textboxes["n-users-displayed"].text = f"Displaying {len(state.users)} users"

    state.scenes[state.scenename].buttons["switch-target"].isvisible = state.selected[0] is not None and state.selected[1] is not None
    state.scenes[state.scenename].buttons["switch-method"].isvisible = state.selected[0] is not None
    state.scenes[state.scenename].textboxes["n-selections"].text = f"Number of selections: {nos}"
    state.scenes[state.scenename].textboxes["phrases"].text = get_phrase()

def mainscene_switch_method(_) -> None:

    global state
    assert state.scenename == "main"

    state.method = state.method.next()
    state_update_users()
    mainscene_update_visuals()

def mainscene_switch_target(_) -> None:

    assert len(Target) == 2

    global state
    assert state.scenename == "main"

    state.target = Target(1 - state.target)
    state_update_users()
    mainscene_update_visuals()

def state_update_users() -> None:

    global state

    if state.selected[0] is None:
        state.users.clear()
        return

    as_target = Target.FOLLOWERS if (state.selected[1] is None) or (state.target == Target.FOLLOWERS) else Target.FOLLOWING
    bs_target = Target.FOLLOWING if (state.selected[1] is None) or (state.target == Target.FOLLOWING) else Target.FOLLOWERS

    try:
        a = ig.extract_from(state.dirs[state.selected[0]].path, as_target)
        b = ig.extract_from(state.dirs[state.selected[0] if state.selected[1] is None else state.selected[1]].path, bs_target)

    except FileNotFoundError as e:
        # TODO: Maybe don't delete users selections, refigure them out
        state.selected = (None, None)
        state.users.clear()
        create_new_error(ErrorType.ERROR, f"Couldn't find {e.filename}. You probably renamed, moved or deleted some files. Restart lcmp and reload the folders if you want to select this one")
        return

    as_users = a.keys()
    bs_users = b.keys()

    if state.method == Method.XA:
        extracted_users = sorted(set(bs_users) - set(as_users))
    elif state.method == Method.AX:
        extracted_users = sorted(set(as_users) - set(bs_users))
    elif state.method == Method.AA:
        extracted_users = sorted(set(as_users) & set(bs_users))
    else:
        raise Unreachable

    merged = a | b
    state.users = {k: merged[k] for k in extracted_users}

def state_update_selected(listidx: int) -> None:

    global state

    if listidx not in state.selected:
        if state.selected[0] is None:
            state.selected = (listidx, None)
        elif state.selected[1] is None:
            state.selected = (state.selected[0], listidx) if listidx > state.selected[0] else (listidx, state.selected[0])
        else:
            create_new_error(ErrorType.WARNING, "Unselect one of the selected folders before selecting a new one")
    else:
        state.selected = (None, None) if state.selected[1] is None else (state.selected[0] + state.selected[1] - listidx, None)

def mainscene_click_folder(i: int, button: Button) -> None:

    global state
    assert state.scenename == "main"

    state_update_selected(button.start + i)
    state_update_users()
    mainscene_update_visuals()

def mainscene_click_user(i: int, button: Button) -> None:

    global state
    assert state.scenename == "main"
    assert state.scenes[state.scenename].buttons.get("user-list") is not None

    username = state.scenes[state.scenename].buttons["user-list"].text.split("\n")[button.start + i]
    if username != "" and (url := state.users[username]):
        if issafeurl(url):
            webbrowser.open(state.users[username])

# TODO: Refactor this
def get_phrase() -> str:
    global state
    assert len(Method) == 3 and len(Target) == 2

    if state.selected[0] is None and state.selected[1] is None:
        return "Select up to two folders from the left"

    if state.selected[1] is None:
        username = state.dirs[state.selected[0]].username
        if state.method == Method.XA:
            return f"People {username} is a fan of"
        if state.method == Method.AX:
            saxongenitive = "'" if username[-1] == 's' else "'s"
            return f"{username}{saxongenitive} fans"
        if state.method == Method.AA:
            return f"People {username} follows and follow {username} back"
        raise Unreachable()

    dir1 = state.dirs[state.selected[0]]
    dir2 = state.dirs[state.selected[1]]

    if state.target == Target.FOLLOWERS:

        if dir1.username == dir2.username:

            if dir1.date == dir2.date:
                create_new_error(ErrorType.WARNING, "Since the two selected folders have the same date, the order in which you added these folders matters. You should have dropped the eldest folder first")
                if state.method == Method.XA:
                    return f"Followers {dir1.username} gained (might be displaying LOST followers since adding order matters)"
                if state.method == Method.AX:
                    return f"Followers {dir1.username} lost (might be displaying LOST followers since adding order matters)"
                if state.method == Method.AA:
                    return f"Followers {dir1.username} kept"
                raise Unreachable()
            else:
                if state.method == Method.XA:
                    return f"Followers {dir1.username} gained"
                if state.method == Method.AX:
                    return f"Followers {dir1.username} lost"
                if state.method == Method.AA:
                    return f"Followers {dir1.username} kept"
                raise Unreachable()

        else:

            if dir1.date == dir2.date:
                if state.method == Method.XA:
                    return f"People who follow {dir2.username} but not {dir1.username}"
                if state.method == Method.AX:
                    return f"People who follow {dir1.username} but not {dir2.username}"
                if state.method == Method.AA:
                    return f"Followers {dir1.username} and {dir2.username} share"
                raise Unreachable()
            else:
                create_new_error(ErrorType.WARNING, "Comparing two different accounts on different dates. This is strange")
                if state.method == Method.XA:
                    return f"People who follow {dir2.username} but not {dir1.username}"
                if state.method == Method.AX:
                    return f"People who follow {dir1.username} but not {dir2.username}"
                if state.method == Method.AA:
                    return f"Followers {dir1.username} and {dir2.username} share"
                raise Unreachable()

    if state.target == Target.FOLLOWING:

        if dir1.username == dir2.username:

            if dir1.date == dir2.date:
                create_new_error(ErrorType.WARNING, "Since the two selected folders have the same date, the order in which you added these folders matters. You should have dropped the eldest folder first")
                if state.method == Method.XA:
                    return f"People {dir1.username} started following (might be displaying people who {dir1.username} STOPPED following since adding order matters)"
                if state.method == Method.AX:
                    return f"People {dir1.username} stopped following (might be displaying people who {dir1.username} STARTED following since adding order matters)"
                if state.method == Method.AA:
                    return f"People {dir1.username} kept following"
                raise Unreachable()
            else:
                if state.method == Method.XA:
                    return f"People {dir1.username} started following"
                if state.method == Method.AX:
                    return f"People {dir1.username} stopped following"
                if state.method == Method.AA:
                    return f"People {dir1.username} kept following"
                raise Unreachable()

        else:

            if dir1.date == dir2.date:
                if state.method == Method.XA:
                    return f"People {dir2.username} follows but {dir1.username} doesn't"
                if state.method == Method.AX:
                    return f"People {dir1.username} follows but {dir2.username} doesn't"
                if state.method == Method.AA:
                    return f"People both {dir1.username} and {dir2.username} follow"
                raise Unreachable()
            else:
                create_new_error(ErrorType.WARNING, "Comparing two different accounts on different dates. This is strange")
                if state.method == Method.XA:
                    return f"People {dir2.username} follows but {dir1.username} doesn't"
                if state.method == Method.AX:
                    return f"People {dir1.username} follows but {dir2.username} doesn't"
                if state.method == Method.AA:
                    return f"People both {dir1.username} and {dir2.username} follow"
                raise Unreachable()

    raise Unreachable()

def handle_dropfile(path: str) -> None:

    global state

    try:
        newdir = InstagramDir(path)
    except InvalidInstagramDir as e:
        create_new_error(ErrorType.ERROR, e.args[0])
        return

    if newdir not in state.dirs:

        state.scenename = "main"
        assert state.scenes[state.scenename].buttons["dir-list"] is not None

        bisect.insort(state.dirs, newdir, key = lambda x: x.date)
        state.scenes[state.scenename].buttons["dir-list"].text = f"> {state.dirs[0].username} {state.dirs[0].date.str} {get_uuid_if_needed(0, state.dirs)}"

        for i, folder in enumerate(state.dirs[1:], 1):
            state.scenes[state.scenename].buttons["dir-list"].text += f"\n> {folder.username} {folder.date.str} {get_uuid_if_needed(i, state.dirs)}"

        # TODO: Maybe don't delete users selections, refigure them out
        state.selected = (None, None)
        state_update_users()
        mainscene_update_visuals()

def main() -> None:

    global state

    state.scenename = str("welcome") # str("welcome") instead of "welcome" so Pylance doesn't complain with: "Condition will always evaluate to False since the types "Literal['welcome']" and "Literal['main']" have no overlapPylancereportUnnecessaryComparison"
    state.scenes = {
        "welcome": WELCOME_SCENE,
        "main": MAIN_SCENE,
    }

    state.scenes["main"].buttons["dir-list"].parrcallback  = mainscene_click_folder
    state.scenes["main"].buttons["user-list"].parrcallback = mainscene_click_user
    state.scenes["main"].buttons["switch-target"].callback = mainscene_switch_target
    state.scenes["main"].buttons["switch-method"].callback = mainscene_switch_method

    pygame.init()
    clock = pygame.time.Clock()

    window = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    pygame.display.set_caption(CAPTION)

    try:
        pygame.display.set_icon(pygame.image.load(LOGO_PATH))
    except Exception:
        ...

    running = True
    while running:

        ww, wh = window.get_size()
        mouseX, mouseY = pygame.mouse.get_pos()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    state.uppressed = True
                elif event.key == pygame.K_DOWN:
                    state.downpressed = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    state.uppressed = False
                elif event.key == pygame.K_DOWN:
                    state.downpressed = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in state.scenes[state.scenename].buttons.values():
                    button.click(mouseX / ww, mouseY / wh, None)
                    button.click_parr(mouseX, mouseY, window, button)

            if event.type == pygame.MOUSEWHEEL:
                for textbox in state.scenes[state.scenename].textboxes.values():
                    textbox.scroll_parrs(mouseX, mouseY, window, -event.y)
                for button in state.scenes[state.scenename].buttons.values():
                    button.scroll_parrs(mouseX, mouseY, window, -event.y)

            if event.type == pygame.DROPFILE:
                handle_dropfile(event.file)

        if state.uppressed:
            for textbox in state.scenes[state.scenename].textboxes.values():
                textbox.scroll_parrs(mouseX, mouseY, window, -1)
            for button in state.scenes[state.scenename].buttons.values():
                button.scroll_parrs(mouseX, mouseY, window, -1)
        if state.downpressed:
            for textbox in state.scenes[state.scenename].textboxes.values():
                textbox.scroll_parrs(mouseX, mouseY, window, 1)
            for button in state.scenes[state.scenename].buttons.values():
                button.scroll_parrs(mouseX, mouseY, window, 1)

        window.fill(rgb.DARK_GRAY)
        state.scenes[state.scenename].draw(window)

        if state.scenename == "main":
            button = state.scenes[state.scenename].buttons["dir-list"]
            frames = button.get_parr_frames(window)
            for sd in state.selected:
                if sd is not None:
                    relative_idx = sd - button.start
                    if 0 <= relative_idx < len(frames):
                        pygame.draw.rect(window, rgb.ORANGE, frames[relative_idx].totuple(), width = 1)

        if state.errortimer > 0:
            state.error.draw(window)
            state.errortimer -= 1

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
