#!/usr/bin/env python3
"""Get Rosette API named entity results in CoNLL 2003-style BIO format"""

import csv
import json
import os
import sys
from getpass import getpass

EXTERNALS = 'argparse', 'rosette_api'
try:
    import argparse
    from rosette.api import API, DocumentParameters
except ImportError:
    message = '''This script depends on the following modules:
    {}
If you are missing any of these modules, install them with pip3:
    $ pip3 install {}'''
    print(
        message.format('\n\t'.join(EXTERNALS), ' '.join(EXTERNALS)),
        file=sys.stderr
    )
    sys.exit(1)

# CoNLL 2003-style B(eginning) I(nside) O(utside) tags
B, I, O = 'B-{}', 'I-{}', 'O'
# CoNLL 2003 fields
CONLL2003 = 'word-token', 'part-of-speech-tag', 'chunk-tag', 'named-entity-tag'
# Default Rosette API URL
DEFAULT_ROSETTE_API_URL = 'https://api.rosette.com/rest/v1/'

def extent(obj):
    """Get the start and end offset attributes of a dict-like object
    
    a = {'startOffset': 0, 'endOffset': 5}
    b = {'startOffset': 0, 'endOffset': 10}
    c = {'startOffset': 5, 'endOffset': 10}
    
    extent(a) -> (0, 5)
    extent(b) -> (0, 10)
    extent(c) -> (5, 10)
    extent({}) -> (-1, -1)
    
    """
    return obj.get('startOffset', -1), obj.get('endOffset', -1)

def overlaps(*objs):
    """Find character offsets that overlap between objects
    
    a = {'startOffset': 0, 'endOffset': 5}
    b = {'startOffset': 0, 'endOffset': 10}
    c = {'startOffset': 5, 'endOffset': 10}
    
    overlaps(a, b) -> {0, 1, 2, 3, 4}
    bool(overlaps(a, b)) -> True
    
    overlaps(b, c) -> {5, 6, 7, 8, 9}
    bool(overlaps(b, c)) -> True
    
    overlaps(a, c) -> set()
    bool(overlaps(a, c)) -> False
    
    """
    return set.intersection(*(set(range(*extent(obj))) for obj in objs))

def load_content(txtfile):
    """Load data from a plain-text file"""
    with open(txtfile, mode='r') as f:
        return f.read()

def get_entities(content, key, url, language=None):
    """Get Rosette API named entity results for the given content
    
    This method gets results of the "entities" endpoint of the Rosette API.
    The result is an A(nnotated) D(ata) M(odel) or ADM that is a Python dict
    representing a document, annotations of the document content, and metadata.
    
    content: the textual content of a document for the Rosette API to process
    key: your Rosette user key
    url: the URL of the Rosette API
    language: an optional ISO 639-2 T language code (the Rosette API will
    automatically detect the language of the content by default)
    
    """
    api = API(user_key=key, service_url=url)
    # Request result as Annotated Data Model (ADM)
    api.setUrlParameter("output", "rosette")
    parameters = DocumentParameters()
    parameters['content'] = content
    parameters['language'] = language
    adm = api.entities(parameters)
    return adm

def entity_mentions(adm):
    """Generate named entity mentions from an ADM (Annotated Data Model)
    
    The ADM contains an "entities" attribute that groups mentions of the
    same entity together in a "mentions" attribute per entity.  Each entity has
    a head mention index, an entity type, an entity identifier, a confidence
    score, and a list of mentions. Each entity mention contains additional 
    information including its start and end character offsets referring to the 
    array of characters in the document content (i.e., the adm["data"]).
    
    Consider an ADM with the following content:
    
    adm["data"] == "New York City or NYC is the most populous city in the United States."
    
    Then the "entities" attribute would be:
    
    adm["attributes"]["entities"] == {
        "items": [
            {
                "headMentionIndex": 0, 
                "mentions": [
                    {
                        "source": "gazetteer", 
                        "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin", 
                        "normalized": "New York City", 
                        "startOffset": 0, 
                        "endOffset": 13
                    }, 
                    {
                        "source": "gazetteer", 
                        "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin", 
                        "normalized": "NYC", 
                        "startOffset": 17, 
                        "endOffset": 20
                    }
                ], 
                "confidence": 0.501718114501715, 
                "type": "LOCATION", 
                "entityId": "Q60"
            }, 
            {
                "headMentionIndex": 0, 
                "mentions": [
                    {
                        "source": "gazetteer", 
                        "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin", 
                        "normalized": "United States", 
                        "startOffset": 55, 
                        "endOffset": 68
                    }
                ], 
                "confidence": 0.08375498050536179, 
                "type": "LOCATION", 
                "entityId": "Q30"
            }
        ], 
        "type": "list", 
        "itemType": "entities"
    }
    
    This method generates a list of all named entity mentions augmented with 
    the named entity type of the the entity it refers to.
    
    entity_mentions(adm) -> <generator object entity_mentions at 0xXXXXXXXXX>
    
    Since the mentions are grouped by the entity they refer to, it is useful to
    get a list of the mentions in the order they appear in the document.  We can
    do this by sorting the mentions by their extent, i.e., their start and end
    character offsets:
    
    sorted(entity_mentions(adm), key=extent) -> [
        {
            "source": "gazetteer", 
            "normalized": "New York City", 
            "startOffset": 0, 
            "endOffset": 13, 
            "type": "LOCATION", 
            "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin"
        }, 
        {
            "source": "gazetteer", 
            "normalized": "NYC", 
            "startOffset": 17, 
            "endOffset": 20, 
            "type": "LOCATION", 
            "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin"
        }, 
        {
            "source": "gazetteer", 
            "normalized": "United States", 
            "startOffset": 55, 
            "endOffset": 68, 
            "type": "LOCATION", 
            "subsource": "/data/roots/rex/data/gazetteer/eng/accept/gaz-LE.bin"
        }
    ]
        
    """
    for entity in adm['attributes']['entities']['items']:
        for mention in entity['mentions']:
            # Augment mentions with the entity type of the entity they refer to
            mention['type'] = entity['type']
            yield mention

def conll2003(adm, use_conll_ne_tags=True):
    """Generate CoNLL 2003-style named entity rows from a Rosette API result
    
    Taking an example ADM:
    adm["data"] == "New York City or NYC is the most populous city in the United States."
    
    Then the output would be:
    
    conll2003(adm) -> <generator object conll2003 at 0xXXXXXXXXX>
    
    list(conll2003(adm)) ->
    [
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "B-LOC", 
            "word-token": "New"
        }, 
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "I-LOC", 
            "word-token": "York"
        }, 
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "I-LOC", 
            "word-token": "City"
        }, 
        ...
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "B-LOC", 
            "word-token": "United"
        }, 
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "I-LOC", 
            "word-token": "States"
        }, 
        {
            "chunk-tag": "", 
            "part-of-speech-tag": "", 
            "named-entity-tag": "O", 
            "word-token": "."
        }
    ]
    
    """
    # Map Rosette named entity types to CoNLL 2003 named entity types
    CONLL2003_NE_TYPES = {
        'PERSON': 'PER',
        'LOCATION': 'LOC',
        'ORGANIZATION': 'ORG'
    }
    # Access the entity mentions, sentences, and tokens from the ADM
    mentions = sorted(entity_mentions(adm), key=extent)
    sentences = adm['attributes']['sentence']['items']
    tokens = adm['attributes']['token']['items']
    # Assign a CoNLL2003-style named entity tag to each token
    for token in tokens:
        sentence = sentences[0] if sentences else {}
        mention = mentions[0] if mentions else {}
        # Add empty rows between sentences
        if min(extent(token)) == min(extent(sentence)):
            yield {k : '' for k in CONLL2003}
            sentences.pop(0)
        bio = O
        if min(extent(token)) == min(extent(mention)):
            bio = B
        elif overlaps(token, mention):
            bio = I
        if max(extent(token)) == max(extent(mention)):
            mentions.pop(0)
        if use_conll_ne_tags:
            entity_type = CONLL2003_NE_TYPES.get(mention.get('type'), 'MISC')
        else:
            entity_type = mention.get('type')
        yield {
            'word-token': adm['data'][slice(*extent(token))],
            'part-of-speech-tag': '', # we can't get this with a single API call
            'chunk-tag': '', # Rosette doesn't currently do syntactic chunking
            'named-entity-tag': bio.format(entity_type)
        }

def main(adm, use_conll_ne_tags):
    """Given an ADM, write CoNLL 2003-style named entity rows to stdout"""
    writer = csv.DictWriter(sys.stdout, fieldnames=CONLL2003, delimiter=' ')
    # document header row
    writer.writerow({
        'word-token': '-DOCSTART-',
        'part-of-speech-tag': '-X-',
        'chunk-tag': O,
        'named-entity-tag': O
    })
    writer.writerows(conll2003(adm, use_conll_ne_tags))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        'input',
        help='A plain-text document to process'
    )
    parser.add_argument(
        '-k',
        '--key',
        help='Rosette API Key',
        default=None
    ),
    parser.add_argument(
        '-u',
        '--url',
        help='Alternative API URL',
        default=DEFAULT_ROSETTE_API_URL
    )
    parser.add_argument(
        '-l',
        '--language',
        help='A three-letter (ISO 639-2 T) code that will override automatic language detection',
        default=None
    )
    parser.add_argument(
        '--use-conll-ne-tags',
        action='store_true',
        help="Use CoNLL 2003 named entity tags (instead of Rosette API's named entity tags)"
    )
    args = parser.parse_args()
    key = args.key
    if key is None:
        key = getpass(prompt='Enter your Rosette API key: ')
    content = load_content(args.input)
    # Get ADM (Annotated Data Model) results from Rosette API
    adm = get_entities(content, key, args.url, args.language)
    main(adm, args.use_conll_ne_tags)
