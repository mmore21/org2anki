# org2anki

Generates Anki cards from org mode notes.

## Description

* Convert a single org mode file.
* Recursively convert an entire directory of org mode files.
* Supports basic card creation and cloze card creation.
* Copies local images referenced in org mode files to local Anki media directory for displaying (uses Anki's preset Linux path).
* Outputs creation statistics including the number of cards for each type and the number of files parsed.

## Example Usage

* org2anki in directory mode: `pipenv run python3 o2a.py -d ./org/ ./anki/ -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki cards from directory (-d): ['./org/', './anki/']
✔️ ./org/sample1.org ‣ ./anki/sample1
✔️ ./org/sample2.org ‣ ./anki/sample2
== Successfully generated 10 basic card(s) and 12 cloze card(s) from 2 file(s)
</pre>

* org2anki in file mode: `pipenv run python3 o2a.py -f ./org/sample1.org ./anki/ -v`

<pre>
                 ____             _    _ 
  ___  _ __ __ _|___ \ __ _ _ __ | | _(_)
 / _ \| '__/ _` | __) / _` | '_ \| |/ / |
| (_) | | | (_| |/ __/ (_| | | | |   <| |
 \___/|_|  \__, |_____\__,_|_| |_|_|\_\_|
           |___/                         
        

== Generating Anki cards from file (-f): ['./org/sample1.org', './anki/']
✔️ ./org/sample1.org ‣ ./anki/
== Successfully generated 5 basic card(s) and 9 cloze card(s) from 1 file(s)
</pre>

## Requirements

Python 3.7.3 and pipenv 2020.11.15 were used when building the software. The requirements.txt file lists the additional packages needed.
