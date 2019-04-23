"""
Get keywords in a target corpus.
Adapted from
Earl K. Brown, ekbrown byu edu (add appropriate characters to create email)
which was based on code written by Adam Davies
"""
from collections import defaultdict
import json
from math import log2
import os
import re
import time

import pandas as pd

start = time.time()


def get_num_wds_freqs(filename):
    """Helper function to retrieve the number of words and the frequencies of those words in a directory"""  # noqa

    freqs = defaultdict(int)
    num_wds = 0

    all_text = ''
    with open(filename) as infile:

        abstract_dicts = [json.loads(line) for line in infile]

    for ad in abstract_dicts:
        try:
            all_text += ad['abstract'][1]
            all_text += ad['title']
        except:  # noqa
            continue

    wds = re.split(r"[^-'a-záéíóúüñ]+", all_text, flags=re.I)
    wds = [wd.upper() for wd in wds if len(wd) > 0]
    num_wds += len(wds)
    for wd in wds:
        freqs[wd] += 1
    print("There are " + "{:,}".format(num_wds) + f" words in {filename}\n")  # noqa

    return (num_wds, freqs)


def main(target_file, ref_file, num_keywords=10, min_freq=3):
    """Get keywords in .txt files within a target directory, comparing them with words in .txt files within a reference directory.
    param: target_dir - the directory with the target corpus in .txt files
    param: ref_dir - the directory with the reference corpus in .txt files
    param: num_keywords - number of keywords desired
    param: min_freq - the minimum frequency of keywords in the target corpus
    return value: a pandas DataFrame with three columns: (1) keyword, (2) frequency in target corpus, (3) keyness score
    """

    # get number of words and freqs in target and reference directories
    print()
    target_num_wds, target_freqs = get_num_wds_freqs(target_file)
    ref_num_wds, ref_freqs = get_num_wds_freqs(ref_file)

    # calculate frequency ratio between target corpus and reference corpus
    rel_freq = target_num_wds / ref_num_wds

    # calculate keyness
    keywords = {}
    for wd in sorted(target_freqs, key=lambda x:target_freqs[x], reverse=True):  # noqa
        if target_freqs[wd] >= min_freq:
            if wd in ref_freqs:
                keywords[wd] = log2((target_freqs[wd] * rel_freq) / ref_freqs[wd])  # noqa

    # sort keywords and limit to number desired by user
    top_keywords = [kw for kw in sorted(keywords, key=lambda x:keywords[x], reverse=True)][:num_keywords]  # noqa

    # push keywords to pandas DataFrame
    df = pd.DataFrame(columns=["keyword", "freq", "keyness"])  # noqa

    for kw in top_keywords:
        df = df.append({'keyword': kw, "freq": target_freqs[kw], "keyness": "{:.4}".format(keywords[kw])}, ignore_index=True)

    return df


# test the function
# target_dir = "/Users/ekb5/Documents/LING_580R/gen_conf/"
# ref_dir = "/Users/ekb5/Corpora/Brown/"
# num_keywords = 10
# min_freq = 3


if __name__ == '__main__':
    main(target_file, ref_file, num_keywords, min_freq)
