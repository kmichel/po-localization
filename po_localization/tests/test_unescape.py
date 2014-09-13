# coding=utf-8

from __future__ import absolute_import
from __future__ import unicode_literals

from unittest import TestCase
from ..unescape import unescape, UnescapeError


class UnescapeTestCase(TestCase):
    def test_empty(self):
        self.assertEqual("", unescape(""))

    def test_simple(self):
        self.assertEqual("First\nSecond", unescape(r"First\nSecond"))

    def test_multiple(self):
        self.assertEqual("\a \b \f \n \r \t \v \\ \"", unescape(r"\a \b \f \n \r \t \v \\ \""))

    def test_octal_escape(self):
        self.assertEqual("e", unescape(r"\145"))
        self.assertEqual("€", unescape(r"\20254"))

    def test_hexadecimal_escape(self):
        self.assertEqual("e", unescape(r"\x65"))
        self.assertEqual("€", unescape(r"\x20ac"))
        self.assertEqual("€", unescape(r"\x20AC"))
        self.assertEqual("€", unescape(r"\x20aC"))

    def test_unfinished_escape(self):
        self.assertRaises(UnescapeError, unescape, "\\")

    def test_invalid_escape(self):
        self.assertRaises(UnescapeError, unescape, "\\FAIL")
