# Regression Test for MWE Query

## Introduction
We describe here a regressiontest and a comparison with gold reference data.

## Regressiontest

The module *mweregressiontest.py* contains functions to do a regression tets, i.e. a test to ensure that after some modifications the system's performance does not get worse.

One can run the regression test by simply running this module:

`python mweregressiontest.py`

It does the following:
- For each (mwe, utterance) pair in the regressiondata it counts the number of matches that are found for *utterance* for each query (MEQ, NMQ, MLQ, RWQ) derived from  *mwe*, yielding a 4-tuple of integers. 
- it compares the result with the results of a previous run. If there are no results from a previous run, it assumes a previous result of (0,0,0,0) .
- if the result is worse than the previous result, this is noted and reported in the report file. After all examples have been dealt with and reported about, it raises an *AssertionError* 
- if the results for each (mwe, utterance pair) are equally good or better than the previous results, the module terminates normally.
- It also compares the scores with the GOLD scores, and reports about it (in the report file).
- It currently does not do anything with the MAX scores, so this could be an extension.
- It generates a report in the file *regressionreport.txt* in the folder *regressiondata/report*
- It generates a file *todo.txt* which specifies for each query which (mwe, utterance) pairs do not score equal to the GOLD score
- It stores the results of the previous run (if there was one) in the file *mweregressionset_previous.json* in the folder *regressiondata/auxdata*, and the results of the current run in the file *regressionset.json* in the same folder.

## Data

The data that the regressiontest runs on is stored in the file *regressionexamples.xlsx* 
in the folder *regresssiondata/data*. This is a MS Excel file because that makes editing this file easy.
It is in essence a simple table with the following columns:

- MWE: the canonical for of a MWE. If a cell is empty, its value s assumed to be identical to the same cell in the
preceding row.
- Uttterance: an utterance 
- GOLD for a gold reference (see explanation below)
- MAX for a MAX reference (see explanation below)

### GOLD reference
The GOLD reference consists of a string of the following form:
- empty string. This is interpreted as 'X1111', the most common GOLD reference value
- a string of the form X\d\d\d\d. Each digit represents the number of matches found for a query, in the order MEQ, NMQ, MLQ, RWQ. The preceding symbol *X*is there just because otherwise Excel would interpret the value as a number, Since most utterances contain maximally one occurrence of the MWE, 'X1111' is the most common GOLD value.

One can of course include utterances that are not an instance of the MWE (e.g. to check whether MEQ v. NMQ works well), and then one might have a GOLD reference such as *X0111*, which means that the MEQ should not yield  a match but all other queries should yield a single match) 

The strings representing score are turned into 4-tuples of integers inside the program.

> In the current implementation the digits are restricted to the values '0' and '1', but that is actually incorrect

### MAX reference

We know that we can not always obtain the score of the GOLD value due to circumstances outside of the control of MWE-Finder.For example, because Alpino has limitations, does not know certain words, etc. Thus, it makes no sense to try to improve MWE-Finder for such cases. The MAX reference value is intended to represent that, but currently nothing is done with it.

>Example: Alpino does not know the word *velen* as a verb. MWE-Finder can therefore never have a match for MEQ and NMQ for the MWE *iets zal iemand ^niet kunnen velen*. The MAX reference score should reflect this and thus have a value of 'X0011'. The *todo.txt* should actually be based on a comparison between the results and the MAX score rather than between the result and the GOLD score.

>However, currently nothing is dome yet with the MAX score 

## Comparing scores

Comparingscores is done by the function *check* in *mweregressiontest.py*

The scores are  4-tuples of integers. Score A=(a1, a2,a3,a4) is better than score B=(b1,b2,b3,b4) if all ai >= bi and at least for one ai, bi pair ai > bi holds. If for all ai, bi pairs ai==bi holds, the scores are equal. In all other cases score A is worse than score B.

If the current score is better than the previous score, this will be mentioned in the report. If the current score is worse than the previous score, a difference is reported. Equal scoresa are not reported

> We should take the GOLD value into account here as well. For example score A=(1,1,1,1) is better than previous score B=(0,1,1,1) but it is actually worse if the GOLD value G=(0,1,1,1). This still has to be imoplemented

# Efficiency
Computers are slow, but we want them to do many things and as fast as possible. So we must assist the computer somewhat.

In order to check whether there is a match in an utterance with a MWE both the utterance and the MWE must be parsed by Alpino. This is a slow process, and if we do nothing special this has to be done each time the regressiontest is run. In order to avoid this, the program stores parses of utterances and MWEs. When it has to parse an utterance or a MWE, it first checks whether a parse for this utterance or MWE has been made earlier, and if so, it just fetches that result. If not, it has to parse the utterance, but it stores the result so that it does not have to reparse t a next time.

The parses for utterances and MWEs are stored in the file *regressiontreebank.xml* in the folder *regressiondata/auxdata*. This file is updated each time a new utteranc or MWE has to be parsed.The previous version is stored in the file *regressiontreebank_previous.xml* in the same folder 