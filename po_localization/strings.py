# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys

# PyCharm incorrectly flags \v as an invalid escape sequence in python regexp, hence the \x0b
ESCAPER = re.compile(r'[\a\b\f\n\r\t\x0b\\"]')
UNESCAPER = re.compile(r'\\(?:([abfnrtv\\"])|([0-7]+)|x([0-9a-fA-F]+)|(.))?')

unicode_chr = unichr if sys.version_info[0] == 2 else chr


def escape(string):
    return ESCAPER.sub(_escape_char, string)


def _escape_char(match):
    char = match.group(0)
    if char == '\a':
        return r'\a'
    elif char == '\b':
        return r'\b'
    elif char == '\f':
        return r'\f'
    elif char == '\n':
        return r'\n'
    elif char == '\r':
        return r'\r'
    elif char == '\t':
        return r'\t'
    elif char == '\v':
        return r'\v'
    elif char == '\\':
        return r'\\'
    else:
        return r'\"'


def unescape(escaped_string):
    return UNESCAPER.sub(_unescape_code, escaped_string)


def _unescape_code(match):
    if match.group(1) is not None:
        code = match.group(1)
        if code == 'a':
            return '\a'
        elif code == 'b':
            return '\b'
        elif code == 'f':
            return '\f'
        elif code == 'n':
            return '\n'
        elif code == 'r':
            return '\r'
        elif code == 't':
            return '\t'
        elif code == 'v':
            return '\v'
        else:
            return code
    elif match.group(2) is not None:
        return unicode_chr(int(match.group(2), base=8))
    elif match.group(3) is not None:
        return unicode_chr(int(match.group(3), base=16))
    else:
        raise UnescapeError("Invalid escape sequence: \\{}".format(match.group(4)))


class UnescapeError(Exception):
    pass
