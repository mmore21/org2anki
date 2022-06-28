import hashlib
import os
import pathlib
import re
import sys
import shutil
import orgparse

class Parser():
    """
    Parser for org mode files.
    """
    
    INCLUDE_TAG = "sr"
    IGNORE_TAG = "nosr"
    INCLUDE_MODE = "all"
    IGNORE_MODE = "none"
    REGEX_CLOZE_EQUAL = "(={1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?={1})|(={1}\S+?={1})"
    REGEX_CLOZE_TILDE = "(~{1}[^=+\-\*\/\s]+?.*?[^=+\-\*\/\s]+?~{1})|(~{1}\S+?~{1})"
    REGEX_IMAGE = "\S+\.(png|jpg|jpeg|svg|bmp)"
    REGEX_LATEX_INLINE = "\\\([\s\S]+?\\\)"
    REGEX_LATEX_BLOCK = "\\\[[\s\S]+?\\\]"
    ANKI_MEDIA_PATH = "/home/maz/.local/share/Anki2/Main/collection.media/"

    def __init__(self, org_file="final.org", anki_dir="tmp"):
        """
        Initializes the parser by opening an org file, getting its max depth,
        and setting the parser to its default mode (include all).
        """
        self.tree = orgparse.load(org_file)
        self.max_depth = self.get_max_depth()
        self.mode = Parser.INCLUDE_MODE
        self.basic_cards = {}
        self.cloze_cards = []
    
    def get_max_depth(self):
        """
        Get the max nest depth among all bullet point headings in an org mode file.

        Ex:
            * Heading 1
            ** Heading 2
            *** Heading 3
            * Heading 4
            ** Heading 5

            Return the depth of Heading 3, which is 3.
        """
        return max([node.level for node in self.tree])
    
    def parse_header(self):
        """
        Parses the header of an org mode file. Looks for the #+org2anki heading
        that specifies whether to set the mode to include or ignore.
        """
        header = self.tree[0].body
        lines = header.lower().split("\n")
        for line in lines:
            if line.startswith("#+org2anki:"):
                mode = line.split(" ")[1].strip()
                if mode == Parser.INCLUDE_MODE or mode == Parser.IGNORE_MODE:
                    self.mode = mode
                else:
                    print("Invalid org2anki Mode")
                break

    def parse_image(self, line):
        """
        Extracts an image path from an org mode file and copies that image to the Anki
        media directory.
        """
        match = re.search(Parser.REGEX_IMAGE, line)
        if match:
            img_path = os.path.abspath(match.group())
            img_name = os.path.basename(img_path)

            # anki_img_name = img_path.replace("/", "+")
            anki_img_name = img_path.encode("utf-8").hex()
            print(anki_img_name)

            anki_img_path = os.path.join(Parser.ANKI_MEDIA_PATH, anki_img_name)
            print(anki_img_path)

            if os.path.exists(img_path):
                # print(img_path, img_name)
                # print(anki_img_path, anki_img_name)
                shutil.copy(img_path, anki_img_path)
                line = "<img src=\"" + anki_img_name + "\" />"
        return line
            
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
                parts.append(line[start+1:end-1])
                cloze_indices.append(idx)
                idx += 1
                prev = end
        parts.append(line[prev:])
        clean = "".join(parts)
        
        tilde_count = 1
        for idx in cloze_indices:
            # Creates cloze that all reveal on same card.
            if cloze_mode == Parser.REGEX_CLOZE_EQUAL:
                parts[idx] = "{{c1::" + parts[idx] + "}}"
            # Creates cloze that reveal on separate cards.
            elif cloze_mode == Parser.REGEX_CLOZE_TILDE:
                parts[idx] = "{{c" + str(tilde_count) + "::" + parts[idx] + "}}"
                tilde_count += 1
        
        cloze = "".join(parts)

        if is_cloze:
            self.cloze_cards.append(cloze)
            return clean
        else:
            return ""

    def gen_card(self, node):
        """
        Generates a basic card (and cloze card(s) if any exist) from a given org mode node.
        """
        # print(node.heading)
        lines = node.body.split("\n")
        answer = []

        for line in lines:
            line = line.lstrip("-+ ")
            res_equal = self.gen_cloze(line, Parser.REGEX_CLOZE_EQUAL)
            res_tilde = self.gen_cloze(line, Parser.REGEX_CLOZE_TILDE)
            if res_equal:
                answer.append(res_equal)
            elif res_tilde:
                answer.append(res_tilde)
            else:
                answer.append(line)
            # Search every line for an image
            answer[-1] = self.parse_image(answer[-1])
        # print("\n".join(answer))
        # print(answer)
        bullet_answer = ["<li>" + a + "</li>" for a in answer]
        #print(bullet_answer)
        self.basic_cards[node.heading] = "\n".join(bullet_answer)
        
    def gen_cards(self):
        """
        Generate Anki cards for every org mode leaf node in the file. Leaf nodes are
        nodes that are equal to the max depth.

        Returns a tuple of two lists: the generated basic cards and the generated cloze cards.
        """
        leaf_nodes = [node for node in self.tree[1:] if node.level == self.max_depth]
        for node in leaf_nodes:
            # Include all cards by default, except ones tagged to ignore
            if self.mode == Parser.INCLUDE_MODE:
                if Parser.IGNORE_TAG not in node.tags:
                    self.gen_card(node)
            # Ignore all cards by default, except ones tagged to include
            elif self.mode == Parser.IGNORE_MODE:
                if Parser.INCLUDE_TAG in node.tags:
                    self.gen_card(node)
        
        return (self.basic_cards, self.cloze_cards)
    
class O2A():
    """
    Converts org mode directories or files to Anki importable files.
    """

    def __init__(self, verbose=False):
        self.file_count = 0
        self.card_count = 0
        self.cloze_count = 0
        self.verbose = verbose
    
    def gen_file(self, org_path, anki_path):
        p = Parser(org_file=org_path, anki_dir=anki_path)
        p.parse_header()

        basic_cards, cloze_cards = p.gen_cards()
        self.card_count += len(basic_cards)
        self.cloze_count += len(cloze_cards)

        anki_path_card = os.path.join(anki_path, "card.txt")
        os.makedirs(os.path.dirname(anki_path_card), exist_ok=True)
        with open(anki_path_card, "w") as f:
            for question, answer in basic_cards.items():
                f.write(question + "; \"" + answer + "\";\n")

        anki_path_cloze = os.path.join(anki_path, "cloze.txt")
        os.makedirs(os.path.dirname(anki_path_cloze), exist_ok=True)
        with open(anki_path_cloze, "w") as f:
            for cloze in cloze_cards:
                f.write(cloze + ";\n")

        if self.verbose:
            print("✔️", org_path, "‣", anki_path)
        self.file_count += 1
        
    def gen_dir(self, org_dir, anki_dir):
        rdname = os.path.basename(os.path.dirname(org_dir))
        for subdir, dirs, files in os.walk(org_dir):
            for file in files:
                fname = os.path.splitext(file)[0]
                dname = os.path.basename(subdir)
                if file.endswith(".org") and fname != dname and fname != rdname:
                    org_path = os.path.join(subdir, file)
                    anki_path = org_path.replace(org_dir, anki_dir).replace(".org", "")
                    self.gen_file(org_path, anki_path)

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
        print(f"{sys.argv[0]} -d <org_root_dir> <anki_root_dir>\n")
        print("== Generate Anki cards from file (-f)")
        print(f"{sys.argv[0]} -f <org_file> <anki_dir>\n")
        print("== Enable verbose logging output (-v)")
        print(f"{sys.argv[0]} -v ...\n")
        print("== View help message (-h)")
        print(f"{sys.argv[0]} -h")

if __name__=="__main__":
    o2a = O2A()
    o2a.run()
