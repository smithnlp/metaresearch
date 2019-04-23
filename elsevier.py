"""
The Elsevier scraper module for metaresearch.
"""
import json
import os
from pathlib import Path
import random
import re
import requests_html
import sys
import time

from pprint import pprint


def parse_pub(publication_text):
    """
    """
    match = re.search(r' ((?:\d+)?\s?[A-Z]\D+?)\s(20\d\d),', publication_text)
    if match:
        # era is sometimes 'January', sometimes 'Winter', sometimes '21 Jan'
        era = match.group(1)
        year = int(match.group(2))
        return era, year
    else:
        return None, None


def parse_abbrevs(abstract):
    """Given a paragraph of abbreviations, transform into a python dictionary
    in the form of {'FEV': 'Fully Expanded Version', ...}

    TODO:
    - extract abbrevs from runnining abstract text ([A-Z][a-z]+)+\s([A-Z])
    - would be useful for other publishers who may not have a section for these
    """
    pass
    # return abbrev_dict


def parse_abstract(elsevier_abstracts):
    """Transform Elsevier's two-abstract format of the extracted Highlights and
    the author's submitted paragraph abstract.

    TODO:
    - not all have the header `Abstract`
    #abss0001
    //*[@id="abss0001"]  except within a div class="abstract author"
    - try/else/except??
    """
    match = re.match(r'^(Highlights.*?)?(Abstract.*\.)',
                     elsevier_abstracts, re.S)

    try:
        highlights = match.group(1)
        # not all articles have highlights, this defaults to None
        # parse into a python dict if there are any highlights
        points = re.findall(r'•\s?(\w+.*?\.)$', highlights, re.S | re.M)
        highlights = {}  # be sure to rename after used in regex above
        counter = 1
        for p in points:
            # we want to maintain the order of these points
            highlights[str(counter)] = p
            counter += 1
    except:  # noqa
        highlights = None

    try:
        abstract = match.group(2)
        # we just want the text
        abstract = re.sub(r'\s?Abstract\s+', '', abstract)
    except:  # noqa
        abstract = None

    # return a tuple as     highlights : dict, abstract : string
    return highlights, abstract


def get_article_info(article_links, session):
    """
    """
    all_info = []

    print(f'\nParsing and saving abstract and metadata for {len(article_links)} urls.\n')  # noqa
    for link in article_links:

        article_info = {}
        r = session.get(link)

        article_info['url'] = link

        try:
            title = r.html.find('.title-text')
            title = [i.text for i in title]
            article_info['title'] = title[0]
        except:  # noqa
            continue

        try:
            abstract = r.html.find('#abstracts')
            abstract = [i.text for i in abstract]
            # parse format into a tuple as    highlights : dict, abstract : string  # noqa
            article_info['abstract'] = parse_abstract(abstract[0])
        except:  # noqa
            continue

        # account for lone and multiple authors and superscript
        # SOLUTION: given_name + surname for every author
        authors = []
        for i in range(30):
            a_givname = r.html.xpath(f'//*[@id="author-group"]/a[{i}]//span[@class="text given-name"]')  # noqa
            a_surname = r.html.xpath(f'//*[@id="author-group"]/a[{i}]//span[@class="text surname"]')  # noqa
            a_givname = [a.text for a in a_givname]
            a_surname = [a.text for a in a_surname]
            try:
                author = a_givname[0] + ' ' + a_surname[0]
                if len(author) > 0:
                    authors.append(author)
            except:  # noqa
                continue

        article_info['auth'] = authors

        try:
            publication = r.html.find('#publication')
            publication = [i.text for i in publication]
            # TODO: parse this into journal, vol, issue, pages as well
            article_info['publication'] = publication[0]
        except:  # noqa
            article_info['publication'] = None

        try:
            # format date into tuple as     era : string, year : int
            article_info['date_of_pub'] = parse_pub(publication[0])
        except:  # noqa
            article_info['date_of_pub'] = None

        try:
            keywords = r.html.find('.keywords-section')
            keywords = [i.text for i in keywords]
            # format as a list of keywords, removing the 'Keywords' label
            article_info['keywords'] = keywords[0].split('\n')[1:]
        except:  # noqa
            article_info['keywords'] = None

        if len(article_info['title']) > 79:
            print(article_info['title'][:79], '...', sep='')
        else:
            print(article_info['title'])

        time.sleep(random.uniform(.5, 3))
        all_info.append(article_info)

    return all_info


def get_links(term, session):
    """
    """
    url = f'https://www.sciencedirect.com/search/advanced?date=2015-2019&tak={term}&show=100&sortBy=relevance'  # noqa
    r = session.get(url)
    article_links = []

    print(f'\nGrabbing 100 or so article urls related to {term} from {r.url}.\n')  # noqa

    # because returning 100 per page and each link is enumerated
    for i in range(101):
        link = r.html.xpath(f'//*[@id="aa-srp-result-list-title-{i}"]/a/@href')
        article_links.append(link)
        print('.', end='', flush=True)

    print('', flush=True)

    # prepend the base url to each of the slugs
    article_links = [f'https://www.sciencedirect.com{i[0]}' for i in article_links if len(i) > 0]  # noqa

    return article_links


def main(term):
    """Instantiate an HTML session and our list of terms. Process the dict
    of terms, and write out human-readable results to file.
    """
    session = requests_html.HTMLSession()

    article_links = get_links(term, session)

    all_info = get_article_info(article_links, session)

    basepath = os.getcwd()

    # create the metaresearch directory if it doesn't already exist
    if os.path.isdir('metaresearch/'):
        print(f'\nSaving mini-corpus to "metaresearch/{term}.json" ... ', end='')  # noqa
    else:
        print(f'\nCreating a directory "metaresearch" in the current working directory, then saving mini-corpus to "metaresearch/{term}.json"\n')  # noqa
        os.mkdir(f'{basepath}/metaresearch')

    mini_corp_path = f'{basepath}/metaresearch/{term}.json'

    with open(mini_corp_path, 'w') as outfile:

        for article_info in all_info:
            outfile.write(json.dumps(article_info))
            outfile.write('\n')

    print(f'Success!\n')


if __name__ == '__main__':
    main(term)
