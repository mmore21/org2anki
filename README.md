# org2anki

Generates Anki cards from Emacs org mode notes.

## Features

* Convert a single org mode file to an Anki import file.
* Recursively convert an entire directory of org mode files.
* Supports flashcard creation and cloze deletion card creation.
* Copies local images referenced in org mode files to local Anki media directory (uses Anki's preset Linux path).
* Outputs creation statistics including the number of cards generated for each type and the number of files parsed.

## Example Usage

* org2anki in directory mode: `python3 org2anki/converter.py ./sample/org ./sample/anki -r -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki card(s) from dir (recursive=True): sample/org
✔️ ./sample/org/sample1.org ‣ ./sample/anki/sample1
✔️ ./sample/org/sample2.org ‣ ./sample/anki/sample2
== Successfully generated 10 basic card(s) and 12 cloze card(s) from 2 file(s)
</pre>

* org2anki in file mode: `python3 org2anki/converter.py ./sample/org/sample1.org ./sample/anki -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki card(s) from file (recursive=False): sample1.org
✔️ ./sample/org/sample1.org ‣ ./sample/anki/
== Successfully generated 5 basic card(s) and 9 cloze card(s) from 1 file(s)
</pre>

## License

TBD
