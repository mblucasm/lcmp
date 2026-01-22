from __future__ import annotations

import pygame
import modules.rgb as rgb

import pygame.freetype
pygame.freetype.init()

from enum import IntEnum
from typing import Callable, Any
from dataclasses import dataclass

LinesType = tuple[list[str], list[tuple[int, int]]]

# TODO: Change everything related to RobotoMono
class RobotoMono(pygame.freetype.Font):

    def __init__(self, file: str, size: float = 0, font_index: int = 0, resolution: int = 0, ucs4: int = False) -> None:
        super().__init__(file, size, font_index, resolution, ucs4)

    @staticmethod
    def advance(size: float) -> int:
        return round(3/5 * size)

    @staticmethod
    def get_chars_per_line(rect_width: float, size: float) -> int:
        return round(rect_width / RobotoMono.advance(size))

    @staticmethod
    def split(text: str, size: float, rect_width: float, start: int = 0) -> LinesType:

        charsperline = RobotoMono.get_chars_per_line(rect_width, size)

        lines: list[str] = []
        data_result: list[tuple[int, int]] = []

        parrs = text.split('\n')
        parrs = parrs[start:]

        for parr in parrs:

            lines.append("")
            start_idx = len(lines) - 1

            words = parr.split()

            for word in words:
                prev_word = lines[-1]
                if len(prev_word) == 0:
                    lines[-1] = word
                elif len(prev_word) + 1 + len(word) <= charsperline:
                    lines[-1] += ' ' + word
                else:
                    lines.append(word)

            end_idx = len(lines) - 1
            data_result.append((start_idx, end_idx))

        return lines, data_result

# TODO: Change everything related to RobotoMono
FONT = RobotoMono("roboto/static/RobotoMono-Regular.ttf")

class TextPos(IntEnum):
    NORTHWEST = 0
    CENTERED  = 1

@dataclass
class Rect:

    x: float
    y: float
    w: float
    h: float

    def scaled(self, x: float, y: float) -> Rect:
        return Rect(x * self.x, y * self.y, x * self.w, y * self.h)

    def deflated(self, x: float, y: float) -> Rect:
        reduceHoriz = x * self.w
        reduceVerti = y * self.h
        return Rect(
            self.x + reduceHoriz / 2,
            self.y + reduceVerti / 2,
            self.w - reduceHoriz,
            self.h - reduceVerti
        )

    def collides_with(self, x: float, y: float) -> bool:
        return (self.x <= x) and (x <= self.x + self.w) and (self.y <= y) and (y <= self.y + self.h)

    def totuple(self) -> tuple[float, float, float, float]:
        return self.x, self.y, self.w, self.h

    def copy(self) -> Rect:
        return Rect(self.x, self.y, self.w, self.h)

class TextBox:

    TEXT_RECT_DEFLATION_FACTOR = 0.05
    SCROLLBAR_WIDTH_REDUCTION_FACTOR = TEXT_RECT_DEFLATION_FACTOR * 0.5 * 0.5

    def __init__(
            self,
            rect: Rect,
            text: str,
            size: float,
            textpos: TextPos = TextPos.NORTHWEST,
            textcolor: rgb.Rgb = rgb.WHITE,
            rectcolor: rgb.Rgb | None = None,
            scrollbarcolor: rgb.Rgb | None = None,
            start: int = 0,
            isscrollable: bool = False,
            isvisible: bool = True,
        ) -> None:

        # TODO: all this needs to be changed
        assert FONT.name == "Roboto Mono"

        self.isscrollable = isscrollable

        self._rect = rect
        self._text = text
        self._size = size
        self._textpos = textpos
        self._start = start

        self.textcolor = textcolor
        self.rectcolor = rectcolor
        self.scrollbarcolor = scrollbarcolor
        self.isvisible = isvisible

        self._sw: int | None = None
        self._sh: int | None = None

        self._cached: dict[str, LinesType | list[Rect] | int | None] = {
            "lines": None,
            "line-rects": None,
            "parr-rects": None,
            "line-frames": None,
            "parr-frames": None,
        }

    def reset_cached(self) -> None:
        for key in self._cached.keys():
            self._cached[key] = None

    def set_screen_size(self, screen: pygame.Surface) -> None:
        sw, sh = screen.get_size()
        if sw != self._sw or sh != self._sh:
            self._sw = sw
            self._sh = sh
            self.reset_cached()

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, rect: Rect) -> None:
        self.reset_cached()
        self._rect = rect

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        self.start = 0
        self.reset_cached()
        self._text = text

    @property
    def size(self) -> float:
        return self._size

    @size.setter
    def size(self, size: float) -> None:
        self.reset_cached()
        self._size = size

    @property
    def textpos(self) -> TextPos:
        return self._textpos

    @textpos.setter
    def textpos(self, textpos: TextPos) -> None:
        self.reset_cached()
        self._textpos = textpos

    @property
    def start(self) -> int:
        return self._start

    @start.setter
    def start(self, start: int) -> None:
        self.reset_cached()
        self._start = start

    def scroll_parrs(self, mouseX: int, mouseY: int, screen: pygame.Surface, delta_start: int) -> None:

        if not self.isscrollable:
            return

        _, parrs = self.get_lines(screen)
        assert self._sw is not None and self._sh is not None

        if not self.rect.scaled(self._sw, self._sh).collides_with(mouseX, mouseY):
            return

        total_parrs = self.start + len(parrs)

        if self.start + delta_start < 0:
            self.start = 0
            return

        if self.start + delta_start >= total_parrs:
            self.start = total_parrs - 1
            return

        self.start += delta_start

    def get_lines(self, screen: pygame.Surface) -> LinesType:

        self.set_screen_size(screen)
        assert self._sw is not None and self._sh is not None

        if self._cached["lines"] is None:
            self._cached["lines"] = FONT.split(self.text, self.size, self.rect.w * self._sw, self.start)

        assert isinstance(self._cached["lines"], tuple)
        return self._cached["lines"]

    def get_parr_rects(self, screen: pygame.Surface) -> list[Rect]:

        assert len(TextPos) == 2

        lines, data = self.get_lines(screen)
        assert self._sw is not None and self._sh is not None

        nparrs = len(data)
        nlines = len(lines)

        if self._cached["parr-rects"] is None:

            self._cached["parr-rects"] = []
            advance = FONT.advance(self.size)
            base_rect = self.rect.scaled(self._sw, self._sh).deflated(self.TEXT_RECT_DEFLATION_FACTOR, self.TEXT_RECT_DEFLATION_FACTOR)

            if self.textpos == TextPos.NORTHWEST:
                for i in range(nparrs):
                    self._cached["parr-rects"].append(base_rect.copy())
                    self._cached["parr-rects"][i].h = (data[i][1] - data[i][0] + 1) * self.size
                    self._cached["parr-rects"][i].y += data[i][0] * self.size
                    self._cached["parr-rects"][i].w = max([len(line) for line in lines[data[i][0]:data[i][1]+1]]) * advance

            elif self.textpos == TextPos.CENTERED:
                for i in range(nparrs):
                    self._cached["parr-rects"].append(base_rect.copy())
                    width = max([len(line) for line in lines[data[i][0]:data[i][1]+1]]) * advance
                    self._cached["parr-rects"][i].x += (self._cached["parr-rects"][i].w - width) / 2
                    self._cached["parr-rects"][i].y += self._cached["parr-rects"][i].h / 2 - nlines * self.size / 2 + data[i][0] * self.size
                    self._cached["parr-rects"][i].w = width
                    self._cached["parr-rects"][i].h = (data[i][1] - data[i][0] + 1) * self.size

        assert isinstance(self._cached["parr-rects"], list)
        return self._cached["parr-rects"]

    def get_parr_frames(self, screen: pygame.Surface) -> list[Rect]:

        assert len(TextPos) == 2

        lines, data = self.get_lines(screen)
        assert self._sw is not None and self._sh is not None

        nparrs = len(data)
        nlines = len(lines)

        if self._cached["parr-frames"] is None:

            self._cached["parr-frames"] = []
            base_frame = self.rect.scaled(self._sw, self._sh).deflated(self.TEXT_RECT_DEFLATION_FACTOR, self.TEXT_RECT_DEFLATION_FACTOR)

            if self.textpos == TextPos.NORTHWEST:
                for i in range(nparrs):
                    self._cached["parr-frames"].append(base_frame.copy())
                    self._cached["parr-frames"][i].h = (data[i][1] - data[i][0] + 1) * self.size
                    self._cached["parr-frames"][i].y += data[i][0] * self.size

            elif self.textpos == TextPos.CENTERED:
                for i in range(nparrs):
                    self._cached["parr-frames"].append(base_frame.copy())
                    self._cached["parr-frames"][i].y += self._cached["parr-frames"][i].h / 2 - nlines * self.size / 2 + data[i][0] * self.size
                    self._cached["parr-frames"][i].h = (data[i][1] - data[i][0] + 1) * self.size

        assert isinstance(self._cached["parr-frames"], list)
        return self._cached["parr-frames"]

    def get_line_rects(self, screen: pygame.Surface) -> list[Rect]:

        assert len(TextPos) == 2

        lines, _ = self.get_lines(screen)
        nlines = len(lines)
        assert self._sw is not None and self._sh is not None

        if self._cached["line-rects"] is None:

            self._cached["line-rects"] = []
            advance = FONT.advance(self.size)
            base_rect = self.rect.scaled(self._sw, self._sh).deflated(self.TEXT_RECT_DEFLATION_FACTOR, self.TEXT_RECT_DEFLATION_FACTOR)

            if self.textpos == TextPos.NORTHWEST:
                for i, line in enumerate(lines):
                    self._cached["line-rects"].append(base_rect.copy())
                    self._cached["line-rects"][i].y += i * self.size
                    self._cached["line-rects"][i].h = self.size
                    self._cached["line-rects"][i].w = len(line) * advance

            elif self.textpos == TextPos.CENTERED:
                for i, line in enumerate(lines):
                    self._cached["line-rects"].append(base_rect.copy())
                    width = len(line) * advance
                    self._cached["line-rects"][i].x += (self._cached["line-rects"][i].w - width) / 2
                    self._cached["line-rects"][i].y += self._cached["line-rects"][i].h / 2 - nlines * self.size / 2 + i * self.size
                    self._cached["line-rects"][i].h = self.size
                    self._cached["line-rects"][i].w = width

        assert isinstance(self._cached["line-rects"], list)
        return self._cached["line-rects"]

    def get_line_frames(self, screen: pygame.Surface) -> list[Rect]:

        assert len(TextPos) == 2

        nlines = len(self.get_lines(screen)[0])
        assert self._sw is not None and self._sh is not None

        if self._cached["line-frames"] is None:

            self._cached["line-frames"] = []
            base_frame = self.rect.scaled(self._sw, self._sh).deflated(self.TEXT_RECT_DEFLATION_FACTOR, self.TEXT_RECT_DEFLATION_FACTOR)

            if self.textpos == TextPos.NORTHWEST:
                for i in range(nlines):
                    self._cached["line-frames"].append(base_frame.copy())
                    self._cached["line-frames"][i].y += i * self.size
                    self._cached["line-frames"][i].h = self.size

            elif self.textpos == TextPos.CENTERED:
                for i in range(nlines):
                    self._cached["line-frames"].append(base_frame.copy())
                    self._cached["line-frames"][i].y += self._cached["line-frames"][i].h / 2 - nlines * self.size / 2 + i * self.size
                    self._cached["line-frames"][i].h = self.size

        assert isinstance(self._cached["line-frames"], list)
        return self._cached["line-frames"]

    def get_scrollbar(self, screen: pygame.Surface) -> tuple[Rect, Rect]:

        _, parrs = self.get_lines(screen)
        assert self._sw is not None and self._sh is not None

        rect = self.rect.scaled(self._sw, self._sh).deflated(0, self.TEXT_RECT_DEFLATION_FACTOR)
        width = min(rect.w * self.TEXT_RECT_DEFLATION_FACTOR / 4, 2)
        x = rect.x + rect.w - 3 / 2 * width

        total_parrs = self.start + len(parrs)
        y = rect.y + self.start / total_parrs * rect.h
        h = max(1, rect.h / total_parrs)

        return Rect(x, rect.y, width, rect.h), Rect(x, y, width, h)

    def draw(self, screen: pygame.Surface) -> None:

        if not self.isvisible:
            return

        lines, _ = self.get_lines(screen)
        rects = self.get_line_rects(screen)

        assert len(lines) == len(rects)
        assert self._sw is not None and self._sh is not None

        if self.rectcolor is not None:
            rect = self.rect.scaled(self._sw, self._sh)
            pygame.draw.rect(screen, self.rectcolor, rect.totuple())

        if self.scrollbarcolor is not None:
            bar, mark = self.get_scrollbar(screen)
            pygame.draw.rect(screen, self.scrollbarcolor, bar.totuple())
            pygame.draw.rect(screen, rgb.comp(self.scrollbarcolor), mark.totuple())

        for line, rect in zip(lines, rects):
            surf, _ = FONT.render(line, self.textcolor, size = self.size)
            screen.blit(surf, rect.totuple())

class Button(TextBox):

    def __init__(
            self,
            rect: Rect,
            text: str,
            size: float,
            textpos: TextPos = TextPos.NORTHWEST,
            textcolor: rgb.Rgb = rgb.WHITE,
            rectcolor: rgb.Rgb | None = None,
            scrollbarcolor: rgb.Rgb | None = None,
            start: int = 0,
            isscrollable: bool = False,
            isvisible: bool = True,
            callback: Callable[[Any], Any] | None = None,
            parrcallback: Callable[[int, Any], Any] | None = None
        ) -> None:

            super().__init__(
                rect = rect,
                text = text,
                size = size,
                textpos = textpos,
                textcolor = textcolor,
                rectcolor = rectcolor,
                scrollbarcolor = scrollbarcolor,
                start = start,
                isscrollable = isscrollable,
                isvisible = isvisible,
            )

            self.callback: Callable[[Any], Any] | None = callback
            self.parrcallback: Callable[[int, Any], Any] | None = parrcallback

    def click(self, normalizedMouseX: float, normalizedMouseY: float, args: Any) -> tuple[bool, Any]:

        if not self.isvisible:
            return False, None

        if self.callback is not None and self.rect.collides_with(normalizedMouseX, normalizedMouseY):
            return True, self.callback(args)

        return False, None

    def click_parr(self, mouseX: int, mouseY: int, screen: pygame.Surface, args: Any) -> tuple[bool, Any]:

        if not self.isvisible:
            return False, None

        if self.parrcallback is None:
            return False, None

        frames = self.get_parr_frames(screen)
        for i, frame in enumerate(frames):
            if frame.collides_with(mouseX, mouseY):
                return True, self.parrcallback(i, args)

        return False, None

@dataclass
class Scene:

    textboxes: dict[str, TextBox]
    buttons: dict[str, Button]

    def draw(self, screen: pygame.Surface) -> None:
        for textbox in self.textboxes.values():
            textbox.draw(screen)
        for button in self.buttons.values():
            button.draw(screen)

if __name__ == "__main__":
    print(f"{__file__}: This is a module")
