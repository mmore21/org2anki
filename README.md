# org2anki

Generates Anki cards from org mode notes.

## Features

* Convert a single org mode file.
* Recursively convert an entire directory of org mode files.
* Supports basic card creation and cloze card creation.
* Copies local images referenced in org mode files to local Anki media directory for displaying (uses Anki's preset Linux path).
* Outputs creation statistics including the number of cards for each type and the number of files parsed.

## Example Usage

* org2anki in directory mode: `python3 o2a.py -d ./sample/org/ ./sample/anki/ -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki cards from directory (-d): ['./org/', './anki/']
✔️ ./sample/org/sample1.org ‣ ./sample/anki/sample1
✔️ ./sample/org/sample2.org ‣ ./sample/anki/sample2
== Successfully generated 10 basic card(s) and 12 cloze card(s) from 2 file(s)
</pre>

* org2anki in file mode: `python3 o2a.py -f ./sample/org/sample1.org ./sample/anki/ -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki cards from file (-f): ['./sample/org/sample1.org', './anki/']
✔️ ./sample/org/sample1.org ‣ ./sample/anki/
== Successfully generated 5 basic card(s) and 9 cloze card(s) from 1 file(s)
</pre>

## License

TBD

