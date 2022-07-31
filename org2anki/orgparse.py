import copy
import re
import shutil
import string
from pathlib import Path


class Flashcard:
    INDENT = 2
    REGEX_IMAGE = r"\[\[file:\S+\.(png|jpg|jpeg|svg|bmp)\]\]"
    SEPARATOR = " ::"

    def __init__(self, front, back):
        self.front = front
        self.back = back


class Cloze:
    REGEX_CLOZE_EQUAL = r"(={1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?={1})|(={1}\S+?={1})"
    REGEX_CLOZE_TILDE = r"(~{1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?~{1})|(~{1}\S+?~{1})"

    def __init__(self, line, mode):
        self.line = line.lstrip("+- ")
        self.mode = mode
        self.parts = []
        self.indices = []

        self.parse()

    @property
    def clean(self):
        """
        Line containing cloze without the cloze syntax.
        """
        return "".join(self.parts)

    @property
    def text(self):
        """
        Line containing cloze with the cloze syntax.
        """
        parts = copy.deepcopy(self.parts)
        cloze_count = 1
        for idx in self.indices:
            # Creates cloze that all reveal on same card
            if self.mode == Cloze.REGEX_CLOZE_EQUAL:
                parts[idx] = "{{c1::" + parts[idx] + "}}"
            # Creates cloze that reveal on separate cards
            elif self.mode == Cloze.REGEX_CLOZE_TILDE:
                parts[idx] = "{{c" + str(cloze_count) + "::" + parts[idx] + "}}"
                cloze_count += 1

        # Remove flashcard question from the cloze text
        text = "".join(parts)
        if Flashcard.SEPARATOR in text:
            text = text.split(Flashcard.SEPARATOR)[-1]

        return text.strip()

    def parse(self):
        """
        Splits the org mode line at each cloze deletion and stores the list indicies of all cloze deletions.
        """
        idx = 0
        prev = 0

        match = re.finditer(self.mode, self.line)
        if match:
            for m in match:
                start = m.span()[0]
                end = m.span()[1]
                self.parts.append(self.line[prev:start])
                idx += 1
                self.parts.append(self.line[start + 1 : end - 1])
                self.indices.append(idx)
                idx += 1
                prev = end

        self.parts.append(self.line[prev:])


class OrgParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.flashcards = []
        self.clozes = []

    def parse_file(self):
        """
        Parse an org mode file and extract flashcards and cloze cards.
        """
        with open(self.file_path, "r") as f:
            lines = f.read().splitlines()

        i = 0
        while i < len(lines):
            lines[i] = self._extract_cloze(lines[i])

            if Flashcard.SEPARATOR in lines[i]:
                flashcard = lines[i].split(Flashcard.SEPARATOR)
                front = flashcard[0].lstrip(string.punctuation + string.whitespace)
                back = flashcard[1].strip()
                is_multiline_flashcard = not back
                if is_multiline_flashcard:
                    back_lines = self._extract_multiline_flashcard(lines, i)
                    i += len(back_lines)
                else:
                    back_lines = [back]
                card = Flashcard(front=front, back=back_lines)
                self.flashcards.append(card)
            i += 1

    def _extract_multiline_flashcard(self, lines, i):
        """
        Iterate over the lines of a file until the indentation level reduces (signals end of flashcard). Parse each line for cloze cards and images.
        """
        back = []
        indent_level = self._indentation(lines[i]) + Flashcard.INDENT
        while i < len(lines) - 1 and self._indentation(lines[i + 1]) == indent_level:
            lines[i + 1] = self._extract_cloze(lines[i + 1])
            lines[i + 1] = self._extract_image(lines[i + 1])

            back.append(lines[i + 1].strip())
            i += 1

        return back

    def _extract_cloze(self, line):
        """
        Extracts a cloze card from a line if matching regex exists.
        """
        if re.search(Cloze.REGEX_CLOZE_EQUAL, line):
            cloze = Cloze(line, Cloze.REGEX_CLOZE_EQUAL)
            self.clozes.append(cloze)
            line = cloze.clean
        elif re.search(Cloze.REGEX_CLOZE_TILDE, line):
            cloze = Cloze(line, Cloze.REGEX_CLOZE_TILDE)
            self.clozes.append(cloze)
            line = cloze.clean
        return line

    def _extract_image(self, line):
        """
        Extracts a relative image path from an org mode file and copies that image to the Anki
        media directory.
        """
        match = re.search(Flashcard.REGEX_IMAGE, line)
        if match:
            rel_org_img_path = match.group().strip("[]").replace("file:", "")
            line = self._copy_image_to_anki_media_dir(rel_org_img_path)

        return line

    def _copy_image_to_anki_media_dir(self, rel_org_img_path):
        """
        Copies an image from the original source path to the Anki media directory if it exists. Returns a line containing the HTML img tag with the source set to the copied image within the Anki media folder.
        """
        abs_org_img_path = Path(self.file_path).parent / rel_org_img_path
        anki_img_name = rel_org_img_path.encode().hex() + ".o2a"
        abs_anki_img_path = (
            Path.home() / ".local/share/Anki2/Main/collection.media/" / anki_img_name
        )

        if abs_org_img_path.exists():
            shutil.copy(abs_org_img_path, abs_anki_img_path)
            line = f'<img src=""{anki_img_name}"" />'

        return line

    def _indentation(self, line, tabsize=Flashcard.INDENT):
        """
        Checks the indentation (number of preceding spaces) of a line.
        """
        line_expanded = line.expandtabs(tabsize)

        if line_expanded.isspace():
            indentation = 0
        else:
            indentation = len(line_expanded) - len(line_expanded.lstrip())

        return indentation
