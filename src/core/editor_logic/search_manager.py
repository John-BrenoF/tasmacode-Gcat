from src.core.editor_logic.buffer import DocumentBuffer
from typing import List, Tuple
from collections import defaultdict

class SearchManager:
    """Manages search and replace operations within a DocumentBuffer."""

    def __init__(self):
        self.highlights = []
        self.root_path = None

    def set_root_path(self, path: str):
        self.root_path = path

    def find_all(self, buffer: DocumentBuffer, text: str, case_sensitive: bool = False) -> List[Tuple[int, int, int]]:
        """
        Finds all occurrences of a text string in the buffer.
        Returns a list of tuples: (line_index, start_col, length).
        """
        if not text:
            self.highlights = []
            return []

        results = []
        search_text = text if case_sensitive else text.lower()
        
        for i, line in enumerate(buffer.lines):
            line_to_search = line if case_sensitive else line.lower()
            start = 0
            while True:
                start = line_to_search.find(search_text, start)
                if start == -1:
                    break
                results.append((i, start, len(text)))
                start += 1 # Move to next character to find overlapping matches
        
        self.highlights = results
        return results

    def clear_highlights(self):
        self.highlights = []

    def replace_all(self, buffer: DocumentBuffer, find_text: str, replace_text: str, case_sensitive: bool = False):
        """
        Performs a replace-all operation and makes it undoable as a single block.
        """
        if not find_text:
            return

        occurrences = self.find_all(buffer, find_text, case_sensitive)
        if not occurrences:
            return

        text_before = buffer.get_text()
        cursors_before = [c.copy() for c in buffer.cursors]
        
        new_lines = list(buffer.lines)
        line_changes = defaultdict(list)
        for line_idx, col, length in occurrences:
            line_changes[line_idx].append((col, length))

        for line_idx in sorted(line_changes.keys(), reverse=True):
            line = new_lines[line_idx]
            for col, length in sorted(line_changes[line_idx], reverse=True, key=lambda x: x[0]):
                line = line[:col] + replace_text + line[col+length:]
            new_lines[line_idx] = line
        
        buffer.replace_full_text(text_before, "\n".join(new_lines), cursors_before)
        self.clear_highlights()