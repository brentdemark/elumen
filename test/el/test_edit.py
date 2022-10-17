import os
import textwrap
from unittest import TestCase
from parameterized import parameterized

from el.edit import FileBuffer, TextEditor

RESOURCE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../resources/')


class TestEdit(TestCase):
    def test_load_file_to_buffer(self):
        editor = TextEditor()
        editor.load_file_to_buffer(os.path.join(RESOURCE_DIR, "file_to_edit.txt"))
        assert editor.buffer.content == textwrap.dedent("""\
        asdf
        asdf
        asdf""")

    @parameterized.expand([
        (0, 3, 0, 8, "a-012345\nb-012345\nc-0123"),
        (2, 4, 3, 8, "123\n12345"),
        (0, 20, 0, 20, "a-0123456789\nb-0123456789\nc-0123\nd-0123456789\n")
    ])
    def test_get_text_view(self, start_line, end_line, start_column, end_column, expected):
        buffer = FileBuffer()
        buffer.content = textwrap.dedent("""\
        a-0123456789
        b-0123456789
        c-0123
        d-0123456789
        """)
        assert buffer.get_text_view(start_line, end_line, start_column, end_column) == expected

    @parameterized.expand([
        (0, 0, "-0123456789\nb-0123456789\n\nd-0123456789\n"),
        (0, 12, "a-0123456789b-0123456789\n\nd-0123456789\n"),
        (3, 12, "a-0123456789\nb-0123456789\n\nd-0123456789"),
        (6, 300, "a-0123456789\nb-0123456789\n\nd-0123456789\n"),
        (4, 4, "a-0123456789\nb-0123456789\n\nd-0123456789\n"),
        (0, -1, "a-0123456789b-0123456789\n\nd-0123456789\n"),
        (0, -3, "a-012345679\nb-0123456789\n\nd-0123456789\n"),
    ])
    def test_delete_char_at(self, line, column, expected):
        buffer = FileBuffer()
        buffer.content = textwrap.dedent("""\
        a-0123456789
        b-0123456789
        
        d-0123456789
        """)
        buffer.delete_char_at(line, column)
        assert buffer.content == expected

    @parameterized.expand([
        ("A", 0, 0, "Aa-0123456789\nb-0123456789\n\nd-0123456789\n"),
        (" ", 1, 5, "a-0123456789\nb-012 3456789\n\nd-0123456789\n"),
        ("\n", 1, 5, "a-0123456789\nb-012\n3456789\n\nd-0123456789\n"),
    ])
    def test_insert_char_at(self, char, line, column, expected):
        buffer = FileBuffer()
        buffer.content = textwrap.dedent("""\
        a-0123456789
        b-0123456789
        
        d-0123456789
        """)
        buffer.insert_char_at(char, line, column)
        assert buffer.content == expected
