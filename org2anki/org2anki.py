import re
from pathlib import Path

import yaml


class Parser:
    CARD_REGEX = r".+::"
    CLOZE_REGEX = r"\/{1}((\\(\[|\().+?\\(\]|\)))|\S.*?\S)\/{1}"

    def __init__(self, file_path):
        self.file_path = file_path
        self.cards = []
        self.clozes = []

    def parse(self, file_path):
        with open(file_path.resolve()) as f:
            lines = f.readlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            next_line = lines[i + 1]
            if line.rstrip().endswith("::"):
                indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
            match = re.finditer(Parser.CLOZE_REGEX, line)
            if match:
                for m in match:
                    print(m.group())
            match = re.finditer(Parser.CARD_REGEX, line)
            if match:
                for m in match:
                    print(m.group())

    def write(self):
        with open("card.txt", "w") as f:
            for question, answer in self.cards.items():
                f.write(question + '; "' + answer + '";\n')
        with open("cloze.txt", "w") as f:
            for cloze in self.clozes:
                f.write(cloze + ";\n")


class Org2Anki:
    def __init__(self):
        self.config = self.load_config()
        target_path = Path(self.config["org_path"])
        self.traverse(target_path)

    def load_config(self):
        with open("config.yml", "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        return config

    def traverse(self, target_path):
        for file in target_path.iterdir():
            if file.is_dir():
                self.traverse(file)
            else:
                if (
                    file.is_file()
                    and file.suffix == ".org"
                    and file.stem != target_path.name
                    and file.stem == "aero_500"
                ):
                    parser = Parser(file.resolve())
                    parser.parse(file)


if __name__ == "__main__":
    o2a = Org2Anki()
