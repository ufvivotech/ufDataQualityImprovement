
#
#  Test date compare
#
import dateutil.parser
import csv

csvReader = csv.reader(open('sparqlquery.txt','r'))
for row in csvReader:
    [uri,date_text] = row
    try:
        date = dateutil.parser.parse(date_text)
    except:
        date = None
    if date == None:
        print uri,"None"
