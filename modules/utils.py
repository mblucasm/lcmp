from __future__ import annotations

import modules.rgb as rgb

from enum import IntEnum
from modules.ig import InstagramDir, Target
from modules.gui import Scene, TextBox, TextPos, Rect

class Unreachable(RuntimeError):
    ...

class ErrorType(IntEnum):
    INFO = 0
    WARNING = 1
    ERROR = 2

class Method(IntEnum):

    XA = 0
    AX = 1
    AA = 2

    def next(self) -> Method:
        return Method((self + 1) % len(Method))

class State:

    scenes: dict[str, Scene] = {}
    scenename: str = ""

    dirs: list[InstagramDir] = []
    selected: tuple[int, int] | tuple[int, None] | tuple[None, None] = (None, None)

    method = Method.XA
    target = Target.FOLLOWERS

    users: dict[str, str] = {}

    uppressed: bool = False
    downpressed: bool = False

    errortimer = 0
    error = TextBox(
        rect = Rect(0, 0.9, 1, 0.1),
        text = "",
        size = 15,
        textpos = TextPos.CENTERED,
        rectcolor = rgb.RED,
    )

def should_add_uuid(i: int, dirs: list[InstagramDir]) -> bool:

    if i == 0:
        return False if len(dirs) == 1 else (dirs[0].date == dirs[1].date and dirs[0].username == dirs[1].username)

    if i == len(dirs) - 1:
        return (dirs[i].date == dirs[i-1].date and dirs[i].username == dirs[i-1].username)

    return (dirs[i].date == dirs[i-1].date and dirs[i].username == dirs[i-1].username) or \
           (dirs[i].date == dirs[i+1].date and dirs[i].username == dirs[i+1].username)

def get_uuid_if_needed(i: int, dirs: list[InstagramDir]) -> str:
    return "" if not should_add_uuid(i, dirs) else f"({dirs[i].uuid})"

if __name__ == "__main__":
    print(f"{__file__}: This is a module")
