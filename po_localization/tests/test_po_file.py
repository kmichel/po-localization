# coding=utf-8

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from unittest import TestCase
from po_localization.po_file import PoFile


class PoFileTestCase(TestCase):
    def test_message(self):
        po_file = PoFile()
        entry = po_file.add_entry("message")
        self.assertEqual("message", entry.message)
        self.assertIn("message", po_file.entries)
        self.assertIs(entry, po_file.entries["message"])

    def test_message_with_plural(self):
        po_file = PoFile()
        entry = po_file.add_entry("message", "plural message")
        self.assertEqual("message", entry.message)
        self.assertEqual("plural message", entry.plural)
        self.assertIn("message", po_file.entries)
        self.assertIs(entry, po_file.entries["message"])

    def test_message_with_context(self):
        po_file = PoFile()
        entry = po_file.add_entry("message", context="context")
        self.assertEqual("message", entry.message)
        self.assertEqual("context", entry.context)
        self.assertIn("context\x04message", po_file.entries)
        self.assertIs(entry, po_file.entries["context\x04message"])

    def test_translation(self):
        po_file = PoFile()
        entry = po_file.add_entry("message")
        entry.add_translation("translation")
        self.assertEqual({0: "translation"}, entry.translations)
        self.assertEqual({"message": "translation"}, po_file.get_catalog())

    def test_plural_translation(self):
        po_file = PoFile()
        entry = po_file.add_entry("message", "plural")
        entry.add_plural_translation(0, "translation")
        entry.add_plural_translation(1, "plural translation")
        self.assertEqual({0: "translation", 1: "plural translation"}, entry.translations)
        self.assertEqual(
            {
                ("message", 0): "translation",
                ("message", 1): "plural translation"},
            po_file.get_catalog())

    def test_location(self):
        po_file = PoFile()
        entry = po_file.add_entry("message")
        entry.add_location("filename.py", 42)
        entry.add_location("filename.py", 4242)
        self.assertEqual([("filename.py", 42), ("filename.py", 4242)], entry.locations)

    def test_header(self):
        po_file = PoFile()
        po_file.add_header_field("Language", "fr")
        po_file.add_header_field("MIME-Version", "1.0")
        self.assertEqual([("Language", "fr"), ("MIME-Version", "1.0")], po_file.header_fields)

    def test_header_overwrite(self):
        po_file = PoFile()
        po_file.add_header_field("Language", "fr")
        po_file.add_header_field("Language", "en")
        self.assertEqual([("Language", "en")], po_file.header_fields)

    def test_nplurals(self):
        po_file = PoFile()
        po_file.add_header_field("Plural-Forms", "nplurals=2; plural=(n > 1)")
        self.assertEqual(2, po_file.get_nplurals())

    def test_catalog(self):
        po_file = PoFile()
        po_file.add_entry("non translated message")
        po_file.add_entry("translated message").add_translation("translation")
        entry = po_file.add_entry("translated message 2", "plural")
        entry.add_plural_translation(0, "translation 2")
        entry.add_plural_translation(1, "plural translation 2")
        po_file.add_entry("translated message 3", context="context").add_translation("translation 3")
        entry = po_file.add_entry("translated message 4", "plural", "context")
        entry.add_plural_translation(0, "translation 4")
        entry.add_plural_translation(1, "plural translation 4")
        self.assertEqual(
            {
                "translated message": "translation",
                ("translated message 2", 0): "translation 2",
                ("translated message 2", 1): "plural translation 2",
                "context\x04translated message 3": "translation 3",
                ("context\x04translated message 4", 0): "translation 4",
                ("context\x04translated message 4", 1): "plural translation 4"},
            po_file.get_catalog())

    def test_dump(self):
        po_file = PoFile()
        po_file.add_entry("non translated message")
        po_file.add_entry("non translated message with plural", "plural")
        po_file.add_entry("translated message").add_translation("translation")
        entry_2 = po_file.add_entry("translated message 2", "plural")
        entry_2.add_plural_translation(0, "translation 2")
        entry_2.add_plural_translation(1, "plural translation 2")
        po_file.add_entry("translated message 3", context="context").add_translation("translation 3")
        entry_4 = po_file.add_entry("translated message 4", "plural", "context")
        entry_4.add_plural_translation(0, "translation 4")
        entry_4.add_plural_translation(1, "plural translation 4")
        entry_5 = po_file.add_entry("translated message 5")
        entry_5.add_location("filename.py", 42)
        entry_5.add_location("filename.py", 4242)
        self.assertEqual("""#. obsolete entry
msgid "translated message"
msgstr "translation"

#. obsolete entry
msgid "translated message 2"
msgid_plural "plural"
msgstr[0] "translation 2"
msgstr[1] "plural translation 2"

#. obsolete entry
msgctxt "context"
msgid "translated message 3"
msgstr "translation 3"

#. obsolete entry
msgctxt "context"
msgid "translated message 4"
msgid_plural "plural"
msgstr[0] "translation 4"
msgstr[1] "plural translation 4"

msgid "translated message 5"
msgstr ""
""", po_file.dumps(include_locations=False, prune_obsoletes=False))
        self.assertEqual("""msgid "translated message 5"
msgstr ""
""", po_file.dumps(include_locations=False, prune_obsoletes=True))
        self.assertEqual("""#: filename.py:42 filename.py:4242
msgid "translated message 5"
msgstr ""
""", po_file.dumps(include_locations=True, prune_obsoletes=True))

    def test_dump_nplurals(self):
        po_file = PoFile()
        entry = po_file.add_entry("message", "plural")
        entry.add_location("filename.py", 42)
        self.assertEqual("""msgid "message"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
""", po_file.dumps(include_locations=False, prune_obsoletes=False))
        po_file.add_header_field("Plural-Forms", "nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;")
        self.assertEqual("""msgid ""
msgstr ""
"Plural-Forms: nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2;\\n"

msgid "message"
msgid_plural "plural"
msgstr[0] ""
msgstr[1] ""
msgstr[2] ""
""", po_file.dumps(include_locations=False, prune_obsoletes=False))

    def test_dump_embedded_newlines(self):
        po_file = PoFile()
        entry = po_file.add_entry("multiline\nmessage", "multiline\nplural", "multiline\ncontext")
        entry.add_location("filename.py", 42)
        entry.add_plural_translation(0, "translated\nmultiline\nmessage")
        entry.add_plural_translation(1, "translated\nmultiline\nplural")
        self.assertEqual(r"""msgctxt ""
"multiline\n"
"context"
msgid ""
"multiline\n"
"message"
msgid_plural ""
"multiline\n"
"plural"
msgstr[0] ""
"translated\n"
"multiline\n"
"message"
msgstr[1] ""
"translated\n"
"multiline\n"
"plural"
""", po_file.dumps(include_locations=False, prune_obsoletes=False))

    def test_dump_terminal_newline(self):
        po_file = PoFile()
        entry = po_file.add_entry("\nmessage\n", "\nplural\n", "\ncontext\n")
        entry.add_location("filename.py", 42)
        entry.add_plural_translation(0, "\ntranslated message\n")
        entry.add_plural_translation(1, "\ntranslated plural\n")
        self.assertEqual(r"""msgctxt "\ncontext\n"
msgid "\nmessage\n"
msgid_plural "\nplural\n"
msgstr[0] "\ntranslated message\n"
msgstr[1] "\ntranslated plural\n"
""", po_file.dumps(include_locations=False, prune_obsoletes=False))

    def test_dump_embedded_and_terminal_newlines(self):
        po_file = PoFile()
        entry = po_file.add_entry("\nmultiline\nmessage\n", "\nmultiline\nplural\n", "\nmultiline\ncontext\n")
        entry.add_location("filename.py", 42)
        entry.add_plural_translation(0, "\ntranslated\nmultiline\nmessage\n")
        entry.add_plural_translation(1, "\ntranslated\nmultiline\nplural\n")
        self.assertEqual(r"""msgctxt ""
"\n"
"multiline\n"
"context\n"
msgid ""
"\n"
"multiline\n"
"message\n"
msgid_plural ""
"\n"
"multiline\n"
"plural\n"
msgstr[0] ""
"\n"
"translated\n"
"multiline\n"
"message\n"
msgstr[1] ""
"\n"
"translated\n"
"multiline\n"
"plural\n"
""", po_file.dumps(include_locations=False, prune_obsoletes=False))
