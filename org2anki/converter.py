import argparse
from pathlib import Path

import orgparse


class Converter:
    def __init__(self, org_path, anki_path, recursive, verbose):
        self.org_path = Path(org_path)
        self.anki_path = Path(anki_path)
        self.recursive = recursive
        self.verbose = verbose
        self.card_count = 0
        self.cloze_count = 0
        self.file_count = 0

    def run(self):
        """
        Executes the CLI program based on the arguments used during object creation.
        """
        self.banner()

        if self.recursive:
            print(
                f"== Generating Anki card(s) from dir (recursive=True): {self.org_path}"
            )
            self.convert_dir(dir_path=self.org_path.resolve())
        else:
            print(
                f"== Generating Anki card(s) from file (recursive=False): {self.org_path.name}"
            )
            self.convert_file(org_path=self.org_path.resolve(), anki_path=self._get_anki_export_path(self.org_path.resolve()))

        print(
            f"== Successfully generated {self.card_count} basic card(s) and {self.cloze_count} cloze card(s) from {self.file_count} file(s)"
        )

    def convert_dir(self, dir_path):
        """
        Recursively iterates through a directory and converts each org mode file.
        """
        for file in dir_path.iterdir():
            if file.is_dir():
                self.convert_dir(file)
            else:
                if self._is_org_mode_file(file):
                    self.convert_file(
                        org_path=file.resolve(),
                        anki_path=self._get_anki_export_path(file),
                    )

    def convert_file(self, org_path, anki_path):
        """
        Parses an org mode file and generates Anki import files if applicable.
        """
        parser = orgparse.OrgParser(file_path=org_path)
        parser.parse_file()

        if parser.flashcards or parser.clozes:
            anki_path.mkdir(parents=True, exist_ok=True)

            if parser.flashcards:
                self.export_cards(parser.flashcards, anki_path)
                self.card_count += len(parser.flashcards)
            if parser.clozes:
                self.export_clozes(parser.clozes, anki_path)
                self.cloze_count += len(parser.clozes)

            self.file_count += 1

            if self.verbose:
                print("✔️", org_path, "‣", anki_path)

    def export_cards(self, cards, anki_path):
        """
        Exports Anki flashcards using Anki's import format.
        """
        anki_path_card = anki_path / "card.txt"
        with anki_path_card.open(mode="w") as f:
            for card in cards:
                f.write(card.front + '; "' + "<br>".join(card.back) + '";\n')

    def export_clozes(self, clozes, anki_path):
        """
        Exports Anki cloze cards using Anki's import format.
        """
        anki_path_cloze = anki_path / "cloze.txt"
        with anki_path_cloze.open(mode="w") as f:
            for cloze in clozes:
                f.write(cloze.text + ";\n")

    def _get_anki_export_path(self, file):
        """
        Forms the absolute path to export the generated Anki import file(s) to.
        """
        file_path_no_suffix = str(file.with_suffix(""))
        if self.org_path.is_dir():
            abs_org_path = str(self.org_path.resolve())
        else:
            abs_org_path = str(self.org_path.resolve().parent)
        abs_anki_path = str(self.anki_path.resolve())
        return Path(file_path_no_suffix.replace(abs_org_path, abs_anki_path))

    def _is_org_mode_file(self, file):
        """
        Checks if a pathlib file exists and is an org mode file.
        """
        return (
            file.is_file() and file.suffix == ".org" and file.stem != self.org_path.name
        )

    def banner(self):
        """
        Displays CLI banner.
        """
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
