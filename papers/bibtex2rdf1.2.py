#!/user/bin/env/python
"""
    bibtex2rdf

    Read a bibtex file and make VIVO RDF

    The following objects will be made as needed:
      -- publisher
      -- journal
      -- information resource
      -- timestamp for the information resource
      -- people
      -- authorships

    The resulting RDF file can then be read into VIVO

    Version 1.0 MC 2012-08-16
      -- Using VIVO as the current state, process a bibtex file, checking VIVO
         for the presence of paper, authors, journal and publisher.  Create missing
         entities as needed.  Never delete or change anything.  Only add new items.
         Don't handle papers with more than 50 authors.

    Version 1.1 MC 2012-09-02
      -- Corporate authorship.  bibtex2rdf now handles author lists of any length.
         A parameter, MAX_AUTHORS controls how many authors appear in an authorship
         before the rest are placed in a corporate authorship.
      -- New report for disambiguation lists the paper and all the choices for an
         author that needs to be disambiguated
      -- Cosmetic improvements to paper titles -- roman numerals, 's, escaped chars &,<,>
      -- Fix bug in lst files that caused author lists to be out of order
      -- Fix bug in which bibtex with no journal field attempted to create publisher/journal
         cross links
      -- Version of the software now in the name of the file

      Version 1.2 MC 2012-11-25
      -- Use UF Entity rather than UFID as the base for the dictionaries to get
         more people into the dictionaries and cut down on stub creation
      -- use key_string on people names to improve matches on mixed case names,
         names with space, punctuation and unicode
      -- show the current time on the console at the start of each major step in the work
      -- move make dictionary and find functions to vivotools

    Proposed future features
      -- add PMID, PMCID and Grants cited to papers that appear in PubMed
      -- Move reusable code to vivotools
      -- Improve DateTimeValue accuracy.  Currently all publications are entered as
          yearMonth precision.  Sometimes we have more information, sometimes we
          have less.  We should use the information as presented by the publisher,
          not overstate (yearMonth when there is only year) and not understate (yearMonth
          when we know the day).
      -- optionally send a notification email to each author congratulating them on their paper,
         asking them confirm authorship (and potentially confirm use of CTSI resources)
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"

import sys
from datetime import datetime,date
from pybtex.database.input import bibtex
import tempita
import vivotools

MAX_AUTHORS = 50

publisher_report = {}
journal_report = {}
title_report = {}
author_report = {}
disambiguation_report = {}

dictionaries = []
journal_dictionary = {}
publisher_dictionary = {}
title_dictionary = {}

def make_pub_datetime(value):
    try:
        year = int(value.fields['year'])
    except:
        year = 2012
    try:
        m = value.fields['month'].upper()
    except:
        m = 'JAN'
    month = 1
    if m.startswith('JAN'):
        month = 1
    elif m.startswith('FEB'):
        month = 2
    elif m.startswith('MAR'):
        month = 3
    elif m.startswith('APR'):
        month = 4
    elif m.startswith('MAY'):
        month = 5
    elif m.startswith('JUN'):
        month = 6
    elif m.startswith('JUL'):
        month = 7
    elif m.startswith('AUG'):
        month = 8
    elif m.startswith('SEP'):
        month = 9
    elif m.startswith('OCT'):
        month = 10
    elif m.startswith('NOV'):
        month = 11
    elif m.startswith('DEC'):
        month = 12
    elif m.startswith('WIN'):
        month = 1
    elif m.startswith('SPR'):
        month = 4
    elif m.startswith('SUM'):
        month = 7
    elif m.startswith('FAL'):
        month = 10
    else:
        month = 1
    dt = date(year,month,1)
    document['date'] = {'month':str(month),'day':'1','year':str(year)}
    return dt.isoformat()

def make_harvest_datetime():
    dt = datetime.now()
    return dt.isoformat()

def make_datetime_rdf(value,title):
    """
    Given a bibtex publication value, create the RDF for a datetime object expressing
    the date of publication
    """
    datetime_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#DateTimeValue"/>
        <core:dateTimePrecision rdf:resource="http://vivoweb.org/ontology/core#yearMonthPrecision"/>
        <core:dateTime>{{pub_datetime}}</core:dateTime>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    uri = vivotools.get_vivo_uri()
    pub_datetime = make_pub_datetime(value)
    harvest_datetime = make_harvest_datetime()
    rdf = "<!-- Timestamp RDF for " + title + "-->" 
    rdf = rdf + datetime_template.substitute(uri=uri,pub_datetime=pub_datetime,harvest_datetime=harvest_datetime)
    return [rdf,uri]

def abbrev_to_words(s):
    """
    Text is often abbreviated in the names of publishers and journals.  This
    little helper function takes a string s and returns an improved version
    with abbreviations replaced by words.  Handle cosmetic improvements.
    Replace special characters with escape versions for RDF
    """
    t = s.replace("Dept ","Department ")
    t = t.replace("Soc ","Society ")
    t = t.replace("Med ","Medical ")
    t = t.replace("Natl ","National ")
    t = t.replace("Univ ","University ")
    t = t.replace("Publ ","Publishers " )
    t = t.replace("Am ","American ")
    t = t.replace("Assoc ","Association ")
    t = t.replace("Acad ","Academy ")
    t = t.replace("Of ","of ")
    t = t.replace("In ","in ")
    t = t.replace("As ","as ")
    t = t.replace("Ieee ","IEEE ")
    t = t.replace("A ","a ")
    t = t.replace("For ","for ")
    t = t.replace("And ","and ")
    t = t.replace("The ","the ")
    t = t.replace("Inst ","Institute ")
    t = t.replace("Sci ","Science ")
    t = t.replace("Amer ","American ")
    t = t.replace("'S ","'s ")
    t = t.replace("Ii ","II ")
    t = t.replace("Iii ","III ")
    t = t.replace("Iv ","IV ")            
    t = t.replace("\&","&amp;")
    t = t.replace("<","&lt;")
    t = t.replace(">","&gt;")
    # Returned value will always start with an upper case letter
    t = t[0].upper() + t[1:]
    return t

def make_journal_uri(value):
    """
    Given a bibtex publication value, return the journal uri from VIVO. Three cases:  1) There is no
    journal name in the bibtex.  We return an empty URI.  2) We find the journal in VIVO, we return the
    URI of the journal in VIVO. 3) We don't find the journal, so we return a new URI.
    """
    #
    #  get the name of the journal from the data.  Fix it up a bit before trying to find
    #
    try:
        journal_name = value.fields['journal'].title()+ " "
        journal_name = abbrev_to_words(journal_name)
        journal_name = journal_name[0:-1]
        issn = value.fields['issn']
        document['journal'] = journal_name
        document['issn'] = issn
    except:
        journal_uri = ""
        journal_name = "No Journal"
        create = False
        return [create,journal_name,journal_uri]
    #
    #  now we are ready to look for the journal -- first in the journal_report (journals we have already
    #  processed in this run, and if not found there, then in the journal dictionary created from VIVO
    #
    if journal_name in journal_report:
        create = False
        journal_uri = journal_report[journal_name][1]
        journal_report[journal_name][2] = journal_report[journal_name][2] + 1
    else:
        [found,uri] = vivotools.find_journal(issn,journal_dictionary)
        if not found:
            # Will need to create
            create = True
            journal_uri = vivotools.get_vivo_uri()
        else:
            # Found in VIVO
            create = False
            journal_uri = uri
        journal_report[journal_name] = [create,journal_uri,1]

    return [create,journal_name,journal_uri]

def make_publisher_rdf(value):
    """
    Given a bibtex publication value, create the RDF for a publisher
    """
    publisher_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <rdfs:label>{{publisher}}</rdfs:label>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Publisher"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Organization"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    #
    #  get the name of the publisher from the data.  Fix it up a bit before trying to find
    #
    try:
        publisher = value.fields['publisher'].title()+ " "
        publisher = abbrev_to_words(publisher)
        publisher = publisher[0:-1]
    except:
        uri=""
        publisher = "No publisher"
        create = False
        rdf = "\n<!-- No publisher found for this publication. No RDF necessary -->"
        return [create,publisher,uri,rdf]
    #
    #  now we are ready to look for the publisher
    #
    if publisher in publisher_report:
        create = False
        uri = publisher_report[publisher][1]
        publisher_report[publisher][2] = publisher_report[publisher][2] + 1
        rdf = "\n<!-- " + publisher + " found at uri to be created " + uri + "  No RDF necessary -->"
    else:    
        [found,uri] = vivotools.find_publisher(publisher,publisher_dictionary)
        if not found:
            # Publisher not found.  We need to add one.
            create = True
            uri = vivotools.get_vivo_uri()
            harvest_datetime = make_harvest_datetime()
            rdf = "\n<!-- Publisher RDF for " + publisher + " -->"
            rdf = rdf + publisher_template.substitute(uri=uri,publisher=publisher,
                                                      harvest_datetime=harvest_datetime)
            publisher_report[publisher] = [create,uri,1]
        else:
            # Publisher found.  return the uri of the publisher.
            create = False
            rdf = "\n<!-- " + publisher + " found in VIVO at uri " + uri + "  No RDF necessary -->"
            publisher_report[publisher] = [create,uri,1]
    return [create,publisher,uri,rdf]

def make_journal_rdf(value,journal_create,journal_name,journal_uri):
    """
    Given a bibtex publication value, create the RDF for the journal of the
    journal of the publication if the journal is not already in VIVO
    """
    journal_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{journal_uri}}">
        <rdfs:label>{{journal_name}}</rdfs:label>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Periodical"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#InformationResource"/>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Collection"/>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Journal"/>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        {{if len(issn) > 0 :}}
            <bibo:issn>{{issn}}</bibo:issn>
        {{endif}}
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    if not journal_create:
        rdf = "\n<!-- " + journal_name + " found at uri " + journal_uri + "  No RDF necessary -->"
    else:
        # Not found. get the issn of the journal 
        #
        try:
            issn = value.fields['issn']
        except:
            issn = ""
        harvest_datetime = make_harvest_datetime()
        rdf = "\n<!-- Journal RDF for " + journal_name + " -->"
        rdf = rdf + journal_template.substitute(journal_uri=journal_uri,journal_name=journal_name,issn=issn,
                                                harvest_datetime=harvest_datetime)  
    return [rdf,journal_uri]

def make_publisher_journal_rdf(publisher_uri,journal_uri):
    """
    Create the assertions PublisherOf and PublishedBy between a publisher and a journal
    """
    publisher_journal_template = tempita.Template("""
    <rdf:Description rdf:about="{{publisher_uri}}">
        <core:publisherOf  rdf:resource="{{journal_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    <rdf:Description rdf:about="{{journal_uri}}">
        <core:publisher rdf:resource="{{publisher_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    rdf = ""
    harvest_datetime = make_harvest_datetime()
    rdf = rdf + "\n<!-- Publisher/Journal assertions for " + publisher + " and " + journal_name + " -->"
    rdf = rdf + publisher_journal_template.substitute(publisher_uri=publisher_uri,
                                                      journal_uri=journal_uri,harvest_datetime=harvest_datetime)
    return rdf    

def name_parts(author):
    """
    Given the name of an author, break it in to first, middle, last and assign a
    case number to the type of name information we have
    
    Case 0 last name only
    Case 1 last name, first initial
    Case 2 last name, first name
    Case 3 last name, first initial, middle initial
    Case 4 last name, first initial, middle name
    Case 5 last name, first name, middle initial
    Case 6 last name, first name, middle name
    """
    count = 0
    name_cut = author.split(',')
    last = name_cut[0]
    if len(name_cut) > 1:
        rest = name_cut[1]
        rest = rest.replace(',','')
        rest = rest.replace('.','')
        name_list = rest.split()
        name_list.insert(0,last)
    else:
        name_list = [last]
    if len(name_list) >= 3:
        last = name_list[0]
        first = name_list[1]
        middle = name_list[2]
        if len(first) == 1 and len(middle) == 1:
            case = 3
        if len(first) == 1 and len(middle) > 1:
            case = 4
        if len(first) > 1 and len(middle) == 1:
            case = 5
        if len(first) > 1 and len(middle) > 1:
            case = 6
    elif len(name_list) == 2:
        last = name_list[0]
        first = name_list[1]
        middle = ""
        if len(first) == 1:
            case = 1
        if len(first) > 1:
            case = 2
    else:
        last = name_list[0]
        first = ""
        middle = ""
        case = 0
    result = [last,first,middle,case]
    return result

def update_dict(dict,key,val):
    """
    return a list of the results of dict[key] with val appended
    """
    try:
        l = dict[key]
    except:
        l = []
    l.append(val)
    return l

def make_people_dictionaries(debug=False):
    """
    Get all the UFEntity people from VIVO and build seven dictionaries -- put
    each person in as many dictionaries as they can be (between 1 and 7) based
    on the presence of their name parts in VIVO.  A last name part is required
    to be in the SPARQL result set.
    """
    query = tempita.Template("""
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type foaf:Person .
?x foaf:lastName ?lname .
?x rdf:type ufVivo:UFEntity .
OPTIONAL {?x core:middleName ?mname .}
OPTIONAL {?x foaf:firstName ?fname .}
}""")
    query = query.substitute()
    result = vivotools.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    # make the dictionaries
    #
    # Case 0 last name only
    # Case 1 last name, first initial
    # Case 2 last name, first name
    # Case 3 last name, first initial, middle initial
    # Case 4 last name, first initial, middle name
    # Case 5 last name, first name, middle initial
    # Case 6 last name, first name, middle name
    #
    case0_dict = {}
    case1_dict = {}
    case2_dict = {}
    case3_dict = {}
    case4_dict = {}
    case5_dict = {}
    case6_dict = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        lname = b['lname']['value']
        uri = b['x']['value']
        try:
            fname = b['fname']['value']
        except:
            fname = ""
        try:
            mname = b['mname']['value']
        except:
            mname = ""
        if len(fname) > 0 and len(mname) > 0:
            #
            # seven cases here
            #
            k0 = vivotools.key_string(lname)
            k1 = vivotools.key_string(lname + ':' + fname[0])
            k2 = vivotools.key_string(lname + ':' + fname)
            k3 = vivotools.key_string(lname + ':' + fname[0] +':' + mname[0])
            k4 = vivotools.key_string(lname + ':' + fname[0] + ':' + mname)
            k5 = vivotools.key_string(lname + ':' + fname + ':' + mname[0])
            k6 = vivotools.key_string(lname + ':' + fname + ':' + mname)
            case0_dict[k0]= update_dict(case0_dict,k0,uri)
            case1_dict[k1]= update_dict(case1_dict,k1,uri)
            case2_dict[k2]= update_dict(case2_dict,k2,uri)
            case3_dict[k3]= update_dict(case3_dict,k3,uri)
            case4_dict[k4]= update_dict(case4_dict,k4,uri)
            case5_dict[k5]= update_dict(case5_dict,k5,uri)
            case6_dict[k6]= update_dict(case6_dict,k6,uri)
        elif len(fname) > 0 and len(mname) == 0:
            #
            # three cases here
            #
            k0 = vivotools.key_string(lname)
            k1 = vivotools.key_string(lname + ':' + fname[0])
            k2 = vivotools.key_string(lname + ':' + fname)
            case0_dict[k0]= update_dict(case0_dict,k0,uri)
            case1_dict[k1]= update_dict(case1_dict,k1,uri)
            case2_dict[k2]= update_dict(case2_dict,k2,uri)
        elif len(fname) == 0 and len(mname) == 0:
            #
            # one case here
            #
            k0 = vivotools.key_string(lname)
            case0_dict[k0]= update_dict(case0_dict,k0,uri)
        i = i + 1
    return [case0_dict,case1_dict,case2_dict,case3_dict,case4_dict,case5_dict,case6_dict]

def find_author(author):
    """
    Given an author name in the form last, first middle with middle and/or first eitehr blank or
    single character with or with periods, find the name in the appropriate case dictionary.  The
    case dictionaries are prepared using make_people_dictionaries
    """
    [lname,fname,mname,case] = name_parts(author)
    [case0_dict,case1_dict,case2_dict,case3_dict,case4_dict,case5_dict,case6_dict] = dictionaries
    if case == 0:
        k0 = vivotools.key_string(lname)
        result = case0_dict.get(k0,[])
    elif case == 1:
        k1 = vivotools.key_string(lname + ':' + fname[0])
        result = case1_dict.get(k1,[])
    elif case == 2:
        k2 = vivotools.key_string(lname + ':' + fname)
        result = case2_dict.get(k2,[])
    elif case == 3:
        k3 = vivotools.key_string(lname + ':' + fname[0] +':' + mname[0])
        result = case3_dict.get(k3,[])
    elif case == 4:
        k4 = vivotools.key_string(lname + ':' + fname[0] + ':' + mname)
        result = case4_dict.get(k4,[])
    elif case == 5:
        k5 = vivotools.key_string(lname + ':' + fname + ':' + mname[0])
        result = case5_dict.get(k5,[])
    else:
        k6 = vivotools.key_string(lname + ':' + fname + ':' + mname)
        result = case6_dict.get(k6,[])
    return result

def uf_affiliation(affiliation):
    """
    Given an affiliation string, return true if the affiliation is for UF, False if not
    """
    #                
    #  Is this list of authors a UF list?
    #
    k1 = affiliation.find("Gainesville")
    k2 = affiliation.find("Univ Fl")
    k3 = affiliation.find("UNIV FL")
    k4 = affiliation.find("UF Col Med")
    k5 = affiliation.find("UF Coll Med")
    isUF_affiliation = k1>=0 or k2>=0 or k3>=0 or k4 >= 0 or k5 >= 0
    return isUF_affiliation

def make_authors(value,debug=False):
    """
    Given a bibtex publication value, return a dictionary, one entry per author.  The key is the
    author name, the value is a list = order, corresponding author (t/f), UF author (t/f), corporate
    author (t/f), last, first, middle and case.  Case is an integer from 0 to 6 indicating how much of a
    name we actually have.  See name_parts for description.

    To do:  Add code to improve parsing of similar names.  The current code can be confused if
    author names are subsets, such as Childs, A. and Childs, A. Baker  
    """
    authors={}
    try:
        author_names = value.fields['author'].split(' and ')
    except:
        author_names = []
    try:    
        affiliation_text = value.fields['affiliation']
    except:
        affiliation_text = ""
    if len(author_names) > MAX_AUTHORS:
        other_authors = ";".join(author_names[MAX_AUTHORS:]) # create a string of the other authors
        author_names = author_names[0:MAX_AUTHORS]         # truncate the list of authors
        author_names.append(other_authors)                   # Add corporate author name string
    #
    #  prepare the affiliation_list
    #       
    order = 0
    for author in author_names:
        order = order + 1
        if order > MAX_AUTHORS:
            authors[author] = [order,False,False,True,author,"","",None]
            break
        authors[author] = [order,False,False,False]+name_parts(author)
        k = affiliation_text.find(author)
        auth = author
        auth = author.replace('.','+')
        if auth == author:
            continue # nothing to do, there are no periods to replace for this author
        else:
            while k >=0:
                affiliation_text = affiliation_text.replace(author,"/"+auth+"/",1)
                k = affiliation_text.find(author)
    affiliation_list = affiliation_text.split('.')
    affiliation_list = affiliation_list[0:-1]
    #
    #  find the corresponding author. Corresponding authors are not listed by full name.
    #  Typically they are listed by last name, first initial, but other variants are used.
    #  Here we match only on the last name, which could result in an error if two authors
    #  have the same last name and the first one is not the corresponding author
    #
    for affiliation in affiliation_list :
        for author in author_names:
            last_name = authors[author][4] 
            if affiliation.find(last_name) >= 0 and affiliation.find('(Reprint Author)') >= 0 :
                authors[author][1] = True
                #
                # while we are here, check to see if this is a UF affiliation.  If it is,
                # mark the found corresponding author as a UF author.  This handles a nasty
                # edge case where the corresponding author might have a UF affiliation in
                # the corresponding author affiliation, but a non-UF affiliation in the
                # regular affiliation fields.
                #
                if uf_affiliation(affiliation):
                    authors[author][2] = True
                break
    #
    #  find the UF authors.  For each affiliation, look to see if it is a UF affiliation.
    #  if it is, all authors found in it are UF authors.  If not, all authors are not
    #  UF authors.  If one person is found in two affiliations and is a UF author in either
    #  one, the the author is a UF author.
    #
    # if all the affiliations are UF affiliations, then all the authors are UF authors
    #
    count_uf_affiliations = 0
    for a in affiliation_list:
        if uf_affiliation(a):
            count_uf_affiliations = count_uf_affiliations + 1
    if len(affiliation_list) == count_uf_affiliations:
        #
        # all affiliations are UF, so all authors are UF
        #
        for author in author_names:
           authors[author][2] = True
    else:
        #
        # Not all the affiliations are UF, so we need to check each one
        #
        for a in affiliation_list :
            affiliation = a.replace('+','.')
            if uf_affiliation(affiliation):  # if UF, continue, otherwise skip the rest
                if len(author_names) == 1:
                    authors[author_names[0]][2] = True # Handle single UF author papers
                else:
                    for author in author_names:
                        if debug:
                            print "...Looking for>"+author+"< in UF affiliation>"+affiliation+"<"
                        if affiliation.find(author) >= 0 :
                            authors[author][2] = True
    return authors

def count_uf_authors(authors,debug=False):
    """
    Given an author structure from make_authors, return the count of UF authors
    """
    count = 0
    for author,value in authors.items():
        if value[2]:
            count = count + 1
    if debug:
        print "UF author count is ",count
    return count

def update_author_report(authors,title):
    """
    Given an authors structure, and the title of the paper for the authors, update the author_report for each author
    """
    #
    # accumulate all the authors in a structure for reporting
    #
    for author,value in authors.items():
        if author in author_report:
            result = author_report[author]
            result[len(result.keys())+1] = value
            author_report[author] = result
        else:
            author_report[author] = {1:value}
    return
    
def make_author_rdf(value,title):
    """
    Given a bibtex publication value, and the improved value of the publication title,
    create the RDF for the authors
    of the publication.  Some authors may need to be created, while others
    may be found in VIVO.

    For each author:
      Is author UF?
      Yes:
        How many authors at UF have this name?
        0:  Add the author, add to notify list
        1:  Get the URI for inclusion in the authorship
        2:  Punt the whole publication to the manual disambiguation list
      No:
        Create a new stub for the author (corporate or single).  Return the URI for authorship.
    If no UF authors, punt the whole publication to the error list
    Otherwise produce RDF for authors to be added
    Return the URIs of all authors (found or added)
    """
    author_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <rdfs:label>{{author_name}}</rdfs:label>
        {{if len(first) > 0:}}
            <foaf:firstName>{{first}}</foaf:firstName>
        {{endif}}
        {{if len(middle)>0:}}
            <core:middleName>{{middle}}</core:middleName>
        {{endif}}
        <foaf:lastName>{{last}}</foaf:lastName>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Person"/>
        {{if isUF:}}
            <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/UFEntity"/>
        {{endif}}
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    corporate_author_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <rdfs:label>{{group_name}}</rdfs:label>
        <core:overview>{{author_name}}</core:overview>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Group"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    rdf = ""
    authors = make_authors(value)
    for author,value in authors.items():
        isUF = value[2]
        isCorporate = value[3]
        if isUF:
            if author in author_report:
                # UF author previously found in this Python Pubs run.  Use the URI previously assigned to this author
                author_uri = author_report[author][1][-1]
                action = "Found UF"
                rdf = rdf + "\n<!-- Previously found UF author " + author + " with uri " + author_uri + " -->"
            else:
                # Look for the author in VIVO
                result = find_author(author)
                # How many people did you find with this author name?
                count = len(result)
                if count == 0:
                    # create a new UF author, and notify
                    author_uri = vivotools.get_vivo_uri()
                    action = "Make UF "
                    harvest_datetime = make_harvest_datetime()
                    rdf = rdf + "\n<!-- UF author stub RDF for " + author + " at uri " + author_uri + " and notify -->"
                    rdf = rdf + author_template.substitute(isUF=isUF,author_uri=author_uri,author_name=author,
                        first=value[5],middle=value[6],last=value[4],harvest_datetime=harvest_datetime)
                elif count == 1:
                    # Bingo! Disambiguated UF author. Add URI
                    author_uri = result[0]
                    action = "Found UF"
                    rdf = rdf + "\n<!-- Found UF author " + author + " with uri " + author_uri + " -->"
                else:
                    # More than 1 UF author has this name.  Add to the disambiguation list
                    author_uri = ";".join(result)
                    action = "Disambig"
                    rdf = rdf + "\n<!-- " + str(count) + " UF people found with name " + author + " Disambiguation required -->"
        elif isCorporate:
            # Corporate author
            author_uri = vivotools.get_vivo_uri()
            action = "Corp Auth"
            group_name = title + " Authorship Group"
            harvest_datetime = make_harvest_datetime()
            rdf = rdf + "\n<!-- Corporate author stub RDF for " + author + " at uri " + author_uri + " -->"
            rdf = rdf + corporate_author_template.substitute(author_uri=author_uri,author_name=author,
                group_name=group_name,harvest_datetime=harvest_datetime) 
        else:
            # Non UF author -- create a stub
            author_uri = vivotools.get_vivo_uri()
            action = "non UF  "
            harvest_datetime = make_harvest_datetime()
            rdf = rdf + "\n<!-- Non-UF author stub RDF for " + author + " at uri " + author_uri + " -->"
            rdf = rdf + author_template.substitute(isUF=isUF,author_uri=author_uri,author_name=author,
                first=value[5],middle=value[6],last=value[4],harvest_datetime=harvest_datetime)
        #
        # For each author, regardless of the cases above, record whether this author needs to be created and
        # what URI refers to the author (a new URI if author will be created, otherwise an existing URI)
        #
        authors[author].append(action)
        authors[author].append(author_uri)
    return [rdf,authors]

def make_authorship_rdf(authors,publication_uri):
    """
    Given the authors structure (see make_authors), and the uri of the publication,
    create the RDF for the authorships of the publication.  Authorships link authors
    to publications, supporting the many-to-many relationship between authors and
    publications.
    """
    authorship_template = tempita.Template("""
    <rdf:Description rdf:about="{{authorship_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Relationship"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Authorship"/>
        <core:linkedAuthor rdf:resource="{{author_uri}}"/>
        <core:linkedInformationResource rdf:resource="{{publication_uri}}"/>
        <core:authorRank>{{author_rank}}</core:authorRank>
        <core:isCorrespondingAuthor>{{corresponding_author}}</core:isCorrespondingAuthor>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    rdf = ""
    authorship_uris = {}
    for author,value in authors.items():
        author_rank = value[0]
        authorship_uri = vivotools.get_vivo_uri()
        authorship_uris[author] = authorship_uri
        author_uri = value[9]
        corresponding_author = value[1]
        harvest_datetime = make_harvest_datetime()
        rdf = rdf + "\n<!-- Authorship for " + author + "-->"
        rdf = rdf + authorship_template.substitute(authorship_uri=authorship_uri,
            author_uri=author_uri,publication_uri=publication_uri,author_rank=author_rank,
            corresponding_author = corresponding_author,harvest_datetime=harvest_datetime)
    return [rdf,authorship_uris]

def make_author_in_authorship_rdf(authors,authorship_uris):
    """
    Given the authorship_uris (see make_authorship_rdf), and the uri of the publication,
    create the RDF for the AuthorInAuthorship relationships of people to authorships.
    """
    author_in_authorship_template = tempita.Template("""
    <rdf:Description rdf:about="{{author_uri}}">
        <core:authorInAuthorship rdf:resource="{{authorship_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    rdf = ""
    for author,value in authors.items():
        author_uri = value[9]
        authorship_uri = authorship_uris[author]
        harvest_datetime = make_harvest_datetime()
        rdf = rdf + "\n<!-- AuthorshipInAuthorship for " + author + "-->"
        rdf = rdf + author_in_authorship_template.substitute(author_uri=author_uri,
            authorship_uri=authorship_uri,harvest_datetime=harvest_datetime)
    return rdf

def make_journal_publication_rdf(journal_uri,publication_uri):
    """
    Create the assertions publicationVenueFor and hasPublicationVenue between a journal and a publication
    """
    journal_publication_template = tempita.Template("""
    <rdf:Description rdf:about="{{journal_uri}}">
        <core:publicationVenueFor  rdf:resource="{{publication_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
    <rdf:Description rdf:about="{{publication_uri}}">
        <core:hasPublicationVenue rdf:resource="{{journal_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    rdf = ""
    harvest_datetime = make_harvest_datetime()
    rdf = rdf + "\n<!-- Journal/publication assertions for " + journal_name + " and " + title + " -->"
    rdf = rdf + journal_publication_template.substitute(publication_uri=publication_uri,
                                                      journal_uri=journal_uri,harvest_datetime=harvest_datetime)
    return rdf    

def map_bibtex_type(bibtex_type):
    map = {"article":"article",
           "book":"book",
           "booklet":"document",
           "conference":"conferencePaper",
           "inbook":"bookSection",
           "incollection":"documentPart",
           "inproceedings":"conferencePaper",
           "manual":"manual",
           "mastersthesis":"thesis",
           "misc":"document",
           "phdthesis":"thesis",
           "proceedings":"proceedings",
           "techreport":"report",
           "unpublished":"document"}
    return map.get(bibtex_type,"document")

def map_tr_types(tr_types_value,debug=False):
    """
    Given a string of TR type information, containing one or more types
    separated by semi-colons, map each one, returning a list of mapped
    values
    """
    map ={"bookreview":"review",
          "correction":"document",
          "editorial material":"editorialArticle",
          "review":"review",
          "article":"article",
          "proceedings paper":"conferencePaper",
          "newsitem":"article",
          "review":"review",
          "letter":"document",
          "theater review":"review"}
    tr_list = tr_types_value.split(";")
    if debug:
        print "tr_list",tr_list
    vivo_types = []
    for a in tr_list:
        b = a.strip()
        tr_type = b.lower()
        vivo_type = map.get(tr_type,"document")
        if len(vivo_types) == 0:
            vivo_types = [vivo_type]
        else:
            if vivo_type not in vivo_types:
                vivo_types.append(vivo_type)
    if debug:
        print vivo_types
    return vivo_types

def map_publication_types(value,debug=False):
    """
    Given a bibtex publication value, find the bibtex type and map to VIVO
    Then get the Thomson-Reuters types and map them to VIVO.
    Then merge the two lists and return all the types
    """
    #
    # Get and map the bibtex type
    #
    try:
        bibtex_type = value.type
    except:
        bibtex_type = "article"
    vivo_type = map_bibtex_type(bibtex_type)
    #
    # get and map the TR types
    #
    try:
        tr_types_value = value.fields['type']
    except:
        tr_types_value = ""
    vivo_types_from_tr = map_tr_types(tr_types_value,debug=debug)
    #
    #  combine the values and return
    #
    if vivo_type not in vivo_types_from_tr:
        vivo_types_from_tr.append(vivo_type)
    if debug:
        print "bibtex type",bibtex_type,"vivo type",vivo_type
        print "tr_types_value",tr_types_value,"vivo types",vivo_types_from_tr
        print vivo_types_from_tr
    return vivo_types_from_tr

def make_publication_rdf(value,title,publication_uri,datetime_uri,authorship_uris):
    """
    Given a bibtex publication value and previously created or found URIs, create the RDF
    for the publication itself. The publication will link to previously created or
    discovered objects, including the timestamp, the journal and the authorships
    """
    publication_template = tempita.Template("""
    <rdf:Description rdf:about="{{publication_uri}}">
        <rdfs:label>{{title}}</rdfs:label>
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#InformationResource"/>
        <rdf:type rdf:resource="http://purl.org/ontology/bibo/Document"/>
        {{for type in types:}}
            {{if type=="article"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Article"/>
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/AcademicArticle"/>
            {{endif}}
            {{if type=="book"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Book"/>
            {{endif}}
            {{if type=="document"}}
            {{endif}}
            {{if type=="conferencePaper"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Article"/>
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#ConferencePaper"/>
            {{endif}}
            {{if type=="bookSection"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/BookSection"/>
            {{endif}}
            {{if type=="documentPart"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/DocumentPart"/>
            {{endif}}
            {{if type=="manual"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Manual"/>
            {{endif}}
            {{if type=="thesis"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Thesis"/>
            {{endif}}
            {{if type=="proceedings"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Proceedings"/>
            {{endif}}
            {{if type=="report"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Report"/>
            {{endif}}
            {{if type=="review"}}
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#Review"/>
            {{endif}}
            {{if type=="editorialArticle"}}
                <rdf:type rdf:resource="http://purl.org/ontology/bibo/Article"/>
                <rdf:type rdf:resource="http://vivoweb.org/ontology/core#EditorialArticle"/>
            {{endif}}
        {{endfor}}
        {{if len(doi) > 0:}}
            <bibo:doi>{{doi}}</bibo:doi>
        {{endif}}
        {{if len(volume) > 0:}}
            <bibo:volume>{{volume}}</bibo:volume>
        {{endif}}
        {{if len(number) > 0:}}
            <bibo:number>{{number}}</bibo:number>
        {{endif}}
        {{if len(start) > 0:}}
            <bibo:pageStart>{{start}}</bibo:pageStart>
        {{endif}}
        {{if len(end) > 0:}}
            <bibo:pageEnd>{{end}}</bibo:pageEnd>
        {{endif}}
        {{for author,authorship_uri in authorship_uris:}}
            <core:informationResourceInAuthorship rdf:resource="{{authorship_uri}}"/>
        {{endfor}}
        <core:dateTimeValue rdf:resource="{{datetime_uri}}"/>
        <ufVivo:harvestedBy>Python Pubs version 1.1</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>
""")
    #
    # get publication attributes from the bibtex value.  In each case, use a try-except construct in
    # case the named attribute does not exist in the bibtex.  Not all publications have a doi, for
    # example
    #
    types = map_publication_types(value)
    try:
        doi = value.fields['doi']
        document['doi'] = doi
    except:
        doi = ""
    try:
        volume = value.fields['volume']
        document['volume'] = volume
    except:
        volume = ""
    try:
        number = value.fields['number']
        document['issue'] = issue
    except:
        number = ""
    #
    # Get the pages element from the bibtex.  If found, try to split it into start and end
    
    try:
        pages = value.fields['pages']
    except:
        pages = ""
    pages_list = pages.split('-')
    try:
        start = pages_list[0]
        document['page_start'] = start
    except:
        start = ""
    try:
        end = pages_list[1]
        document['page_end'] = end
    except:
        end = ""
    # write out the head, then one line for each authorship, then the tail
    rdf = "\n<!-- Publication RDF for " + title + "-->"
    harvest_datetime = make_harvest_datetime()
    rdf = rdf + publication_template.substitute(publication_uri=publication_uri,title=title,
        doi=doi,volume=volume,number=number,start=start,end=end,types=types,
        datetime_uri=datetime_uri,harvest_datetime=harvest_datetime,authorship_uris=authorship_uris.items())
    return rdf

rdf_header = """
<rdf:RDF
  xmlns:rdf    = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs   = "http://www.w3.org/2000/01/rdf-schema#"
  xmlns:foaf   = "http://xmlns.com/foaf/0.1/"
  xmlns:owl    = "http://www.w3.org/2002/07/owl#"
  xmlns:ufVivo = "http://vivo.ufl.edu/ontology/vivo-ufl/"
  xmlns:bibo   = "http://purl.org/ontology/bibo/"
  xmlns:core   = "http://vivoweb.org/ontology/core#">"""
rdf_footer = """
</rdf:RDF>"""

def make_document_authors(authors):
    """
    Given the structure returned by make_authors, return the structure needed by document
    """
    author_dict = {}
    for key,author in authors.items():
        author_dict["{0:>10}".format(author[0])] = {'first':author[5],'middle':author[6],'last':author[4]}
    return author_dict

def open_files(bibtex_file_name):
    """
    Give the name of the bibitex file to be used as input, generate the file names for
    rdf, rpt and lst.  Return the open file handles
    """
    base = bibtex_file_name[:bibtex_file_name.find('.')]
    rpt_file = open(base+'.rpt','w')
    lst_file = open(base+'.lst','w')
    rdf_file = open(base+'.rdf','w')
    return [rdf_file,rpt_file,lst_file]

def update_disambiguation_report(authors,publication_uri):
    """
    Given the authors structure and thte publication_uri, add to the report if any of the authors need to
    be disambiguated
    """
    for author,value in authors.items():
        if value[8] == "Disambig":
            if publication_uri in disambiguation_report:
                result = disambiguation_report[publication_uri]
                result[len(result.keys())+1] = value
                disambiguation_report[publication_uri] = result
            else:
                disambiguation_report[publication_uri] = {1:value}
    return
#
# start here.  Create a parser for bibtex and use it to read the file of bibtex entries.
# open the output files
#
print datetime.now(),"Read the BibTex"
bibtex_file_name = sys.argv[1]
[rdf_file,rpt_file,lst_file] = open_files(bibtex_file_name)
parser = bibtex.Parser()
bib_data = parser.parse_file(bibtex_file_name)
bib_sorted = sorted(bib_data.entries.items(), key = lambda x: x[1].fields['title'])
print >>rdf_file,"<!--",len(bib_data.entries.keys()),"publications to be processed -->"
print datetime.now(),len(bib_data.entries.keys()),"publications to be processed."
#
#  make dictionaries for people, papers, publishers and journals.
#
print datetime.now(),"Creating the dictionaries"
print datetime.now(),"Publishers"
publisher_dictionary = vivotools.make_publisher_dictionary()
print datetime.now(),"Journals"
journal_dictionary = vivotools.make_journal_dictionary()
print datetime.now(),"People"
dictionaries = make_people_dictionaries()
print datetime.now(),"Titles"
title_dictionary = vivotools.make_title_dictionary()
#
# process the papers
#
print >>rdf_file,rdf_header

for key,value in bib_sorted:
    try:
        title = value.fields['title'].title() + " "
    except:
        title_report["No title"] = ["No Title", None, 1]
        print >>rdf_file,"<!-- No title found. No RDF necessary -->"
        continue
    title = abbrev_to_words(title)
    title = title[0:-1]
    if title in title_report:
        print >>rdf_file,"<!-- Title",title,"handled previously.  No RDF necessary -->"
        title_report[title][2] = title_report[title][2] + 1 # increase the count for this title
        continue
    else:
        print >>rdf_file,"<!-- Begin RDF for " + title + " -->"
        print datetime.now(),"<!-- Begin RDF for " + title + " -->"
        document = {}
        document['title'] = title
        title_report[title] = ["Start", None, 1] # No create, no URI yet, count
        [found,uri] = vivotools.find_title(title,title_dictionary)
        if not found:
            title_report[title][0] = "Create" # Create
            #
            # Authors
            #
            [author_rdf,authors] = make_author_rdf(value,title)
            document['authors'] = make_document_authors(authors)
            if count_uf_authors(authors) == 0:
                print >>rdf_file,"<!-- End RDF.  No UF authors for " + title + " No RDF necessary -->"
                title_report[title][0] = "No UF Auth"
                continue
            update_author_report(authors,title)
            #
            # Datetime
            #
            [datetime_rdf,datetime_uri] = make_datetime_rdf(value,title)
            #
            # Publisher
            #
            [journal_create,journal_name,journal_uri] = make_journal_uri(value)
            [publisher_create,publisher,publisher_uri,publisher_rdf] = make_publisher_rdf(value)
            #
            # Journal
            #
            [journal_rdf,journal_uri] = make_journal_rdf(value,journal_create,journal_name,journal_uri)
            #
            # Publisher/Journal bi-directional links
            #
            publisher_journal_rdf = ""
            if journal_uri != "" and publisher_uri != "" and (journal_create or publisher_create):
                publisher_journal_rdf = make_publisher_journal_rdf(publisher_uri,journal_uri)
            #
            # Authorships
            #
            publication_uri = vivotools.get_vivo_uri()
            title_report[title][1] = publication_uri 
            [authorship_rdf,authorship_uris] = make_authorship_rdf(authors,publication_uri)
            #
            # AuthorInAuthorships
            #
            author_in_authorship_rdf = make_author_in_authorship_rdf(authors,authorship_uris)
            #
            #  Journal/Publication bi-directional links
            #
            if journal_uri != "" and publication_uri != "":
                journal_publication_rdf = make_journal_publication_rdf(journal_uri,publication_uri)
            #
            # Publication
            #
            publication_rdf = make_publication_rdf(value,title,publication_uri,datetime_uri,authorship_uris)
            print >>rdf_file,datetime_rdf,publisher_rdf,journal_rdf,publisher_journal_rdf,author_rdf,authorship_rdf, \
                author_in_authorship_rdf,journal_publication_rdf,publication_rdf
            print >>rdf_file,"<!-- End RDF for " + title + " -->"
            print >>lst_file,vivotools.string_from_document(document),'VIVO uri',publication_uri,'\n'
            update_disambiguation_report(authors,publication_uri)
        else:
            title_report[title][0] = "Found"
            title_report[title][1] = uri
            print >>rdf_file,"<!-- Found: " + title + " No RDF necessary -->"
print >>rdf_file,rdf_footer

#
# Reports
#
print >>rpt_file,"""

Publisher Report

Lists the publishers that appear in the bibtex file in alphabetical order.  For
each publisher, show the improved name, the number of papers in journals of this publisher,
the action to be taken for the publisher and the VIVO URI -- the URI is the new
URI to be created if Action is Create, otherwise it is the URI of the found publisher
in VIVO.

Publisher                             Papers Action VIVO URI
---------------------------------------------------------------------------------"""
publisher_count = 0
actions = {}
for publisher in sorted(publisher_report.keys()):
    publisher_count = publisher_count + 1
    [create,uri,count] = publisher_report[publisher]
    if create:
        result = "Create"
    else:
        result = "Found "
    actions[result] = actions.get(result,0) + 1
    print >>rpt_file, "{0:40}".format(publisher[0:40]),"{0:>3}".format(count),result,uri
print >>rpt_file,""
print >>rpt_file, "Publisher count by action"
print >>rpt_file, ""
for action in sorted(actions):
    print >>rpt_file, action,actions[action]
print >>rpt_file, publisher_count,"publisher(s)"

print >>rpt_file, """

Journal Report

Lists the journals that appear in the bibtex file in alphabetical order.  For
each journal, show the improved name, the number of papers t be linked to the journal,
the action to be taken for the journal and the VIVO URI -- the URI is the new
URI to be created if Action is Create, otherwise it is the URI of the found journal
in VIVO.

Journal                               Papers Action VIVO URI
---------------------------------------------------------------------------------"""
journal_count = 0
actions = {}
for journal in sorted(journal_report.keys()):
    journal_count = journal_count + 1
    [create,uri,count] = journal_report[journal]
    if create:
        result = "Create"
    else:
        result = "Found "
    actions[result] = actions.get(result,0) + 1
    print >>rpt_file, "{0:40}".format(journal[0:40]),"{0:>3}".format(count),result,uri
print >>rpt_file, ""
print >>rpt_file, "Journal count by action"
print >>rpt_file, ""
for action in sorted(actions):
    print >>rpt_file, action,actions[action]
print >>rpt_file, journal_count,"journal(s)"


print >>rpt_file, """

Title Report

Lists the titles that appear in the bibtex file in alphabetical order.  For
each title, show the action to be taken, the number of times the title appears in
the bibtex, the improved title and the VIVO URI of the publication -- the URI is the new
URI to be created if action is Create, otherwise it is the URI of the found publication
in VIVO.

Action   # Title and VIVO URI
---------------------------------------------------------------------------------"""
title_count = 0
actions = {}
for title in sorted(title_report.keys()):
    title_count = title_count +1
    [action,uri,count] = title_report[title]
    actions[action] = actions.get(action,0) + 1
    print >>rpt_file, "{0:>10}".format(action),title,uri
print >>rpt_file, ""
print >>rpt_file, "Title count by action"
print >>rpt_file, ""
for action in sorted(actions):
    print >>rpt_file, action,actions[action]
print >>rpt_file, title_count,"title(s)"

print >>rpt_file, """

Author Report

For each author found in the bibtex file, show the author's name followed by the number of papers
for the author in the bibtex to be entered, followed by 
a pair of results for each time the author appears on a paper in the bibtex.  The result
pair contains an action and a URI.  The action is "non UF" if a non-UF author stub will be
be created, the URI is the URI of the new author stub.  Action "Make UF" if a new UF author
stub will be created with the URI of the new author stub.  "Found UF" indicate the author was
found at the URI.  "Disambig" if multiple UF people were found with the given name.  The URI
is the URI of one of the found people.  Follow-up is needed to determine if correct and
reassign author if not correct.

Author                    Action   URI                                          Action   URI
----------------------------------------------------------------------------------------------"""
author_count = 0
actions = {}
for author in sorted(author_report.keys()):
    author_count = author_count + 1
    results = ""
    papers = len(author_report[author])
    action = author_report[author][1][8] # 1st report, 8th value is action
    actions[action] = actions.get(action,0) + 1    
    for key in author_report[author].keys():
        value = author_report[author][key]
        results = results + value[8] + " " + "{0:45}".format(value[9])
    print >>rpt_file, "{0:25}".format(author),"{0:>3}".format(papers),results
print >>rpt_file, ""
print >>rpt_file, "Author count by action"
print >>rpt_file, ""
for action in sorted(actions):
    print >>rpt_file, action,actions[action]
print >>rpt_file, author_count,"authors(s)"

print >>rpt_file, """

Disambiguation Report

For each publication with one or more authors to disambiguate, list the paper, and
then the authors in question with each of the possible URIs to be disambiguated, show the URI
of the paper, and then for each author that needs to be disambiguated on the paper, show
the last name, first name and middle initial and the all the URIs in VIVO for UF persons
with the same names.
"""

for uri in disambiguation_report.keys():
    print >>rpt_file,"The publication at",uri,"has one or more authors in question"
    for key,value in disambiguation_report[uri].items():
        uris = value[9].split(";")
        print >>rpt_file,"    ",value[4],value[5],value[6],":"
        for u in uris:
            print >>rpt_file,"        ",u
        print >>rpt_file
    print >>rpt_file
#
#  Close the files, we're done
#
rpt_file.close()
rdf_file.close()
lst_file.close()

    
