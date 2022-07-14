#!/usr/bin/env python

"""
Fuzzy Match Algorithm for Cobalt
7/13/2022
David C. Morley

My fuzzy string matching algorithm is based on the approach in:
    J. Wang, G. Li and J. Fe, "Fast-join: An efficient method
    for fuzzy token matching based string similarity join,"
    2011 IEEE 27th International Conference on Data Engineering,
    2011
However, it does not utilize the Jaccard distance
"""

from collections import namedtuple

EQUAL = 0
SUBST = 1
INSRT = 2
DELET = 3
TRANS = 4
Match = namedtuple('Match', ['s1', 's2', 'score'])
Edit = namedtuple('Edit', ['edit_type', 'weight'])


def min_score(tuples):
    """Given a named tuple edit_tag: weight, return a tuple of the min tag and its weight."""
    return min(tuples, key=lambda x: x.weight)


def compute_distance(s1, s2, sub_weight=1, ins_weight=1, del_weight=1, trans_weight=0):
    """Given two strings (or lists) compute the minimum edit distance
    Types of Distance:
        - The Levenshtein distance allows deletion, insertion and substitution.
        - The Damerau–Levenshtein distance allows insertion, deletion, substitution, and transposition.
    Parameters:
        s1, s2 (str) - the strings to compare
        sub_weight, ins_weight, del_weight (float) - the weights for each operation
        trans_weight. (float) - the weight for transposition operation, Levenshtein distance if 0
    """
    l1, l2 = len(s1) + 1, len(s2) + 1        # Add 1 to handle empty strings
    scores = {0: {i: Edit(INSRT, i) for i in range(l2)}}
    # For every word in both texts
    for i in range(1, l1):
        scores[i] = {0: Edit(DELET, i)}
        for j in range(1, l2):
            # You don't have to change anything, the error hasn't changed
            if s1[i - 1] == s2[j - 1]:
                scores[i][j] = Edit(EQUAL, scores[i - 1][j - 1].weight)
            # Something happened
            else:
                scores[i][j] = min_score([Edit(SUBST, scores[i - 1][j - 1].weight + sub_weight),
                                          Edit(INSRT, scores[i][j - 1].weight + ins_weight),
                                          Edit(DELET, scores[i - 1][j].weight + del_weight),
                                          ])
                # If Damerau–Levenshtein distance
                if trans_weight and i > 1 and j > 1 and s1[i-1] == s2[j-2] and s1[i-2] == s2[j-1]:
                    scores[i][j] = min_score([scores[i][j],
                                              Edit(TRANS, scores[i - 2][j - 2].weight + trans_weight),
                                              ])
    return scores[l1 - 1][l2 - 1].weight


def ned(t1, t2, weights):
    """
    NED (Normalized Edit Distance) := 1 - edit_distance / max str length
    Parameters:
        t1 (str) - the search token
        t2 (str) - the token to match against
        weights (dict) - a mapping of the edit weights for compute_distance
    Returns:
        (float) normalized edit distance
    """
    l1, l2 = len(t1), len(t2)
    return 1 - compute_distance(t1, t2, **weights) / max(l1, l2)


def tokenize(s):
    """
    Returns a set of tokens from a string
    Parameters:
        s (str or list) - the input string to tokenize
    Returns:
        a set of tokens for each input string (so can be list of sets)
    """
    if isinstance(s, str):
        return set(s.lower().split())
    elif isinstance(s, list):
        return [set(t.lower().split()) for t in s]
    else:
        raise ValueError(f"Unsupported input {repr(s)}")


def fuzzy_match(t1, t2, thresh, weights):
    """
    Computes the fuzzy match score of two token strings
    Parameters:
        t1 (str) - the search token
        t2 (str) - the token to match against
        thresh (float) - the threshold for how similar the words must be
        weights (dict) - a mapping of the edit weights for compute_distance
    Returns:
        Match object containing the two strings and their similarity score
    """
    # Check if no letters in common
    if not set(t1) & set(t2):
        score = 0.0
    # Check if one string contains the other
    elif t1 in t2 or t2 in t1:
        score = 1.0
    else:
        score = ned(t1, t2, weights)

    # Check that score exceeds threshold
    if score >= thresh:
        return Match(t1, t2, score)
    else:
        return Match(t1, t2, 0.)


def main(string1, string2, min_distance, weights):
    """
    Driving function. Takes search string, compares against doc strings and print best matches.
    Parameters:
        string1 (str) - the search string
        string2 (list(str)) - the documents to search against
        min_distance (float) - the threshold for how similar the words must be
        weights (dict) - a mapping of the edit weights for compute_distance
    """
    matches = []
    t1, docs = tokenize(string1), tokenize(string2)
    # For each document string compare each token in the search string and add doc level score
    for idx, t2 in enumerate(docs):
        doc_score = 0
        for s1 in t1:
            for s2 in t2:
                doc_score += fuzzy_match(s1, s2, min_distance, weights).score
        matches.append(Match(string1, string2[idx], doc_score))
    # Sort matches by best score and print nonzero results
    for match in sorted(matches, key=lambda x: x.score, reverse=True):
        if match.score:
            print(match)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fuzzy Match: An algorithm to determine the similarity of strings')
    parser.add_argument('s1', metavar='input_string', type=str, help='the string to search for')
    parser.add_argument('s2', metavar='search_string', type=str, nargs='+', help='the string (or strings) to search in')
    parser.add_argument('-m', '--min_distance', type=float, default=.3, help='the cutoff threshold for edit distance')
    parser.add_argument('-s', '--sub_weight', type=float, default=1, help='weight for substitution operation')
    parser.add_argument('-d', '--del_weight', type=float, default=1, help='weight for deletion operation')
    parser.add_argument('-i', '--ins_weight', type=float, default=1, help='weight for insertion operation')
    parser.add_argument('-t', '--trans_weight', type=float, default=0, help='weight for transposition operation')

    args = parser.parse_args()
    edit_weights = {
        'sub_weight': args.sub_weight,
        'ins_weight': args.ins_weight,
        'del_weight': args.del_weight,
        'trans_weight': args.trans_weight
    }
    main(args.s1, args.s2, args.min_distance, edit_weights)
