# Edit Distance
This repository contains some of my explorations with edit distance. 
  - `levenshten.py` contains my implementation of the Wagner-Fisher algorithm for computing the Levenshtein Edit Distance. Unlike most implementations, it uses dictionaries in its edit table for faster lookup times and the ability to store backpointers. As a result, it can return each edit made as well as the transformation from input to output text.
  - `fuzzy_match.py` demonstrates an application of edit distance for approximate (fuzzy) string matching. My implementation allows for multi-token search strings as well as different types of edit distance.
## Example Usage
### Levenshtein
```commandline
$ ./levenshtein.py -h
usage: levenshtein.py [-h] [-p] [-c] [-s SUB_WEIGHT] [-d DEL_WEIGHT]
                      [-i INS_WEIGHT]
                      input_string search_string

Fuzzy Match: An algorithm to determine the similarity of strings

positional arguments:
  input_string          the string to search for
  search_string         the string (or strings) to search in

optional arguments:
  -h, --help            show this help message and exit
  -p, --pretty_print    print in/out strings with transformations
  -c, --ignore_case     disregard differences in capitalization
  -s SUB_WEIGHT, --sub_weight SUB_WEIGHT
                        weight for substitution operation
  -d DEL_WEIGHT, --del_weight DEL_WEIGHT
                        weight for deletion operation
  -i INS_WEIGHT, --ins_weight INS_WEIGHT
                        weight for insertion operation
```

```commandline
$ ./levenshtein.py "Fork Handles" "four candles" -p
Min Edit Distance: 4
Edit Tally: {'s': 4, 'i': 0, 'd': 0, ' ': 8, 'Total': 12}
Edits:
 'Fork Handles'
 '↕ ↕↕ ↕      '
 'four candles'
```


### Fuzzy Match
```commandline
$ ./fuzzy_match.py -h
usage: fuzzy_match.py [-h] [-m MIN_DISTANCE] [-s SUB_WEIGHT] [-d DEL_WEIGHT]
                      [-i INS_WEIGHT] [-t TRANS_WEIGHT]
                      input_string search_string [search_string ...]

Fuzzy Match: An algorithm to determine the similarity of strings

positional arguments:
  input_string          the string to search for
  search_string         the string (or strings) to search in

optional arguments:
  -h, --help            show this help message and exit
  -m MIN_DISTANCE, --min_distance MIN_DISTANCE
                        the cutoff threshold for edit distance
  -s SUB_WEIGHT, --sub_weight SUB_WEIGHT
                        weight for substitution operation
  -d DEL_WEIGHT, --del_weight DEL_WEIGHT
                        weight for deletion operation
  -i INS_WEIGHT, --ins_weight INS_WEIGHT
                        weight for insertion operation
  -t TRANS_WEIGHT, --trans_weight TRANS_WEIGHT
                        weight for transposition operation
```

Including the `-t` tag allows for transpositions to be counted in the edit distance, effectively implementing the Damerau–Levenshtein Edit distance.
```commandline
$ ./fuzzy_match.py abc acb cab bbb xxx
Match(s1='abc', s2='acb', score=0.33333333333333337)
Match(s1='abc', s2='cab', score=0.33333333333333337)
Match(s1='abc', s2='bbb', score=0.33333333333333337)
```

```commandline
$ ./fuzzy_match.py abc acb cab bbb xxx -t 1
Match(s1='abc', s2='acb', score=0.6666666666666667)
Match(s1='abc', s2='cab', score=0.33333333333333337)
Match(s1='abc', s2='bbb', score=0.33333333333333337)
```

Comparing long inputs from files
```commandline
$ file1=$(cat test_files/christmas_carol.txt)
$ file2=$(cat test_files/winnie_the_pooh.txt)
$ ./levenshtein.py "{$file1}" "{$file2}"
Min Edit Distance: 1004
Edit Tally: {'s': 791, 'i': 144, 'd': 69, ' ': 354, 'Total': 1358}
```
```commandline
$ file1=$(cat test_files/christmas_carol.txt)
$ file2=$(cat test_files/winnie_the_pooh.txt)
$ ./levenshtein.py "{$file1}" "{$file2}" -p -c
Min Edit Distance: 994
Edit Tally: {'s': 781, 'i': 144, 'd': 69, ' ': 364, 'Total': 1358}
Too many edits to display
```

The algorithm allows for multi-token strings in both the search string and the options
```commandline
$ ./fuzzy_match.py "I am Sam" "sam I am" "he bob" "Who is sam?"   
    Match(s1='I am Sam', s2='sam I am', score=5.0)
    Match(s1='I am Sam', s2='Who is sam?', score=3.0)
```

```commandline
$ ./fuzzy_match.py Mary Marie Annmarie marry Jill "She will marry Marie"
    Match(s1='Mary', s2='She will marry Marie', score=1.4)
    Match(s1='Mary', s2='marry', score=0.8)
    Match(s1='Mary', s2='Marie', score=0.6)
    Match(s1='Mary', s2='Annmarie', score=0.375)
```

## Time Comparison
```python
s1 = open('test_files/christmas_carol.txt').read()
s2 = open('test_files/winnie_the_pooh.txt').read()
# Just edit distance
%timeit compute_distance(s1, s2, all_edits=False)
    7.76 s ± 305 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
%timeit edit_distance.edit_distance(s1,s2)
    3.74 s ± 50.4 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
# Keeping track of all edits
%timeit compute_distance(s1, s2, all_edits=True)
    7.26 s ± 118 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
%timeit edit_distance.edit_distance_backpointer(s1,s2)
    3.91 s ± 57.7 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
```