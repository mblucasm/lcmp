Rgb  = tuple[int, int, int]

def fromhex(hex: int) -> Rgb:
    return (
        (hex & 0xff0000) >> (4 * 4),
        (hex & 0x00ff00) >> (2 * 4),
        (hex & 0x0000ff) >> (0 * 4),
    )

def comp(rgb: Rgb) -> Rgb:
    return (
        0xff - rgb[0],
        0xff - rgb[1],
        0xff - rgb[2],
    )

BLACK      = fromhex(0x000000)
WHITE      = fromhex(0xffffff)
RED        = fromhex(0xff0000)
GREEN      = fromhex(0x00ff00)
DARK_GREEN = fromhex(0x06402b)
BLUE       = fromhex(0x0000ff)
YELLOW     = fromhex(0xffff00)
DARK_GRAY  = fromhex(0x181818)
LIGHT_GRAY = fromhex(0x404040)
GARNET     = fromhex(0x5c0820)
ORANGE     = fromhex(0xffa010)

if __name__ == "__main__":
    print(f"{__file__}: This is a module")
