# script to download html files off of the sos voterguide and extract relevant
# text.

from os import mkdir, rename, listdir
from os.path import isdir, join, isfile, dirname, realpath, exists, expanduser
from time import sleep
from sklearn.datasets.base import Bunch
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from wget import download
from tabulate import tabulate
from numpy import int32

from parser import SOSParser

sos_url = "http://voterguide.sos.ca.gov/en/propositions"
propositions = range(51, 68)

pages = ["title-summary.htm", "analysis.htm", "arguments-rebuttals.htm"]

# propositions for which I have opinions. 0 is against, 1 is for
opinions = {56: 0, 60: 0, 62: 1, 64: 1}

current_directory = dirname(realpath(__file__))

raw_html_folder = 'data/raw_html'

if not isdir(raw_html_folder):
    mkdir(raw_html_folder)
# download the text from the sos voterguide
for prop in propositions:
    for page in pages:
        url = join(sos_url, str(prop), page)
        html_page = join(raw_html_folder, str(prop)+"_"+page)
        if not isfile(html_page):
            print(url, html_page)
            filename = download(url)
            sleep(1)
            rename(join(current_directory, filename),
                   join(current_directory, html_page))

# strip the extraneous html. I started writing this, but there's hardly any
# structure, and I think the bag of words analysis will handle the common
# elements. Also, perhaps there's some subtle way in the way the propositions
# are presented that can be mined.
prop_texts_known = Bunch()
prop_texts_known.data = []
prop_texts_known.target_names = ['against', 'for']
prop_texts_known.target = []
prop_texts_unknown = Bunch()
prop_texts_unknown.data = []
prop_texts_unknown.target_names = ['against', 'for']
for file in listdir(raw_html_folder):
    prop_number = int(file.split("_")[0])
    html_page = join(raw_html_folder, file)

    if prop_number in opinions.keys():
        prop_texts_known.data.append(open(html_page, "r").read(-1))
        prop_texts_known.target.append(opinions[prop_number])
    else:
        prop_texts_unknown.data.append(open(html_page, "r").read(-1))
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(prop_texts_known.data)
clf = MultinomialNB().fit(X_train_counts, prop_texts_known.target)

# I think we don't need to transform to frequency, since a lot of these
# documents are the same length
X_new_counts = count_vect.transform(prop_texts_unknown.data)
predicted = clf.predict(X_new_counts)
_sos_parser = SOSParser()

predictions = {}

for doc, category in zip(prop_texts_unknown.data, predicted):
    _sos_parser.clear()
    _sos_parser.feed(doc)
    if _sos_parser.title[0] not in predictions.keys():
        predictions[_sos_parser.title[0]] = {}
    predictions[_sos_parser.title[0]][_sos_parser.title[1]] = category
    predictions[_sos_parser.title[0]]['Summary'] = _sos_parser.summary


results_table = []
results_table_headers = ["Proposition", "Summary"]+list(predictions[list(predictions.keys())[0]].keys())+["Total"]
for proposition in predictions:
    row = [proposition, predictions[proposition]['Summary']]
    total = 0
    for prediction in sorted(predictions[proposition]):
        if type(predictions[proposition][prediction]) is int32:
            total += predictions[proposition][prediction]
            row.append(predictions[proposition][prediction])
    row.append(total)
    results_table.append(row)

opinions_table = []
opinions_table_headers = ["Proposition", "Summary", "Opinion"]
for opinion in opinions:
    row = [opinion]
    _sos_parser.clear()
    row.append(_sos.summary)
    row.append()

# if my blog exists on this computer, insert the results into the corresponding
# post
_post_filename = expanduser('~/ruby_projects/CatherineH.github.io/_drafts/2016-10-01-voting-advice-from-a-naive-bayes-classifier.md')
if exists(_post_filename):
    text = open(_post_filename, "r").read(-1)
    text = text.replace("$RESULT_TABLE$",
                        tabulate(results_table, results_table_headers, tablefmt="html"))

    _output_filename = _post_filename.replace('_drafts', '_posts')
    open(_output_filename, "w").write(text)


print(len(clf.feature_log_prob_))
print(len(clf.feature_count_))
