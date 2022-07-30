import argparse
import re
import string
from pathlib import Path

CLOZE_EQUAL_REGEX = r"={1}[^\s=]+={1}"
REGEX_CLOZE_EQUAL = r"(={1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?={1})|(={1}\S+?={1})"
REGEX_CLOZE_TILDE = r"(~{1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?~{1})|(~{1}\S+?~{1})"
INDENTATION_AMOUNT = 2


class Cloze:
    def __init__(self, text, extra=""):
        self.text = text
        self.extra = extra


class Card:
    def __init__(self, front, back):
        self.front = front
        self.back = back


class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.cards = []
        self.clozes = []

    def gen_cloze(self, line, cloze_mode):
        """
        Generates a cloze card from a line in the org mode file.
        """
        is_cloze = re.search(cloze_mode, line)
        match = re.finditer(cloze_mode, line)

        cloze_indices = []
        parts = []
        idx = 0
        prev = 0
        # Removes the cloze mode symbols to later use the line for the basic card type.
        if match:
            for m in match:
                start = m.span()[0]
                end = m.span()[1]
                parts.append(line[prev:start])
                idx += 1
                parts.append(line[start + 1 : end - 1])
                cloze_indices.append(idx)
                idx += 1
                prev = end
        parts.append(line[prev:])
        clean = "".join(parts)

        tilde_count = 1
        for idx in cloze_indices:
            # Creates cloze that all reveal on same card.
            if cloze_mode == REGEX_CLOZE_EQUAL:
                parts[idx] = "{{c1::" + parts[idx] + "}}"
            # Creates cloze that reveal on separate cards.
            elif cloze_mode == REGEX_CLOZE_TILDE:
                parts[idx] = "{{c" + str(tilde_count) + "::" + parts[idx] + "}}"
                tilde_count += 1

        cloze = Cloze(text="".join(parts), extra="")

        if is_cloze:
            self.clozes.append(cloze)
            return clean
        else:
            return ""

    def parse_file(self):
        with open(self.file_path, "r") as f:
            lines = f.read().splitlines()

        i = 0
        while i < len(lines):
            res_equal = self.gen_cloze(lines[i], REGEX_CLOZE_EQUAL)
            res_tilde = self.gen_cloze(lines[i], REGEX_CLOZE_TILDE)
            if res_equal:
                lines[i] = res_equal
            elif res_tilde:
                lines[i] = res_tilde
            if "::" in lines[i]:
                components = lines[i].split("::")
                front = components[0].lstrip(string.punctuation + string.whitespace)
                back = []
                if not components[1]:
                    indentation_level = self.indentation(lines[i]) + INDENTATION_AMOUNT
                    while (
                        i < len(lines) - 1
                        and self.indentation(lines[i + 1]) == indentation_level
                    ):
                        res_equal = self.gen_cloze(lines[i + 1], REGEX_CLOZE_EQUAL)
                        res_tilde = self.gen_cloze(lines[i + 1], REGEX_CLOZE_TILDE)
                        if res_equal:
                            lines[i + 1] = res_equal
                        elif res_tilde:
                            lines[i + 1] = res_tilde
                        back.append(lines[i + 1].strip())
                        i += 1
                else:
                    back.append(components[1].strip())
                card = Card(front=front, back=back)
                self.cards.append(card)

            i += 1

    def indentation(self, line, tabsize=2):
        line_expanded = line.expandtabs(tabsize)
        return (
            0
            if line_expanded.isspace()
            else len(line_expanded) - len(line_expanded.lstrip())
        )


class Converter:
    def __init__(self, org_path, anki_path, recursive, verbose):
        self.org_path = Path(org_path)
        self.anki_path = Path(anki_path)
        self.recursive = recursive
        self.verbose = verbose
        self.card_count = 0
        self.cloze_count = 0
        self.file_count = 0

    def convert_file(self, org_path, anki_path):
        parser = Parser(file_path=org_path)
        parser.parse_file()
        self.export_cards(parser.cards, anki_path)
        self.export_clozes(parser.clozes, anki_path)
        self.card_count += len(parser.cards)
        self.cloze_count += len(parser.clozes)
        self.file_count += 1
        if self.verbose:
            print("✔️", org_path, "‣", anki_path)

    def convert_dir(self, dir_path):
        for file in dir_path.iterdir():
            if file.is_dir():
                self.convert_dir(file)
            else:
                if (
                    file.is_file()
                    and file.suffix == ".org"
                    and file.stem != self.org_path.name
                    and file.stem == "aero_500"
                ):
                    anki_path = Path(
                        str(file.with_suffix("")).replace(
                            str(self.org_path.resolve()), str(self.anki_path.resolve())
                        )
                    )
                    self.convert_file(org_path=file.resolve(), anki_path=anki_path)

    def export_cards(self, cards, anki_path):
        anki_path_card = anki_path / "card.txt"
        anki_path.mkdir(parents=True, exist_ok=True)
        with anki_path_card.open(mode="w") as f:
            for card in cards:
                f.write(card.front + '; "' + "<br>".join(card.back) + '";\n')

    def export_clozes(self, clozes, anki_path):
        anki_path_cloze = anki_path / "cloze.txt"
        anki_path.mkdir(parents=True, exist_ok=True)
        with anki_path_cloze.open(mode="w") as f:
            for cloze in clozes:
                f.write(cloze.text + ";\n")

    def run(self):
        self.banner()

        if self.recursive:
            print(
                "== Generating Anki cards from directory (recursive=True):",
                self.org_path,
            )
            self.convert_dir(dir_path=self.org_path.resolve())
        else:
            print(
                "== Generating Anki cards from file (recursive=False):",
                self.org_path.name,
            )
            self.convert_file(file_path=self.org_path.resolve())

        print(
            f"== Successfully generated {self.card_count} basic card(s) and {self.cloze_count} cloze card(s) from {self.file_count} file(s)"
        )

    def banner(self):
        print(
            r"""
                 ____             _    _
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/
           """
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Emacs org mode to Anki flashcard converter"
    )
    parser.add_argument("org_path", type=str, help="path to parse org mode file(s)")
    parser.add_argument(
        "anki_path", type=str, help="path to generate Anki import file(s)"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="enable recursive conversion of directory instead of file",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="enable verbose logging"
    )
    args = vars(parser.parse_args())

    c = Converter(
        org_path=args["org_path"],
        anki_path=args["anki_path"],
        recursive=args["recursive"],
        verbose=args["verbose"],
    )
    c.run()
