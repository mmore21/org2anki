import re
import os
import sys

class Parser():
    def __init__(self):
        self.verbose = False
        self.card_count = 0
        self.cloze_count = 0
        self.file_count = 0
    
    def run(self):
        # Display banner
        self.banner()

        # Get CLI options and arguments
        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]
        args = [arg for arg in sys.argv[1:] if not arg.startswith("-")]\

        if "-v" in opts:
            self.verbose = True
        if "-h" in opts:
            self.help()
        elif "-d" in opts:
            print("== Generating Anki cards from directory (-d):", args)
            self.gen_dir(args[0], args[1])
            print(f"== Successfully generated {self.card_count} basic card(s) and {self.cloze_count} cloze card(s) from {self.file_count} file(s)")
        elif "-f" in opts:
            print("== Generating Anki cards from file (-f):", args)
            self.gen_file(args[0], args[1])
            print(f"== Successfully generated {self.card_count} basic card(s) and {self.cloze_count} cloze card(s) from {self.file_count} file(s)")
        else:
            self.help()
    
    def nest_level(self, line):
        """
        Determines the number of asterisk (*) symbols for the deepest nested headers.
        Ex: A line with a header of "***" would yield a response of 3 from this function.
        """
        length = len(max(re.compile("^\**").findall(line)))
        return length
    
    def gen_file(self, org_path, anki_path):
        """
        Generates an Anki import file from an org mode file.
        """
        cards = {}
        clozes = []
        question = ""
        answer = ""

        # Read the org mode file
        with open(org_path, "r") as f:
            lines = f.readlines()
        
        # Determine the deepest nested header level
        max_nest = max([self.nest_level(line) for line in lines])

        # Iterate over lines of file
        for i in range(len(lines)):
            # Check if line is a question
            # Questions start with an asterisk and are at the deepest nested header level
            if lines[i].startswith("*") and self.nest_level(lines[i]) == max_nest:
                
                question = lines[i].strip("*\n ")
                i += 1

                # Iterate over the answer lines underneath the question
                while i < len(lines) and not lines[i].startswith("*"):

                    cloze_split = lines[i].split(" ")
                    clean_split = lines[i].split(" ")
                    # This regex looks for any cloze words, which are surrounded by equality signs in org mode
                    # Ex: The word =cloze= is marked by surrounding it with two equality signs with no spaces
                    cloze_regex = "(={1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?={1})|(={1}\S+?={1})"
                    # Find the indices of the line's cloze(s)
                    cloze_indices = [idx for idx, item in enumerate(cloze_split) if re.search(cloze_regex, item)]

                    # Generate a cloze card for the line if any indices were found
                    if cloze_indices:

                        for cloze_index in cloze_indices:
                            w = cloze_split[cloze_index]
                            lidx = cloze_split[cloze_index].find("=")
                            ridx = cloze_split[cloze_index].rfind("=") + 1
                            clean_word = w[:lidx] + w[lidx:ridx].strip("=") + w[ridx:]
                            cloze_word = w[:lidx] + "{{c1::" + w[lidx:ridx].strip("=") + "}}" + w[ridx:]
                            cloze_split[cloze_index] = cloze_word
                            clean_split[cloze_index] = clean_word
                        
                        # Create a cloze card
                        cloze = " ".join(cloze_split).rstrip("\n")
                        clozes.append(cloze)
                        # Create a cleanly parsed version of the line to add to the basic card answer
                        clean = " ".join(clean_split)
                        lines[i] = clean

                    answer += lines[i]
                    i += 1

                cards[question] = answer.rstrip("\n")
                question = ""
                answer = ""

        # Write basic cards to file
        if cards:
            self.card_count += len(cards)
            anki_path_card = os.path.join(anki_path, "card.txt")
            os.makedirs(os.path.dirname(anki_path_card), exist_ok=True)
            with open(anki_path_card, "w") as f:
                for question, answer in cards.items():
                    f.write(question + "; \"" + answer + "\";\n")

        # Write cloze cards to file
        if clozes:
            self.cloze_count += len(clozes)
            anki_path_cloze = os.path.join(anki_path, "cloze.txt")
            os.makedirs(os.path.dirname(anki_path_cloze), exist_ok=True)
            with open(anki_path_cloze, "w") as f:
                for cloze in clozes:
                    f.write(cloze + ";\n")

    def gen_dir(self, org_dir, anki_dir):
        """
        Generates a directory of Anki import files from an org mode directory
        """
        rdname = os.path.basename(os.path.dirname(org_dir))
        for subdir, dirs, files in os.walk(org_dir):
            for file in files:
                fname = os.path.splitext(file)[0]
                dname = os.path.basename(subdir)
                if file.endswith(".org") and fname != dname and fname != rdname:
                    org_path = os.path.join(subdir, file)
                    anki_path = org_path.replace(org_dir, anki_dir).replace(".org", "")
                    if self.verbose:
                        print("✔️", org_path, "‣", anki_path)
                    gen_file(org_path, anki_path)
                    self.file_count += 1

    def banner(self):
        print("""
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        \n""")

    def help(self):
        print("== Generate Anki cards from directory (-d)")
        print(f"{sys.argv[0]} -d <org_dir> <anki_dir>\n")
        print("== Generate Anki cards from file (-f)")
        print(f"{sys.argv[0]} -f <org_file> <anki_file>\n")
        print("== Enable verbose logging output (-v)")
        print(f"{sys.argv[0]} -v ...\n")
        print("== View help message (-h)")
        print(f"{sys.argv[0]} -h")

if __name__=="__main__":
    parser = Parser()
    parser.run()
