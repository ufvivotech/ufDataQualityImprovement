#!/user/bin/python
"""
    read-bibtex.py -- read bibtex, list and tabulate papers, journals,
    publishers
    
    Version 1.0 MC 6/30/2012
    --  Read a fixed bibtex file (see fix-bibtex.py) and tabulate
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"

from pybtex.database.input import bibtex
import sys

def print_publication_list(bib_sorted):
    """
    Given a sorted list of bib entries from the pybtex parser,
    create a tabular output of year, author, type, title, issn, doi
    Not every object has a doi, so try to get the doi and if there is none, show "NA"
    """
    print ""
    print "Publication List.  Row, ISI Number, Year, Author, Type, Title, ISSN, DOI"
    print ""
    i = 0
    for key, value in bib_sorted:
        i = i+1
        author_count = len(value.fields['author'].split(' and '))      
        try:
            doi = value.fields['doi']
        except:
            doi = 'NA'
	try:
	    issn = value.fields['issn']
	except:
	    issn = 'NA'
        print "{0:>3}".format(i),value.fields['year'],"{0:30}".format(value.fields['title'][0:30]),"({0:>2})".format(author_count),\
            "{0:20}".format(value.fields['author'][0:20]),"{0:10}".format(value.fields['type'][0:10]),issn,doi

def print_publication_types(bib_sorted):
    """
    Given bib entries read by the pybtex parser, create a frequency table of
    publications counted by the bibtex type, not to be confused with any field
    in the bibtex called type.  The bibtex type is the word after the @ in the
    entry and is defined in the bibtex spec -- @article, @incollection, etc.
    """
    print """
    Publication count by bibtex type
    """
    types = {}
    for key,value in bib_sorted:
        type = value.type
        types[type] = types.get(type,0) + 1
    i = 0    
    for type in types:
        i = i + 1
        print i,type,types[type]

def print_publication_counts(bib_sorted,count='type'):
    """
    Given bib entries read by the pybtex parser, create a frequency table of
    publications counted by the property named in the count parameter. Possible
    values are 'type', 'year', 'journal', 'issn', 'doi', 'author'
    """
    print ""
    print "Publication count by",count,".  Row,",count,", freq"
    print ""
    types = {}
    for key,value in bib_sorted:
        try:
            type = value.fields[count]
        except:
            type = "Not Found"
        types[type] = types.get(type,0) + 1
    i = 0    
    for type in types:
        i = i + 1
        print i,type,types[type]

def print_publication_venues(bibo_sorted):
    """
    Given bib entries from the pybtex parser, create a frequency table of
    publications by publication venue, each with its issn and mixed case name
    """
    print ""
    print "Publication venue count by issn.  Row, ISSN, Count, Journal Name"
    print ""
    issns = {}
    names = {}
    for key,value in bib_sorted:
	try:
	    issn = value.fields['issn']
	except:
	    issn = 'NA'
        issns[issn] = issns.get(issn,0) + 1
        try:
            names[issn] = value.fields['journal']
        except:
            names[issn] = 'Unknown'
    i = 0    
    for issn in issns:
        i = i + 1
        print i,issn,issns[issn],names[issn].title()

def print_publication_author_counts(bib_sorted,max_authors=50):
    """
    Given bib entries from the pybtex parser, create a frequency table of
    publications by the number of authors on the publication
    """
    print ""
    print "Publication author count.  Row, Number of Authors, Count of publications"
    print ""
    papers = {}
    for key,value in bib_sorted:
        author_count = len(value.fields['author'].split(' and '))
        if author_count > max_authors:
            title = value.fields['title']
            print "WARNING:",title,"has",author_count,"authors.  This is more than the maximum of",max_authors
        papers[author_count] = papers.get(author_count,0) + 1
    i = 0    
    for author_count in sorted(papers.keys()):
        i = i + 1
        print i,author_count,papers[author_count]

def print_authors(bib_sorted,trim=0):
    """
    Given bib entries from the pybtex parser, return a list of authors.  For each
    author in the list, return name, and list of ISI numbers of authored pubs.
    if the author count is larger than trim value, do not include that paper in the output.
    """
    authors={}
    for key,value in bib_sorted:
        author_list = value.fields['author'].split(' and ')
        if len(author_list) <= trim :
            for author in author_list :
                try:
                    authors[author].append(key)
                except:
                    authors[author] = [key] 
    i = 0
    for author in sorted(authors.keys()):
        i = i+1
        print i,author,authors[author]
#
#  read the file
#
parser = bibtex.Parser()
file_name = sys.argv[1]
bib_data = parser.parse_file(file_name)
print "The file",file_name,"has",len(bib_data.entries.keys()),"publications"

#
#  sort by title
#
bib_sorted = sorted(bib_data.entries.items(), key = lambda x: x[1].fields['title'])

print_authors(bib_data.entries.items(),trim=50)
print_publication_list(bib_sorted)
print_publication_types(bib_sorted)
print_publication_counts(bib_sorted)
print_publication_counts(bib_sorted,'year')
print_publication_author_counts(bib_sorted)
print_publication_counts(bib_sorted,'publisher')
print_publication_venues(bib_sorted)


    
    

