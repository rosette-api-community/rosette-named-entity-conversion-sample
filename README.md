#Introduction
This repository contains an example Python script demonstrating how one might go about converting results from Rosette API's named entity extraction to the data format used in the [CoNLL 2003 shared task for named entity extraction](http://www.aclweb.org/anthology/W03-0419).

##The Annotated Data Model
To convert the named entity annotations we take advantage of [Rosette's A(nnotated) D(ata) M(odel)]((https://github.com/basis-technology-corp/annotated-data-model)) via the Python bindings.  The following is a sample ADM one might receive as a result when you set the `"output"` parameter to `"rosette"` and make an `entities` call to the Rosette API:

    {
        "data": "New York City or NYC is the most populous city in the United States.\n",
        "attributes": {
            "entities": {
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
                                "startOffset": 54, 
                                "endOffset": 67
                            }
                        ], 
                        "confidence": 0.08375498050536179, 
                        "type": "LOCATION", 
                        "entityId": "Q30"
                    }
                ], 
                "type": "list", 
                "itemType": "entities"
            }, 
            "token": {
                "items": [
                    {
                        "text": "New", 
                        "startOffset": 0, 
                        "endOffset": 3
                    }, 
                    {
                        "text": "York", 
                        "startOffset": 4, 
                        "endOffset": 8
                    }, 
                    {
                        "text": "City", 
                        "startOffset": 9, 
                        "endOffset": 13
                    }, 
                    {
                        "text": "or", 
                        "startOffset": 14, 
                        "endOffset": 16
                    }, 
                    {
                        "text": "NYC", 
                        "startOffset": 17, 
                        "endOffset": 20
                    }, 
                    {
                        "text": "is", 
                        "startOffset": 21, 
                        "endOffset": 23
                    }, 
                    {
                        "text": "the", 
                        "startOffset": 24, 
                        "endOffset": 27
                    }, 
                    {
                        "text": "most", 
                        "startOffset": 28, 
                        "endOffset": 32
                    }, 
                    {
                        "text": "populous", 
                        "startOffset": 33, 
                        "endOffset": 41
                    }, 
                    {
                        "text": "city", 
                        "startOffset": 42, 
                        "endOffset": 46
                    }, 
                    {
                        "text": "in", 
                        "startOffset": 47, 
                        "endOffset": 49
                    }, 
                    {
                        "text": "the", 
                        "startOffset": 50, 
                        "endOffset": 53
                    }, 
                    {
                        "text": "United", 
                        "startOffset": 54, 
                        "endOffset": 60
                    }, 
                    {
                        "text": "States", 
                        "startOffset": 61, 
                        "endOffset": 67
                    }, 
                    {
                        "text": ".", 
                        "startOffset": 67, 
                        "endOffset": 68
                    }
                ], 
                "type": "list", 
                "itemType": "token"
            }, 
            "scriptRegion": {
                "items": [
                    {
                        "script": "Latn", 
                        "startOffset": 0, 
                        "endOffset": 69
                    }
                ], 
                "type": "list", 
                "itemType": "scriptRegion"
            }, 
            "languageDetection": {
                "detectionResults": [
                    {
                        "confidence": 0.981137482980466, 
                        "script": "Latn", 
                        "language": "eng", 
                        "encoding": "UTF-16BE"
                    }
                ], 
                "type": "languageDetection", 
                "startOffset": 0, 
                "endOffset": 69
            }, 
            "sentence": {
                "items": [
                    {
                        "startOffset": 0, 
                        "endOffset": 69
                    }
                ], 
                "type": "list", 
                "itemType": "sentence"
            }
        }, 
        "responseHeaders": {
            "X-RosetteAPI-Concurrency": "2", 
            "transfer-encoding": "chunked", 
            "Strict-Transport-Security": "max-age=63072000; includeSubdomains; preload", 
            "Server": "openresty", 
            "Connection": "keep-alive", 
            "X-RosetteAPI-Request-Id": "a53453af-7c40-4bd3-8849-513405f7cba0", 
            "Content-Encoding": "gzip", 
            "Vary": "Accept-Encoding", 
            "X-RosetteAPI-App-Id": "1409612466626", 
            "Date": "Tue, 29 Nov 2016 21:31:11 GMT", 
            "Content-Type": "application/json"
        }, 
        "version": "1.1.0", 
        "documentMetadata": {
            "processedBy": [
                "whole-document-language@10.233.73.125", 
                "entity-extraction@10.233.177.187", 
                "entity-linking@10.233.177.187"
            ], 
            "res-docid": [
                "res-document-964ec8f4-f361-494f-828b-0bc746decdc0"
            ]
        }
    }

From this result we can access all the information we need to pull out the entity extractions and format them in the way we want.

##`rosette_to_conll2003.py`
This script traverses the words, sentences, and named entities identified in the ADM to produce CoNLL 2003-style output with one token per line.

###Installing Dependencies with Virtualenv
The script is written for Python 3.  If you are alright with installing external Python packages globally, you may skip this section.

You can install the dependencies using `virtualenv` so that you don't alter your global site packages.

The process for installing the dependencies using `virtualenv` is as follows for `bash` or similar shells:

Ensure your `virtualenv` is up to date.

    $ pip install -U virtualenv

**Note**: You may need to use `pip3` depending on your Python installation.

`cd` into the directory where the `rosette_to_conll2003.py` script exists and create a Python virtual environment (this is the same location as this README):

    $ virtualenv .

Activate the virtual environment:

    $ source bin/activate

Once you've activated the virtual environment you can proceed to install the requirements safely without affecting your globabl site packages.

###Installing the Dependencies
You can install the dependencies via `pip` (or `pip3` depending on your installation of Python 3) as follows using the provided `requirements.txt`:

    $ pip install -r requirements.txt

###Usage
Once you've installed the dependencies you can run the script as follows:

    $ ./rosette_to_conll2003.py -h
    usage: rosette_to_conll2003.py [-h] [-k KEY] [-u URL] [-l LANGUAGE] input
    
    Get Rosette API named entity results in CoNLL 2003-style BIO format
    
    positional arguments:
      input                 A plain-text document to process
    
    optional arguments:
      -h, --help            show this help message and exit
      -k KEY, --key KEY     Rosette API Key (default: None)
      -u URL, --url URL     Alternative API URL (default:
                            https://api.rosette.com/rest/v1/)
      -l LANGUAGE, --language LANGUAGE
                            A three-letter (ISO 639-2 T) code that will override
                            Rosette language detection (default: None)

If you do not use the `--key` option the script will prompt you to type in your Rosette API key before running.  If you find yourself running the script repeatedly, it may be convenient to set your Rosette API key as an environment variable in your shell:

    $ export ROSETTE_USER_KEY=<your user key>

Then you can add your key as an option with `-k $ROSETTE_USER_KEY`.

###Example
The CoNLL 2003 data format has 4 fields separated by spaces:

| Field | Description                |
|:-----:|----------------------------|
| 1     | A word token               |
| 2     | A part-of-speech (POS) tag |
| 3     | A syntactic chunk tag      |
| 4     | A named entity tag         |

The following is a sample sentence annotated in the [CoNLL 2003 format](http://www.aclweb.org/anthology/W03-0419):

    U.N. NNP I-NP I-ORG
    official NN I-NP O
    Ekeus NNP I-NP I-PER
    heads VBZ I-VP O
    for IN I-PP O
    Baghdad NNP I-NP I-LOC
    . . O O

The ConLL 2003 format uses so-called BIO or B(egining) I(nside) O(outside) tags to indicate the relative position of word tokens within named entity boundaries.  Tokens that are part of a named entity are suffixed with a named entity type: `LOC`, `ORG` `PER`, or `MISC`.  Note that the first word within a named entity gets prefixed with `B-` because it is at the *beginning* of the mention.  Subsequent tokens within a named entity are prefixed with `I-` indicating they are *inside* the entity mention.  All other tokens that are *outside* of an entity mention are tagged as `O`.

**Note**: In this example we will ignore the second field.  You can get POS tags from the [Rosette API via the `morphology/parts-of-speech` endpoint](https://developer.rosette.com/features-and-functions#parts-of-speech), but that is a separate API call, and we are only concerned with the named entity tags here.  Rosette does not currently offer syntactic chunking, so we will also ignore the third field (though we do offer [dependency parsing](https://developer.rosette.com/features-and-functions#syntactic-dependencies)).  In the fourth and final field, we use Rosette named entity tags, which includes a larger, more informative set of named entity tags than the four tags used in the CoNLL 2003 shared task.

You view the example text, `example/ny.txt`, as follows:

    $ cat example/ny.txt 
    New York City or NYC is the most populous city in the United States.

You can run the script on the example file as follows:

    $ ./rosette_to_conll2003.py example/ny.txt
    Enter your Rosette API key: 
    -DOCSTART- -X- O O
   
    New   B-LOCATION
    York   I-LOCATION
    City   I-LOCATION
    or   O
    NYC   B-LOCATION
    is   O
    the   O
    most   O
    populous   O
    city   O
    in   O
    the   O
    United   B-LOCATION
    States   I-LOCATION
    .   O

To translate Rosette API named entity tags to CoNLL 2003 named entity tags, use the `--use-conll-ne-tags` option:

    $ ./rosette_to_conll2003.py --use-conll-ne-tags example/ny.txt
    Enter your Rosette API key: 
    -DOCSTART- -X- O O
   
    New   B-LOC
    York   I-LOC
    City   I-LOC
    or   O
    NYC   B-LOC
    is   O
    the   O
    most   O
    populous   O
    city   O
    in   O
    the   O
    United   B-LOC
    States   I-LOC
    .   O
