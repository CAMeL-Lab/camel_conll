# Camel-depeval

Compare two CoNLL-X files or directories, to obtain the tokenization F-score and POS tag accuracy, as well as the LAS, UAS, and label scores.<br><br>
Since comparison usually occurs between gold and parsed files, the two files/directories will be differentiated using `gold` and `parsed` keywords. In other words, you do not need to have gold and parsed files to compare; any two will do.<br><br>

The tree alignment part of the code uses <a href="https://github.com/CAMeL-Lab/ced_word_alignment">ced_word_alignment</a>.

Note: the evaluator is also CoNLL-U compatible.

## Methodology
<ol>
<li>Two files or directories are passed to the evaluator. If two directories are passed, the directories must have matching file names.</li>
<li>The files are read, and the trees every two files are compared.</li>
<li>Align trees using ced_word_alignment
<ul><li>involves inserting null alignment tokens</li></ul>
</li>
<li>The evaluation scores are then calulated
<ul><li>tokenization f-score is calculated on all aligned tokens, while the remaining metrics are calulated after removing insertions (null alignment tokens added to the gold tree)</li></ul>
</li>
</ol>




## Assumptions
Since ced_word_alignment is used, the second and third assumptions are the same.
- No words are added to either the parsed or gold files.
- No changes to the word order.
- Text is in the same script and encoding.

---

## Contents

- `align_trees.py` aligns trees using the ced_word_alignment algorithm
- `class_conllx` used to read CoNLL-X files
- `classes` dataclasses used throughout the code
- `conllx_counts` gets different statistics after comparing 2 CoNLL-X files
- `conllx_scores` calculates scores given counts
- `evaluate_conllx_driver` main script
- `handle_args` simplifies use of the argparse library
- `requirements.txt` necessary dependencies needed to run the scripts.
- ced_word_alignment/ the ced alignment library
- `README.md` this document.

## Requirements

- Python 3.8 and above.

To use, you need to first install the necessary dependencies by running the following command:

```bash
pip install -r requirements.txt
```

---

## Usage

```text
usage: evaluate_conllx_driver.py [-h] [-g] [-p] [-gd] [-pd]

This script takes 2 CoNLL-X files or 2 directories of CoNLL-X files and evaluates the scores.

required arguments:
  -g , --gold          the gold CoNLL-X file
  -p , --parsed        the parsed CoNLL-X file

or:
  -gd , --gold_dir     the gold directory containing CoNLL-X files
  -pd , --parsed_dir   the parsed directory containing CoNLL-X files
```

---

## Examples

The sentences used are taken from CamelTB_1001_introduction_1.conllx and CamelTB_1001_night_1_1.conllx (data can be obtained from <a href="http://treebank.camel-lab.com/">The Camel Treebank</a>.

### Sample 1:
The toknization is the same, and so the F_score is 100%, and the insertion/deletion counts are both 0. <br>
```text
python src/main.py -g data/samples_gold/sample_1.conllx -p data/samples_parsed/sample_1.conllx
```
|||
|- |- |
| tokenization_f_score |      100.0 |
| tokenization_precision |    100.0 |
| tokenization_recall |       100.0 |
| word_accuracy |             100.0 |
| pos |                      81.579 |
| uas |                      55.263 |
| label |                    65.789 |
| las |                      44.737 |
| pp_uas_score |                  0 |
| pp_label_score |                0 |
| pp_las_score |                  0 |


### Sample 2:

```text
python src/main.py -g data/samples_gold/sample_2.conllx -p data/samples_parsed/sample_2.conllx
```
|||
|- |- |
| tokenization_f_score |      90.385 |
| tokenization_precision |    90.385 |
| tokenization_recall |       90.385 |
| word_accuracy |             97.222 |
| pos |                       86.538 |
| uas |                       65.385 |
| label |                       75.0 |
| las |                       57.692 |
| pp_uas_score |                 0.0 |
| pp_label_score |               0.0 |
| pp_las_score |                 0.0 |

### Sample normalization:

Using the arguments x (punctuation), n (number), and a (alef, yeh, and ta marbuta), the evaluation will ignore differences in tokenization. When using the arguments, the following comparisons will be equal:

1 and ١
, and ،
ي and ى

#### Without normalization
```text
python src/main.py -g data/samples_gold/sample_4_norm.conllx -p data/samples_parsed/sample_4_norm.conllx 
```
|||
|- |- |
| tokenization_f_score |      80.0 |
| tokenization_precision |    80.0 |
| tokenization_recall |       80.0 |
| word_accuracy |             75.0 |
| pos |                       80.0 |
| uas |                       80.0 |
| label |                     80.0 |
| las |                       80.0 |
| pp_uas_score |              50.0 |
| pp_label_score |            50.0 |
| pp_las_score |              50.0 |

#### With normalization of punctuation and numbers (you can also add a to make the arugment -xna)
```text
python src/main.py -g data/samples_gold/sample_4_norm.conllx -p data/samples_parsed/sample_4_norm.conllx -xn
```
|||
|- |- |
| tokenization_f_score |      100.0 |
| tokenization_precision |    100.0 |
| tokenization_recall |       100.0 |
| word_accuracy |             100.0 |
| pos |                       100.0 |
| uas |                       100.0 |
| label |                     100.0 |
| las |                       100.0 |
| pp_uas_score |              100.0 |
| pp_label_score |            100.0 |
| pp_las_score |              100.0 |


### Run evaluation on a folder
```text
python src/main.py --gold_dir=data/samples_gold --parsed_dir=data/samples_parsed
```
|||||||||||
|- |- |- |- |- |- |- |- |- |- |
|tokenization_f_score| tokenization_precision| tokenization_recall| word_accuracy| pos| uas| label| las| pp_uas_score| pp_label_score| pp_las_score|
|sample\_4\_norm|80\.0|80\.0|80\.0|75\.0|80\.0|80\.0|80\.0|80\.0|50\.0|50\.0|50\.0||
|sample\_2|90\.385|90\.385|90\.385|97\.222|86\.538|65\.385|75\.0|57\.692|0\.0|0\.0|0\.0||
|sample\_1|100\.0|100\.0|100\.0|100\.0|81\.579|55\.263|65\.789|44\.737|0\.0|0\.0|0\.0||
|sample\_3|80\.0|80\.0|80\.0|75\.0|100\.0|100\.0|100\.0|100\.0|100\.0|100\.0|100\.0||

---


## License

conllx_evaluator is available under the MIT license.
See the [LICENSE file](/LICENSE) for more info.