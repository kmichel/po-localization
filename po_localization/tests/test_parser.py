# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from io import StringIO
from unittest import TestCase
from po_localization.parser import Parser, ParseError, parse_po_file, parse_po_filename
from po_localization.po_file import PoFile

class ParserTestCase(TestCase):
    def _parse_and_expect(self, file_content, expected_catalog):
        file_object = StringIO(file_content)
        self.assertDictEqual(expected_catalog, parse_po_file(file_object))

    def _parse_and_expect_failure(self, file_content):
        file_content = StringIO(file_content)
        self.assertRaises(ParseError, parse_po_file, file_content)

    def test_empty_file(self):
        self._parse_and_expect("", {})

    def test_comment(self):
        self._parse_and_expect("""
# Comment
""", {})

    def test_empty_line(self):
        self._parse_and_expect("""

""", {})

    def test_simple(self):
        self._parse_and_expect("""
msgid "Message to translate"
msgstr "Message translated"
""", {
            "Message to translate": "Message translated"
        })

    def test_unescaping(self):
        self._parse_and_expect(r"""
msgid "Line One\nLine Two"
msgstr "First Line\nSecond Line"
""", {
            "Line One\nLine Two": "First Line\nSecond Line"
        })

    def test_broken_unescaping(self):
        self._parse_and_expect_failure(r"""
msgid "Line One\"
"nLine Two"
msgstr "First Line\nSecond Line"
""")

    def test_header_not_in_catalog(self):
        self._parse_and_expect(r"""
msgid ""
msgstr ""
"Project-Id-Version: Django\n"

msgid "Message to translate"
msgstr "Message translated"
""", {
            "Message to translate": "Message translated"
        })

    def test_context(self):
        self._parse_and_expect("""
msgctxt "Context"
msgid "Message to translate"
msgstr "Translated message"
""", {
            "Context\x04Message to translate": "Translated message"
        })

    def test_plural(self):
        self._parse_and_expect("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""", {
            ("Message to translate", 0): "Translated message",
            ("Message to translate", 1): "Translated messages"
        })

    def test_context_and_plural(self):
        self._parse_and_expect("""
msgctxt "Context"
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""",
            {
                ("Context\x04Message to translate", 0): "Translated message",
                ("Context\x04Message to translate", 1): "Translated messages"
            })

    def test_unexpected_keywords(self):
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgctxt "Context"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgstr "Translated message"
msgid "Message to translate"
""")
        self._parse_and_expect_failure("""
poney "Poney"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message"
msgstr "Translated messages"
""")

    def test_duplicate_keywords(self):
        self._parse_and_expect_failure("""
msgctxt "Context"
msgctxt "Context"
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid "Message to translate"
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid "Message to translate"
msgstr "Translated message"
msgstr "Translated message"
""")

    def test_duplicate_plural_index(self):
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message"
msgstr[0] "Translated message again"
""")

    def test_early_termination(self):
        self._parse_and_expect_failure("""
msgctxt "Context"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
"... with continuation"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
# With comment
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"

""")

    def test_missing_string(self):
        self._parse_and_expect_failure("""
msgctxt
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid
msgstr "Translated Message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgstr
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0]
msgstr[1] "Translated messages"
""")

    def test_partial_string(self):
        self._parse_and_expect_failure("""
msgctxt "Context
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgstr "Translated message
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message
msgstr[1] "Translated messages"
""")

    def test_unexpected_index(self):
        self._parse_and_expect_failure("""
msgctxt[0] "Context"
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid[0] "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid "Message to translate"
msgstr[0] "Translated message"
""")
        self._parse_and_expect_failure("""
msgctxt "Context"
msgid "Message to translate"
msgid_plural[0] "Messages to translate"
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""")

    def test_unexpected_continuation(self):
        self._parse_and_expect_failure("""
"Continuation"
""")
        self._parse_and_expect_failure("""
msgctxt "context"
"Continuation"
""")

    def test_garbage_at_end(self):
        self._parse_and_expect_failure("""
msgctxt "Context" GARBAGE
msgid "Message to translate"
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate" GARBAGE
msgstr "Translated message"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgstr "Translated message" GARBAGE
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate" GARBAGE
msgstr[0] "Translated message"
msgstr[1] "Translated messages"
""")
        self._parse_and_expect_failure("""
msgid "Message to translate"
msgid_plural "Messages to translate"
msgstr[0] "Translated message" GARBAGE
msgstr[1] "Translated messages"
""")

    def test_real_file(self):
        filename = os.path.join(os.path.dirname(__file__), 'sample.po')
        self.assertDictEqual(parse_po_filename(filename), {
            ("Context\x04Message to translate", 0): "Message à traduire",
            ("Context\x04Message to translate", 1): "Messages à traduire",
        })

    def test_header_parsing(self):
        file_object = StringIO(r"""
msgid ""
msgstr ""
"Project-Id-Version: Django\n"
"Report-Msgid-Bugs-To: \n"
"Language-Team: French <None>\n"
"Language: fr\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Plural-Forms: nplurals=2; plural=(n > 1)\n"
""")
        po_file = PoFile()
        self.assertListEqual(po_file.header_fields, [])
        self.assertIsNone(po_file.get_nplurals())
        parser = Parser(po_file)
        parser.parse_po_file(file_object)
        self.assertListEqual(po_file.header_fields, [
            ('Project-Id-Version', 'Django'),
            ('Report-Msgid-Bugs-To', ''),
            ('Language-Team', 'French <None>'),
            ('Language', 'fr'),
            ('MIME-Version', '1.0'),
            ('Content-Type', 'text/plain; charset=UTF-8'),
            ('Content-Transfer-Encoding', '8bit'),
            ('Plural-Forms', 'nplurals=2; plural=(n > 1)')])
        self.assertEqual(po_file.get_nplurals(), 2)

    def test_exception_message(self):
        try:
            raise ParseError("filename.po", 42, "the error message")
        except ParseError as error:
            self.assertEqual("filename.po:42: the error message", "{}".format(error))

        try:
            raise ParseError("filename.po", None, "unexpected end of file")
        except ParseError as error:
            self.assertEqual("filename.po: unexpected end of file", "{}".format(error))

        try:
            raise ParseError(None, 42, "the error message")
        except ParseError as error:
            self.assertEqual("line 42: the error message", "{}".format(error))

        try:
            raise ParseError(None, None, "the error message")
        except ParseError as error:
            self.assertEqual("the error message", "{}".format(error))

