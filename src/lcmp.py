from __future__ import annotations

from pathlib import Path
FILE = Path(__file__).stem

import sys
if len(sys.argv) <= 1 or sys.argv[1] != "launched":
    print(f"{FILE}: [ERROR]: This file is not supposed to be run directly. Run launcher.py")
    sys.exit(1)

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = '1'

import re
import bisect
import webbrowser

import pygame
from pygame import Surface

import pygame.freetype
pygame.freetype.init()
from pygame.freetype import Font

from typing import Literal
from dataclasses import dataclass

TARGET_FPS = 60
FONT = Font(None)
SIZE = (1280, 720)

PATTERN = r'"https://www\.instagram\.com/(?:_u/)?([^"]+)"'
PATHS: dict[str, str] = {
    "icon": "assets/logo.svg",
    "followers": "followers_1.html",
    "following": "following.html",
}

Rgb = tuple[int, int, int]
BLACK:      Rgb = (0x00, 0x00, 0x00)
WHITE:      Rgb = (0xFF, 0xFF, 0xFF)
LIGHT_GRAY: Rgb = (0xAA, 0xAA, 0xAA)
DARK_GRAY:  Rgb = (0x18, 0x18, 0x18)
RED:        Rgb = (0xFF, 0x00, 0x00)
GREEN:      Rgb = (0x00, 0xFF, 0x00)
BLUE:       Rgb = (0x00, 0x00, 0xFF)

def draw_text(screen: Surface, text: str, rect: Rect, color: Rgb, size: int | None = None, pos: Literal["centered"] | Literal["left"] | Literal["left-centered"] = "centered") -> None:

    assert pos in ("centered", "left", "left-centered")    

    size = size if size is not None else rect.get_suitable_font_size(FONT, text)
    tr = FONT.get_rect(text, size = size)

    if pos == "left":
        tr.topleft = rect.get_corner_ints()
    elif pos == "left-centered":
        tr.topleft = int(rect.x), int(rect.y + rect.h // 2 - size // 2)
    elif pos == "centered":
        tr.center = rect.get_center_ints()

    FONT.render_to(screen, tr.topleft, text, color, size = size)

@dataclass
class Folder:
    path: str
    user: str
    date_int: int
    date_str: str

@dataclass
class Rect:

    x: float
    y: float
    w: float
    h: float

    def totuple(self) -> tuple[float, float, float, float]:
        return self.x, self.y, self.w, self.h

    def scaled(self, x: float, y: float) -> Rect:
        return Rect(x * self.x, y * self.y, x * self.w, y * self.h)
    
    def deflate(self, x: float, y: float) -> Rect:
        assert 0 <= x and x <= 1 and 0 <= y and y <= 1
        xremoved = x * self.w / 2
        yremoved = y * self.h / 2
        self.x += xremoved
        self.y += yremoved
        self.w -= 2 * xremoved
        self.h -= 2 * yremoved
        return self
    
    def collides_with_point(self, x: float, y: float) -> bool:
        return self.x < x and x < self.x + self.w and self.y < y and y < self.y + self.h
    
    def get_corner_ints(self) -> tuple[int, int]:
        return int(self.x), int(self.y)
    
    def get_center_ints(self) -> tuple[int, int]:
        return int(self.x + self.w / 2), int(self.y + self.h / 2)

    def get_suitable_font_size(self, font: Font, text: str, min_size: int = 1, max_size: int = 200) -> int:
        best, lo, hi = min_size, min_size, max_size
        while lo <= hi:
            mid = (lo + hi) // 2
            rect = font.get_rect(text, size = mid)
            if rect.width <= self.w and rect.height <= self.h:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return best

class Scrollable:

    def __init__(self, rect: Rect, color: Rgb, lines: list[str], lines_color: Rgb, lines_background: Rgb | None = None, selected_background: Rgb | None = None, ndisplayed: int = 20) -> None:
        self.rect = rect
        self.color = color
        self.lines = lines
        self.lines_color = lines_color
        self.lines_background = lines_background
        self.selected_background = selected_background
        self.ndisplayed = ndisplayed
        self.lo = 0

    def get_visible_lines(self) -> tuple[int, int]:
        return self.lo, self.lo + self.ndisplayed

    def get_line_rect(self, idx: int, screen: Surface) -> Rect:

        sw, sh = screen.get_size()

        rect = self.rect.scaled(sw, sh)
        rect.h = self.rect.h * sh / self.ndisplayed
        rect.y += idx * rect.h
        rect.deflate(0.02, 0.01)
        return rect

    def scroll(self, y: int) -> None:

        newlo = self.lo - y
        if newlo < 0:
            self.lo = 0
            return
        
        totallines = len(self.lines)

        if newlo + self.ndisplayed > totallines:
            self.lo = max(0, totallines - self.ndisplayed)
            return
        
        self.lo = newlo
        
    def draw(self, screen: Surface, selections: list[int] | None = None, font_size: int | None = None, lines_pos: Literal["centered"] | Literal["left"] = "centered") -> None:

        sw, sh = screen.get_size()
        pygame.draw.rect(screen, self.color, self.rect.scaled(sw, sh).totuple())

        line_height = self.rect.h * sh / self.ndisplayed
        line_rect = self.get_line_rect(0, screen)

        lines = self.lines[self.lo : self.lo + self.ndisplayed]
        
        for i, line in enumerate(lines, self.lo):

            if selections is not None:
                color = self.selected_background if i in selections else self.lines_background
                if color is not None:
                    pygame.draw.rect(screen, color, line_rect.totuple())

            draw_text(screen, line, line_rect, self.lines_color, font_size, lines_pos)
            line_rect.y += line_height

@dataclass
class Button:

    rect: Rect
    color: Rgb
    text: str
    text_color: Rgb

    def draw(self, screen: Surface) -> None:
        sw, sh = screen.get_size()
        dst = self.rect.scaled(sw, sh)
        pygame.draw.rect(screen, self.color, dst.totuple())
        draw_text(screen, self.text, dst.deflate(0.1, 0.1), self.text_color)

from enum import IntEnum
class Method(IntEnum):

    XA = 0
    AX = 1
    AA = 2
    NMETHODS = 3
    
    @staticmethod
    def switch(current: Method) -> Method:
        return Method((current + 1) % Method.NMETHODS)
    
    @staticmethod
    def phrase(state: State) -> str:

        nselected = len(state.selected_folders)

        assert state.method in Method
        if nselected not in (1, 2):
            return ""

        if nselected == 1:
            if state.method == Method.XA:
                return "People you follow but DON'T follow back"
            if state.method == Method.AX:
                return "People who follow you but you DON'T follow back"
            if state.method == Method.AA:
                return "People you follow and follow you back"

        user1 = state.folders[min(state.selected_folders)].user
        user2 = state.folders[max(state.selected_folders)].user

        if state.comparing_followers:
            if user1 == user2:
                if state.method == Method.XA:
                    return "People who started following you"
                if state.method == Method.AX:
                    return "People who stopped following you"
                if state.method == Method.AA:
                    return "People who keep following you"
            if state.method == Method.XA:
                return f"People who follow {user2} that DON'T follow {user1}"
            if state.method == Method.AX:
                return f"People who follow {user1} that DON'T follow {user2}"
            if state.method == Method.AA:
                return f"People who follow {user1} and {user2}"

        if user1 == user2:
            if state.method == Method.XA:
                return "People you started following"
            if state.method == Method.AX:
                return "People you stopped following"
            if state.method == Method.AA:
                return "People you keep following"
        if state.method == Method.XA:
            return f"People {user2} follows but {user1} DOESN'T"
        if state.method == Method.AX:
            return f"People {user1} follows but {user2} DOESN'T"
        if state.method == Method.AA:
            return f"People {user1} and {user2} follow"

        assert False, "unreachable"

def date_from_str(date: str, sep: str = '-') -> int:
    split = list(map(int, date.split(sep)))
    return 10000 * split[0] + 100 * split[1] + split[2]

def find_nth(haystack: str, needle: str, n: int) -> int:
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return start

def folder_from_path(path: str) -> Folder | None:

    start = find_nth(path, '-', 1)
    end   = find_nth(path, '-', 2)

    if start == -1 or end == -1:
        return None
    
    user = path[start + 1 : end]

    start = find_nth(path, '-', 2)
    end   = find_nth(path, '-', 5)

    if start == -1 or end == -1:
        return None
    
    date = path[start + 1 : end]
    if len(date) != 10 or not date[:4].isdigit() or date[4] != '-' or not date[5:7].isdigit() or date[7] != '-' or not date[8:11].isdigit():
        return None

    return Folder(path, user, date_from_str(date), date)

def extract_from_root(root: str, target: str) -> list[str]:

    matches: list[str] = []
    path = os.path.join(root, "connections", "followers_and_following", PATHS[target])
    
    with open(path, "r") as f:
        contents = f.read()
        matches = re.findall(PATTERN, contents)

    return matches

def get_user_link(user: str) -> str:
    return f"https://www.instagram.com/{user.split(' ')[1]}"

class State:

    def __init__(self) -> None:

        self.method = Method(0)
        self.comparing_followers = True
        
        self.folders: list[Folder] = []
        self.selected_folders: list[int] = []

        method_used = Scrollable(Rect(0.82, 0.1, 0.17, 0.19), DARK_GRAY, ["Method used:" , ""], WHITE)
        method_used.ndisplayed = len(method_used.lines)

        comparing_used = Scrollable(Rect(0.82, 0.4, 0.17, 0.19), DARK_GRAY, ["Comparing:", ""], WHITE)
        comparing_used.ndisplayed = len(comparing_used.lines)

        self.scrollables = {
            "folders": Scrollable(Rect(0, 0, 0.2, 1), WHITE, [], WHITE, DARK_GRAY, GREEN),
            "results": Scrollable(Rect(0.21, 0.1, 0.6, 0.89), LIGHT_GRAY, [], BLACK, ndisplayed = 40),
            "method-used": method_used,
            "comparing-used": comparing_used,
        }

        self.buttons = {
            "switch-comparing": Button(Rect(0.82, 0.7, 0.17, 0.09), BLUE, f"Click to compare {"following" if self.comparing_followers else "followers"} instead", WHITE),
            "switch-method": Button(Rect(0.82, 0.8, 0.17, 0.09), RED, "Click to switch method", WHITE),
            "total-users": Button(Rect(0.82, 0.9, 0.17, 0.09), DARK_GRAY, "", WHITE),
        }

    def switch_method(self) -> None:
        self.method = Method.switch(self.method)

    def switch_comparing(self) -> None:
        self.comparing_followers = bool(1 - self.comparing_followers)
        self.buttons["switch-comparing"].text = f"Click to compare {"following" if self.comparing_followers else "followers"} instead"

    def update_results(self) -> None:

        nselected = len(self.selected_folders)

        self.scrollables["results"].lo = 0
        self.scrollables["results"].lines = []
        if nselected == 0 or nselected > 2:
            return

        as_target = "followers" if nselected == 1 or self.comparing_followers else "following"
        bs_target = "following" if nselected == 1 or not self.comparing_followers else "followers"

        a = extract_from_root(self.folders[min(self.selected_folders)].path, as_target)
        b = extract_from_root(self.folders[max(self.selected_folders)].path, bs_target)

        if self.method == Method.XA:
            lines = sorted(set(b) - set(a))
        elif self.method == Method.AX:
            lines = sorted(set(a) - set(b))
        elif self.method == Method.AA:
            lines = sorted(set(a) & set(b))
        else:
            assert False, "unreachable"

        self.scrollables["results"].lines = [f"{i + 1}. {line}" for i, line in enumerate(lines)]

def main() -> None:

    state = State()

    pygame.init()
    clock = pygame.time.Clock()

    screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
    pygame.display.set_caption(FILE)
    pygame.display.set_icon(pygame.image.load(PATHS["icon"]))

    running = True
    while running:

        sw, sh = screen.get_size()
        mx, my = pygame.mouse.get_pos()

        drawing_folders = len(state.folders) != 0
        drawing_results = len(state.selected_folders) > 0

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                if drawing_results and state.buttons["switch-method"].rect.scaled(sw, sh).collides_with_point(mx, my):
                    state.switch_method()
                    state.update_results()

                elif drawing_results and state.buttons["switch-comparing"].rect.scaled(sw, sh).collides_with_point(mx, my):
                    state.switch_comparing()
                    state.update_results()

                elif drawing_folders and state.scrollables["folders"].rect.scaled(sw, sh).collides_with_point(mx, my):
                    lo, hi = state.scrollables["folders"].get_visible_lines()
                    for i, folder in enumerate(state.scrollables["folders"].lines[lo : hi + 1]):
                        if state.scrollables["folders"].get_line_rect(i, screen).collides_with_point(mx, my):
                            if i + lo in state.selected_folders:
                                state.selected_folders.pop(state.selected_folders.index(i + lo))
                            elif len(state.selected_folders) < 2:
                                state.selected_folders.append(i + lo)

                            state.update_results()

                elif drawing_results and state.scrollables["results"].rect.scaled(sw, sh).collides_with_point(mx, my):
                    lo, hi = state.scrollables["results"].get_visible_lines()
                    for i, user in enumerate(state.scrollables["results"].lines[lo : hi + 1]):
                        if state.scrollables["results"].get_line_rect(i, screen).collides_with_point(mx, my):
                            webbrowser.open(get_user_link(user))

            if event.type == pygame.MOUSEWHEEL:
                for scrollable in state.scrollables.values():
                    if scrollable.rect.scaled(sw, sh).collides_with_point(mx, my):
                        scrollable.scroll(event.y)

            if event.type == pygame.DROPFILE:
                if os.path.isdir(event.file):
                    folder = folder_from_path(event.file)
                    if folder is not None:
                        if folder not in state.folders:
                            bisect.insort(state.folders, folder, key = lambda x: x.date_int)                        
                            state.scrollables["folders"].lines.insert(state.folders.index(folder), f"{folder.user} {folder.date_str}")
                    else:
                        print(f"{FILE}: [ERROR] Folder loading ({event.file}) was NOT successful, please try again. The expected folder name is instagram-USERNAME-YYYY-MM-DD-UUID (replacing uppercase letters with the corresponding data)")

        screen.fill(DARK_GRAY)

        if not drawing_folders:
            draw_text(screen, "Drag & Drop", Rect(0, 0, 1, 1).scaled(sw, sh).deflate(0.5, 0.5), WHITE)
        else:
            state.scrollables["folders"].draw(screen, state.selected_folders)

        if not drawing_results:
            if drawing_folders:
                draw_text(screen, "Select up to two folders", Rect(0.2, 0, 0.8, 1).scaled(sw, sh).deflate(0.5, 0.5), WHITE)
        else:

            state.scrollables["results"].draw(screen, [], int(0.95 * state.scrollables["results"].rect.h * sh / state.scrollables["results"].ndisplayed), "left")
            state.scrollables["method-used"].lines[1] = state.method.name
            state.scrollables["method-used"].draw(screen, [])

            state.buttons["switch-method"].draw(screen)

            dst = Rect(0.21, 0.01, 0.5, 0.08).scaled(sw, sh)
            draw_text(screen, Method.phrase(state), dst, WHITE, size = int(0.4 * dst.h), pos = "left-centered")

            state.buttons["total-users"].text = f"Total users: {len(state.scrollables["results"].lines)}"
            state.buttons["total-users"].draw(screen)

            if len(state.selected_folders) == 2:
                state.scrollables["comparing-used"].lines[1] = "Followers" if state.comparing_followers else "Following"
                state.scrollables["comparing-used"].draw(screen, [])
                state.buttons["switch-comparing"].draw(screen)

        pygame.display.flip()
        clock.tick(TARGET_FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
        