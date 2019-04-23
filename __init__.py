"""
- random_sample('term') || pprints a mini-corpus entry for the given term
- pos_tag('term')
- authored_by('author') || pprints abstracts w/metadata with this author across all mini-corpora in metaresearch/  # noqa
- beautiful thing about this format is allowance of one-off integrations such as single google searches about author bio
- concordance/KwiC
- kwic('term', sortby) || pprints minicorp \t prewords TERM postwords

- search() appends to the file if exists already for the term, removes duplicates
- create and store corpora in Downloads folder? but would need Pathlib hacks
- subprocesses with headless shells might be a better solution for some of these

- keywords against YOUR writings as a reference corpus to see what is different about theirs/yours
- this would require the abstract parser from pdf or txt or doc or tex

- article_info from any starting param, given another argument
- dispersion as keywords
"""
# import the scraper modules for each individual publisher
import elsevier
import keywords
# import the external dependencies
from collections import defaultdict as dd
from glob import glob
import json
import matplotlib as plt


def article_info(title_string):
    """
    """
    search_expr = title_string[:15]
    searching = True

    while searching:

        for minicorp in glob('metaresearch/*.json'):

            with open(minicorp) as infile:
                abstract_dicts = [json.loads(line) for line in infile]

            for ad in abstract_dicts:
                if ad['title'].startswith(search_expr):
                    target_ad = ad
                    searching = False

    print()
    print('TITLE:', target_ad['title'], sep='\t\t')  # noqa
    print('AUTHOR(S):', target_ad['auth'], sep='\t\t')  # loop over
    print('DATE:', target_ad['date_of_pub'], sep='\t\t')  # unpack
    print('PUBLICATION:', target_ad['publication'], sep='\t\t')
    print('URL:', target_ad['url'], sep='\t\t')
    print('ABSTRACT:\n', target_ad['abstract'], sep='\t')
    print('KEYWORDS:', target_ad['keywords'], sep='\t\t')  # loop over
    print()


def show_corpora():
    """
    """
    try:
        print()
        for minicorp in glob('metaresearch/*.json'):
            minicorp_end = minicorp.split('/')[-1]
            minicorp_name = minicorp_end.split('.')[0]
            print(minicorp_name)
        print()
    except:  # noqa
        print('\nIt looks like you do not have any mini-corpora yet. Try metaresearch.search(\'yourtermhere\') first.')  # noqa


def authored_by(author):
    """
    """
    authored = {}

    for minicorp in glob('metaresearch/*.json'):

        with open(minicorp) as infile:
            abstract_dicts = [json.loads(line) for line in infile]

        for ad in abstract_dicts:
            if author in ad['auth']:
                authored[minicorp] = ad

    if authored:
        print()
        for minicorp, ad in authored.items():
            minicorp_name = minicorp.split('/')[1]
            print(minicorp_name[:30], ad['title'], sep='\t\t')  # noqa
        print()
    else:
        print(f'\nA search for {author} returned no results.\n')  # noqa


def compare_authors(term1, term2):
    """
    """
    auths_dict = dd(list)

    for t in term1, term2:

        with open(f'metaresearch/{t}.json') as infile:  # noqa
            abstract_dicts = [json.loads(line) for line in infile]

        for ad in abstract_dicts:
            num_auth = len(ad['auth'])
            for i in range(num_auth):
                auths_dict[t] += ad['auth']

    overlap = set([v for v in auths_dict[term1] if v in auths_dict[term2]])

    if overlap:
        print()
        for i in overlap:
            print(i)
        print()
    else:
        print(f'\nNo overlapping authors between these subsets of {term1} and {term2} articles.\n')  # noqa


def list_authors(term):
    """
    """
    with open(f'metaresearch/{term}.json') as infile:  # noqa
        abstract_dicts = [json.loads(line) for line in infile]

    for ad in abstract_dicts:
        num_auth = len(ad['auth'])
        for i in range(num_auth):
            print(ad['auth'][i])


def get_keywords(term1, term2):
    """
    """
    target_dir = glob(f'metaresearch/{term1}*')[0]
    ref_dir = glob(f'metaresearch/{term2}*')[0]
    df = keywords.main(target_dir, ref_dir)
    print(f'\nThese are the keywords for {term1} when compared to {term2}.\n')
    print(df)
    print()


def search(term):
    """ """
    elsevier.main(term)


if __name__ == '__main__':
    search(term)
    list_authors(term)
    compare_authors(term1, term2)
