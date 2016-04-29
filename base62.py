#!/usr/bin/python
import string

# 0-9a-zA-Z
BASE62 = string.digits + string.ascii_letters


def to_base62(integer):
    assert integer >= 0
    div, mod = divmod(integer, 62)
    if div > 0:
        return to_base62(div) + BASE62[mod]
    return BASE62[mod]


def from_base62(base62):
    assert base62 != ''
    integer = 0
    for char in base62:
        integer *= 62
        integer += BASE62.find(char)
    return integer


if __name__ == "__main__":
    for i in [0, 1, 5, 62, 620, 9999]:
        assert from_base62(to_base62(i)) == i
