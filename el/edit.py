#!/usr/bin/python3
import curses
import curses.textpad
import curses.ascii
import os
import sys
from pathlib import Path

KEY_BACKSPACE = 127
KEY_ESC = 27
KEY_ENTER = 10


class FileBuffer:
    def __init__(self):
        self.content = None

    def get_text_view(self, start_line: int, end_line: int, start_column: int, end_column: int) -> str:
        """
        Get a portion of the buffer to view
        :param start_line: first line of the desired view
        :param end_line: last line of the desired view
        :param start_column: first column of the desired view
        :param end_column: last column of the desired view
        :return: String from the buffer content within the given parameters
        """
        rows = self.content.split(os.linesep)[start_line:end_line]
        trimmed_rows = [row[start_column:end_column] for row in rows]
        return os.linesep.join(trimmed_rows)

    def insert_char_at(self, char: str, line: int, column: int):
        """
        Insert a character into the content at the give line and column
        :param char: Character to insert
        :param line: Line to insert at
        :param column: Column to insert at
        """
        rows = self.content.split(os.linesep)
        rows[line] = rows[line][:column] + char + rows[line][column:]
        self.content = os.linesep.join(rows)

    def delete_char_at(self, line: int, column: int):
        """
        Delete a character at the given line and column
        :param line: Line number to delete at
        :param column: Column number to delete at
        """
        rows = [x + os.linesep for x in self.content.split(os.linesep)]
        if rows[-1] == os.linesep:
            rows = rows[:-1]
        if 0 <= line <= len(rows) - 1:
            if column == -1:
                rows[line] = rows[line][:column]
            else:
                rows[line] = rows[line][:column] + rows[line][column + 1:]
        self.content = ''.join(rows)


class TextEditor:
    def __init__(self):
        self.buffer = FileBuffer()
        self.stdscr = curses.initscr()
        self.term_height, self.term_width = self.stdscr.getmaxyx()
        self.text_line_start = 0
        self.text_column_start = 0

    def load_file_to_buffer(self, file_name: str):
        """
        load the given file into the buffer, if it exists,
        otherwise initialize the buffer to an empty string.
        :param file_name:
        """
        file_path = Path(file_name)
        text = ''
        if file_path.is_file():
            with open(file_path, 'r') as file:
                text = file.read()
        self.buffer.content = str(text)

    def save_buffer_to_file(self, file_name: str):
        """
        Save the buffer to the given file
        :param file_name:
        """
        file_path = Path(file_name)
        with open(file_path, 'w') as file:
            file.writelines(self.buffer.content)

    def edit(self, file_name: str):
        """
        Present the given file for editing within the terminal
        :param file_name: The file to edit
        """
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.load_file_to_buffer(file_name)
        self.show_buffer_content()
        self.stdscr.move(0, 0)
        self.stdscr.refresh()

        x, y = 0, 0
        while True:
            key = self.stdscr.getch()
            x, y, message = self.handle_keyboard_input(x, y, key)
            self.stdscr.clear()
            self.show_buffer_content()
            self.stdscr.addstr(self.term_height - 1, 0, f"{message} Pos: {y} {x}")
            self.stdscr.move(y, x)
            self.stdscr.refresh()
            self.save_buffer_to_file(file_name)

    def show_buffer_content(self):
        """
        Get a portion of the buffer to show and display it in the terminal
        """
        content = self.buffer.get_text_view(self.text_line_start, self.text_line_end(), self.text_column_start,
                                            self.text_column_end())
        self.stdscr.addstr(0, 0, content.encode('utf_8'))

    def text_line_end(self):
        """
        Get the last line of the content to view base on the start and window size
        """
        return self.text_line_start + self.term_height - 1

    def text_column_end(self):
        """
        Get the last column of the content to view base on the start and window size
        """
        return self.text_line_start + self.term_width - 1

    def can_scroll_down(self, y):
        """
        :param y: The current cursor y position
        :return: True if the cursor is at the bottom and there is more text below to show
        """
        return y == self.term_height - 2 and self.text_line_end() < len(self.buffer.content.split(os.linesep))

    def can_scroll_up(self, y):
        """
        :param y: The current cursor y position
        :return: True if the cursor is at the top and there is more text above to show
        """
        return y == 0 and self.text_line_start

    def handle_keyboard_input(self, x, y, key):
        """
        Handle keyboard input
        :param x: Current cursor x position
        :param y: Current cursor y position
        :param key: The key that was pressed ASCII value
        :return: new cursor x, y and message
        """
        message = ''
        if key == curses.KEY_LEFT and x > 0:
            x -= 1
        elif key == curses.KEY_RIGHT and x < self.term_width:
            x += 1
        elif key == curses.KEY_DOWN and y < self.term_height - 2:
            y += 1
        elif key == curses.KEY_DOWN and self.can_scroll_down(y):
            self.text_line_start += 1
        elif key == curses.KEY_UP and y > 0:
            y -= 1
        elif key == curses.KEY_UP and self.can_scroll_up(y):
            self.text_line_start -= 1
        elif key == curses.KEY_DC:  # DELETE
            line = self.text_line_start + y
            column = self.text_column_start + x
            self.buffer.delete_char_at(line, column)
        elif key == KEY_BACKSPACE:
            if x == 0 and y > 0:
                line = self.text_line_start + y - 1
                column = -1
                self.buffer.delete_char_at(line, column)
            elif x > 0:
                line = self.text_line_start + y
                column = x - 1
                self.buffer.delete_char_at(line, column)
        elif curses.ascii.isprint(key) or curses.ascii.isblank(key):
            line = self.text_line_start + y
            column = self.text_column_start + x
            self.buffer.insert_char_at(chr(key), line, column)
            x += 1
        elif key == KEY_ENTER:
            line = self.text_line_start + y
            column = self.text_column_start + x
            self.buffer.insert_char_at('\n', line, column)
            y += 1
            x = 0
        elif key == KEY_ESC:
            exit(0)
        else:
            message = f"Unknown key: {key}"
        return x, y, message


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(f'I can only edit one file at a time')
        exit()
    file_name = sys.argv[1] if len(sys.argv) == 2 else '~temp.txt'
    editor = TextEditor()
    editor.edit(file_name)
