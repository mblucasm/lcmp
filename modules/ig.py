from __future__ import annotations

import os

from pathlib import Path
from enum import IntEnum
from html.parser import HTMLParser

class Unreachable(RuntimeError):
    ...

class InvalidInstagramDir(Exception):
    ...

class Target(IntEnum):
    FOLLOWING = 0
    FOLLOWERS = 1

class UsersExtractor(HTMLParser):

    def __init__(self):
        super().__init__()
        self.users: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "a":
            for attr, userlink in attrs:
                if attr == "href" and userlink is not None:
                    username = userlink[userlink.rfind('/')+1:]
                    self.users[username] = userlink

class Date:

    def __init__(self, year: int, month: int, day: int) -> None:
        self.year = year
        self.month = month
        self.day = day
        self.str = f"{self.year:04d}-{self.month:02d}-{self.day:02d}"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Date):
            return self.year == other.year and self.month == other.month and self.day == other.day
        return False
    
    def __lt__(self, other: Date) -> bool:
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __gt__(self, other: Date) -> bool:
        return (self.year, self.month, self.day) > (other.year, other.month, other.day)

class InstagramDir:
    
    def __init__(self, dirpath: str) -> None:
        self.path = dirpath
        self.date = self.ensure_valid_name()
        self.ensure_valid_tree()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, InstagramDir):
            return (self.username, self.date, self.uuid) == (other.username, other.date, other.uuid)
        return False
    
    def ensure_valid_name(self) -> Date:

        stem = Path(self.path).stem

        try:
            instagram, username, year, month, day, uuid, *_ = stem.split('-')
        except:
            raise InvalidInstagramDir(f"Folder name '{stem}' is invalid\nMust be instagram-USERNAME-YEAR-MONTH-DAY-UUID")

        if len(_) != 0:
            raise InvalidInstagramDir(f"Folder name '{stem}' is invalid\nMust be instagram-USERNAME-YEAR-MONTH-DAY-UUID")

        if instagram != "instagram":
            raise InvalidInstagramDir(f"Couldn't find 'instagram' in folder's name\n'{stem}'")

        if len(username) == 0:
            raise InvalidInstagramDir(f"Couldn't find USERNAME in folder's name\n'{stem}'")

        if len(year) != 4 or not year.isnumeric():
            raise InvalidInstagramDir(f"Invalid year found in folder's name\n'{stem}'")

        if len(month) != 2 or not month.isnumeric():
            raise InvalidInstagramDir(f"Invalid month found in folder's name\n'{stem}'")

        if len(day) != 2 or not day.isnumeric():
            raise InvalidInstagramDir(f"Invalid day found in folder's name\n'{stem}'")

        if len(uuid) == 0:
            raise InvalidInstagramDir(f"Couldn't find UUID in folder's name\n'{stem}'")
        
        self.uuid = uuid
        self.username = username

        return Date(int(year), int(month), int(day))

    def ensure_valid_tree(self) -> None:
        
        connections = os.path.join(self.path, "connections")
        if not os.path.exists(connections) or not os.path.isdir(connections):
            raise InvalidInstagramDir(f"Couldn't find subfolder 'connections'\n{connections}")

        followers_and_following = os.path.join(connections, "followers_and_following")
        if not os.path.exists(followers_and_following) or not os.path.isdir(followers_and_following):
            raise InvalidInstagramDir(f"Couldn't find subfolder 'followers_and_following'\n{followers_and_following}")

        following = os.path.join(followers_and_following, "following.html")
        if not os.path.exists(following) or not os.path.isfile(following):
            raise InvalidInstagramDir(f"Couldn't find file 'following.html'\n{following}")

        followers = os.path.join(followers_and_following, "followers_1.html")
        if not os.path.exists(followers) or not os.path.isfile(followers):
            raise InvalidInstagramDir(f"Couldn't find file 'followers_1.html'\n{followers}")

def file_get_contents(filepath: str, mode: str = 'r', encoding: str | None = None) -> str:
    with open(filepath, mode = mode, encoding = encoding) as f:
        return f.read()

def extract_from(instagram_dir: str, target: Target) -> dict[str, str]:

    assert len(Target) == 2

    parser = UsersExtractor()

    if target == Target.FOLLOWING:
        html = file_get_contents(os.path.join(instagram_dir, "connections", "followers_and_following", "following.html"))
        parser.feed(html)

    elif target == Target.FOLLOWERS:
        i = 1
        try:
            while True:
                html = file_get_contents(os.path.join(instagram_dir, "connections", "followers_and_following", f"followers_{i}.html"))
                parser.feed(html)
                i += 1
        except FileNotFoundError:
            if i == 1:
                raise
    
    else:
        raise Unreachable()

    return parser.users

if __name__ == "__main__":
    print(f"{__file__}: This is a module")
