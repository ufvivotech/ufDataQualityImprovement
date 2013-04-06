#!/usr/bin/env/python
"""vivotools.py -- A library of useful things for working with VIVO

    1.1     3/2/2013    MC
            Added assert_data_property to generate RDF for asserting that an
            entity have a named data property value
            Added update_data property to generate addtion and subtraction RDF
            based on five case logic to update a VIVO data property value with
            a source data property value
            Added hr_abbrev_to_words to fix position and working titles
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"

import urllib, urllib2, json, random
from string import Template
from datetime import datetime,date
import time
from xml.dom.minidom import parseString
import sys, httplib                     # tools for making HTTP requests
import tempita
import csv
from Bio import Entrez

def hr_abbrev_to_words(s):
    """
    HR uses a series of abbreviations to fit job titles into limited text
    strings.
    Here we attempt to reverse the process -- a short title is turned into a
    longer one
    """

    s = s.lower() # convert to lower
    s = s.title() # uppercase each word
    s = s + ' '   # add a trailing space so we can find these abbreviated words throughout the string
    t = s.replace(", ,",",")
    t = t.replace("  "," ")
    t = t.replace(" & "," and ")
    t = t.replace(" &"," and ")
    t = t.replace("&"," and ")
    t = t.replace("/"," @")
    t = t.replace("/"," @") # might be two slashes in the input
    t = t.replace(","," !")
    t = t.replace("-"," #")
    t = t.replace("Aca ","Academic ")
    t = t.replace("Act ","Acting ")
    t = t.replace("Advanc ","Advanced ")
    t = t.replace("Adv ","Advisory ")
    t = t.replace("Agric ","Agricultural ")
    t = t.replace("Alumn Aff ","Alumni Affairs ")
    t = t.replace("Ast #R ","Research Assistant ")
    t = t.replace("Ast #G ","Grading Assistant ")
    t = t.replace("Ast #T ","Teaching Assistant ")
    t = t.replace("Ast ","Assistant ")
    t = t.replace("Affl ","Affiliate ")
    t = t.replace("Aso ","Associate ")
    t = t.replace("Asoc ","Associate ")
    t = t.replace("Assoc ","Associate ")
    t = t.replace("Bio ","Biological ")
    t = t.replace("Prof ","Professor ")
    t = t.replace("Mstr ","Master ")
    t = t.replace("Couns ","Counselor ")
    t = t.replace("Adj ","Adjunct ")
    t = t.replace("Dist ","Distinguished ")
    t = t.replace("Chr ","Chair ")
    t = t.replace("Cio ","Chief Information Officer ")
    t = t.replace("Coo ","Chief Operating Officer ")
    t = t.replace("Coord ","Coordinator ")
    t = t.replace("Co ","Courtesy ")
    t = t.replace("Clin ","Clinical ")
    t = t.replace("Dn ","Dean ")
    t = t.replace("Finan ","Financial ")
    t = t.replace("Stu ","Student ")
    t = t.replace("Prg ","Program ")
    t = t.replace("Dev ","Development ")
    t = t.replace("Aff ","Affiliate ")
    t = t.replace("Svcs ","Services ")
    t = t.replace("Devel ","Development ")
    t = t.replace("Tech ","Technician ")
    t = t.replace("Progs ","Programs ")
    t = t.replace("Facil ","Facility ")
    t = t.replace("Hlth ","Health ")
    t = t.replace("Int ","Interim ")
    t = t.replace("Sctst ","Scientist ")
    t = t.replace("Supp ","Support ")
    t = t.replace("Cty ","County ")
    t = t.replace("Ext ","Extension ")
    t = t.replace("Emer ","Emeritus ")
    t = t.replace("Enforce ","Enforcement ")
    t = t.replace("Environ ","Environmental ")
    t = t.replace("Gen ","General ")
    t = t.replace("Jnt ","Joint ")
    t = t.replace("Eng ","Engineer ")
    t = t.replace("Ctr ","Center ")
    t = t.replace("Opr ","Operator ")
    t = t.replace("Admin ","Administrative ")
    t = t.replace("Dis ","Distinguished ")
    t = t.replace("Ser ","Service ")
    t = t.replace("Rep ","Representative ")
    t = t.replace("Radiol ","Radiology ")
    t = t.replace("Technol ","Technologist ")
    t = t.replace("Pres ","President ")
    t = t.replace("Pres5 ","President 5 ")
    t = t.replace("Pres6 ","President 6 ")
    t = t.replace("Emin ","Eminent ")
    t = t.replace("Cfo ","Chief Financial Officer ")
    t = t.replace("Prov ","Provisional ")
    t = t.replace("Adm ","Administrator ")
    t = t.replace("Info ","Information ")
    t = t.replace("It ","Information Technology ")
    t = t.replace("Mgr ","Manager ")
    t = t.replace("Mgt ","Management ")
    t = t.replace("Vis ","Visiting ")
    t = t.replace("Phas ","Phased ")
    t = t.replace("Prog ","Programmer ")
    t = t.replace("Pract ","Practitioner ")
    t = t.replace("Registr ","Registration ")
    t = t.replace("Rsch ","Research ")
    t = t.replace("Rsrh ","Research ")
    t = t.replace("Ret ","Retirement ")
    t = t.replace("Sch ","School ")
    t = t.replace("Sci ","Scientist ")
    t = t.replace("Svcs ","Services ")
    t = t.replace("Serv ","Service ")
    t = t.replace("Tch ","Teaching ")
    t = t.replace("Tele ","Telecommunications ")
    t = t.replace("Tv ","TV ")
    t = t.replace("Univ ","University ")
    t = t.replace("Educ ","Education ")
    t = t.replace("Crd ","Coordinator ")
    t = t.replace("Res ","Research ")
    t = t.replace("Dir ","Director ")
    t = t.replace("Pky ","PK Yonge ")
    t = t.replace("Rcv ","Receiving ")
    t = t.replace("Sr ","Senior ")
    t = t.replace("Spec ","Specialist ")
    t = t.replace("Spc ","Specialist ")
    t = t.replace("Spv ","Supervisor ")
    t = t.replace("Supv ","Supervisor ")
    t = t.replace("Supt ","Superintendant ")
    t = t.replace("Pky ","P. K. Yonge ")
    t = t.replace("Ii ","II ")
    t = t.replace("Iii ","III ")
    t = t.replace("Iv ","IV ")
    t = t.replace("Communic ","Communications ")
    t = t.replace("Postdoc ","Postdoctoral ")
    t = t.replace("Tech ","Technician ")
    t = t.replace("Vp ","Vice President ")
    t = t.replace(" @","/") # restore /
    t = t.replace(" @","/")
    t = t.replace(" !",",") # restore ,
    t = t.replace(" #","-") # restore -
    return t[:-1] # Take off the trailing space

def assert_data_property(uri,data_property,value):
    """
    Given a uri and a data_property name, and a value, generate rdf to assert
    assert the uri has the value of the data property

    Note:
    This function does not check that the data property name is valid
    """
    data_property_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{uri}}">
        <{{data_property}}>{{value}}</{{data_property}}>
    </rdf:Description>
    """)
    rdf = data_property_template.substitute(uri=uri, \
        data_property=data_property,value=value)
    return rdf

def update_data_property(uri,data_property,vivo_value,source_value):
    """
    Given the URI of an entity, the name of a data_proprty, the current
    vivo value for the data_property and the source (correct) value for
    the property, use five case logic to generate appropriate subtraction
    and addtion rdf to update the data_property

    Note:   we could have shortened the if statements, but they might not have
            been as clear

    To do:  Generalize to handle a URI assertion
            Generalize to handle a sub-class object assertion
    """
    srdf = ""
    ardf = ""
    if vivo_value == None and source_value == None:
        pass
    elif vivo_value == None and source_value != None:
        ardf = assert_data_property(uri,data_property,source_value)
    elif vivo_value !=None and source_value == None:
        srdf = assert_data_property(uri,data_property,vivo_value)
    elif vivo_value != None and source_value != None and \
        vivo_value == source_value:
        pass
    elif vivo_value != None and source_value != None and \
        vivo_value != source_value:
        srdf = assert_data_property(uri,data_property,vivo_value)
        ardf = assert_data_property(uri,data_property,source_value)
    return [ardf,srdf]

def make_datetime_interval_rdf(start_date,end_date):
    """
    Given a start_date and/or end_date in isoformat, create the RDF for
    a datetime entity
    """
    [start_date_rdf,start_date_uri] = make_datetime_rdf(start_date)
    [end_date_rdf,end_date_uri] = make_datetime_rdf(end_date)
    [datetime_interval_rdf,datetime_interval_uri] = \
        make_dt_interval_rdf(start_date_uri,end_date_uri)
    rdf = start_date_rdf + end_date_rdf + datetime_interval_rdf
    return [rdf,datetime_interval_uri]

def make_datetime_rdf(datetime):
    """
    Given a datetime string in isoformat, create the RDF for a datetime object
    """
    datetime_template = tempita.Template(
    """
    <rdf:Description rdf:about="{{datetime_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#DateTimeValue"/>
        <core:dateTimePrecision rdf:resource="http://vivoweb.org/ontology/core#yearMonthDayPrecision"/>
        <core:dateTime>{{datetime}}</core:dateTime>
    </rdf:Description>
""")
    if datetime == "" or datetime == None:
        datetime_uri = None
        rdf = ""
    else: 
        datetime_uri = get_vivo_uri()
        rdf = datetime_template.substitute(datetime_uri=datetime_uri,
                                           datetime=datetime)
    return [rdf,datetime_uri]

def make_dt_interval_rdf(start_uri,end_uri):
    """
    Given a start and end uri, return the rdf for a datetime interval with the given start and end uris. Either may be empty.
    """
    dt_interval_template = tempita.Template("""
    <rdf:Description rdf:about="{{interval_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#DateTimeInterval"/>
        {{if start_uri != "" and start_uri != None}}
            <core:start rdf:resource="{{start_uri}}"/>
        {{endif}}
        {{if end_uri != "" and end_uri != None}}
            <core:end rdf:resource="{{end_uri}}"/>
        {{endif}}
    </rdf:Description>
""")
    if (start_uri == "" or start_uri == None) and (end_uri == "" or end_uri == None):
        rdf = ""
        interval_uri = None
    else:
        interval_uri = get_vivo_uri()
        rdf = dt_interval_template.substitute(interval_uri=interval_uri,
                                              start_uri=start_uri,
                                              end_uri=end_uri)
    return [rdf,interval_uri]

def read_csv(filename):
    """
    Given a filename, read the CSV file with that name.  We use "!" as a
    separator in CSV files to allow commas to appear in values.

    CSV files read by this function follow these conventions:
    --  use "!" as a seperator
    --  have a first row that contains column headings.  Columns headings
        must be known to VIVO, typically in the form prefix:name
    --  all elements must have values.  To specify a missing value, use
        the string "None" between separators, that is !None!
    --  leading a trailing whitespace in values is ignored.  ! The  ! will be
        read as "The"

    CSV files processed by read_CSV will be returned as a dictionary of
    dictionaries, one dictionary per row with a name of and an
    integer value for the row number of data.

    Exceptions
    --  will raise RowError if number of data values on a subsequent row
        does not match the number of headings given on the first row.

    To Do:
    --  "know" some of the VIVO data elements, checking and converting as
        appropriate.  In particular, handle dates and convert to datetime
    """

    class RowError(Exception):
        pass
    heading = []
    row_number = 0
    data = {}
    csvReader = csv.reader(open(filename,'rb'),delimiter="!")
    for row in csvReader:
        i = 0
        for r in row:
            row[i] = r.strip() # remove white space fore and aft
            i = i + 1
        if heading == []:
            heading = row # the first row is the heading
            number_of_columns = len(heading)
            continue
        row_number = row_number + 1
        if len(row) != number_of_columns:
            raise RowError("On row "+str(row_number)+", expecting "+
                           str(number_of_columns)+ " data values. Found "+
                           str(len(row))+" data values.")
        data[row_number] = {}
        i = 0
        for r in row:
            data[row_number][heading[i]] = r
            i = i + 1
    return data
        
def get_pmid_from_doi(doi, email='mconlon@ufl.edu', tool='PythonQuery', database='pubmed'):
    """
    Given a DOI, return the PMID of ther corresponding PubMed Article.  If not found in PubMed, return None
    Adapted from http://simon.net.nz/articles/query-pubmed-for-citation-information-using-a-doi-and-python/
    """
    params = {'db':database,'tool':tool,'email':email,'term': doi,'usehistory':'y','retmax':1}
    url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?' + urllib.urlencode(params)
    data = urllib.urlopen(url).read()
    xmldoc = parseString(data)
    ids = xmldoc.getElementsByTagName('Id')
    if len(ids) == 0:
        pmid = None
    else:
        pmid = ids[0].childNodes[0].data
    return pmid

def get_pubmed_values_from_pubmed(doi):
    """
    Given the doi of a paper, return the current values (if any) for PMID,
    PMCID, Grants Cited and Full_text_url of the paper in PubMed and
    PubMed Central. If values do not exist, return None.

    Return four items in a list.  Grants cited is itself a list of
    strings.  String values are sponsordids for grants
    """
    Entrez.email = 'mconlon@ufl.edu'
    pmid = None
    pmcid = None
    grants_cited = []
    full_text_url = None
    pmid = get_pmid_from_doi(doi)
    if pmid == None:
        return [None,None,[],None]
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    records = Entrez.parse(handle)
    for record in records:
        article_id_list = record['PubmedData']['ArticleIdList']
        for article_id in article_id_list:
            attributes = article_id.attributes
            if 'IdType' in attributes:
                if attributes['IdType'] == 'pmc':
                    pmcid = str(article_id)

    try:
        grants = record['MedlineCitation']['Article']['GrantList']
        for grant in grants:
            grants_cited.append(grant['GrantID'])
    except:
        grants_cited = []
    if pmcid == None:
        return [pmid,None,grants_cited,None]
    full_text_url = "http://www.ncbi.nlm.nih.gov/pmc/articles/" + pmcid.upper()+ "/pdf"
    return [pmid,pmcid,grants_cited,full_text_url]

def get_pubmed_values_from_vivo(paper_uri):
    """
    Given the URI of a paper in VIVO, return the current values (if any) for PMID, PMCID, Grants Cited and Full_text_url.
    If values do not exist, return None.

    Return four items in a list.  Grants cited is itself a list of strings.  String values are sponsordids for grants
    """
    rdf_uri = make_rdf_uri(paper_uri)
    f = urllib2.urlopen(rdf_uri)
    rdf = f.read()
    dom = parseString(rdf)
    pmid = None
    for node in dom.getElementsByTagName('bibo:pmid'):
        pmid = node.toxml()
        pmid = pmid.replace('<bibo:pmid>','')
        pmid = pmid.replace('</bibo:pmid>','')
        break # stop on the first pmid value found
    pmcid = None
    for node in dom.getElementsByTagName('ufVivo:pmcid'):
        pmcid = node.toxml()
        pmcid = pmcid.replace('<ufVivo:pmcid>','')
        pmcid = pmcid.replace('</ufVivo:pmcid>','')
        break # stop on the first pmcid value found
    grants_cited = []
    for node in dom.getElementsByTagName('ufVivo:grantCited'):
        grant_cited = node.toxml()
        grant_cited = grant_cited.replace('<ufVivo:grantCited>','')
        grant_cited = grant_cited.replace('</ufVivo:grantCited>','')
        grants_cited.append(grant_cited)
    #
    #   Dereference the webpage references for each web page (most papers
    #   have zero or one), get the webpage uri, go there, parse it, and
    #   find the full text URL.  The code stops on the first fulltextURL
    #   attribute of a web page, but processes all web pages and returns
    #   the last fulltextURL found in the collection.
    #
    full_text_url = None
    for node in dom.getElementsByTagName('<vivo:webpage>'):
        web_page_url = node.getAttribute('rdf:resource')
        web_page_uri = make_rdf_uri(web_page_uri)
        f = urllib2.urlopen(web_page_uri)
        rdf = f.read()
        dom = parseString(rdf)    
        for node in dom.getElementsByTagName('ufVivo:fullTextURL'):
            full_text_url = node.toxml()
            full_text_url = full_text_url.replace('<ufVivo:fullTextURL>','')
            full_text_url = full_text_url.replace('</ufVivo:fullTextURL>','')
            break # stop on the first fullTextURL value found on the web page
    return [pmid,pmcid,grants_cited,full_text_url]

def rdf_header():
    """
    Return a text string containing the standard VIVO RDF prefixes suitable as
    the beginning of an RDF statement to add or remove RDF to VIVO.

    Note:  This function should be updated for each new release of VIVO and to
        include local ontologies and extensions.
    """
    rdf_header = """<rdf:RDF
    xmlns:rdf     = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs    = "http://www.w3.org/2000/01/rdf-schema#"
    xmlns:xsd     = "http://www.w3.org/2001/XMLSchema#"
    xmlns:owl     = "http://www.w3.org/2002/07/owl#"
    xmlns:swrl    = "http://www.w3.org/2003/11/swrl#"
    xmlns:swrlb   = "http://www.w3.org/2003/11/swrlb#"
    xmlns:vitro1  = "http://vitro.mannlib.cornell.edu/ns/vitro/0.7#"
    xmlns:bibo    = "http://purl.org/ontology/bibo/"
    xmlns:c4o     = "http://purl.org/spar/c4o/"
    xmlns:dcelem  = "http://purl.org/dc/elements/1.1/"
    xmlns:dcterms = "http://purl.org/dc/terms/"
    xmlns:event   = "http://purl.org/NET/c4dm/event.owl#"
    xmlns:foaf    = "http://xmlns.com/foaf/0.1/"
    xmlns:fabio   = "http://purl.org/spar/fabio/"
    xmlns:geo     = "http://aims.fao.org/aos/geopolitical.owl#"
    xmlns:pvs     = "http://vivoweb.org/ontology/provenance-support#"
    xmlns:ero     = "http://purl.obolibrary.org/obo/"
    xmlns:scires  = "http://vivoweb.org/ontology/scientific-research#"
    xmlns:skos    = "http://www.w3.org/2004/02/skos/core#"
    xmlns:ufVivo  = "http://vivo.ufl.edu/ontology/vivo-ufl/"
    xmlns:vitro2  = "http://vitro.mannlib.cornell.edu/ns/vitro/public#"
    xmlns:vivo    = "http://vivoweb.org/ontology/core#">"""
    return rdf_header

def rdf_footer():
    """
    Return a text string suitable for edning an RDF statement to add or
    remoe RDF/XML to VIVO
    """
    rdf_footer = """</rdf:RDF>"""
    return rdf_footer

def make_rdf_uri(uri):
    """
    Given a uri of a VIVO profile, generate the URI of the corresponding RDF page
    """
    k = uri.rfind("/")
    word = uri[k+1:]
    rdf_uri = uri + "/" + word + ".rdf"
    return rdf_uri

def key_string(s):
    """
    Given a string s, return a string with a bunch of punctuation and special characters
    removed and then everything lower cased.  Useful for matching strings in which case,
    punctuation and special characters should not be considered in the match
    """
    k = s.encode("utf-8","ignore").translate(None,""" \t\n\r\f!@#$%^&*()_+:"<>?-=[]\;',./""")
    k = k.lower()
    return k

def get_triples(uri):
    """
    Given a VIVO URI, return all the triples referencing that URI as subject    
    """
    query = tempita.Template("""
    SELECT ?p ?o WHERE
    {
    <{{uri}}> ?p ?o .
    }""")
    query = query.substitute(uri=uri)
    result = vivo_sparql_query(query)
    return result

def show_triples(triples):
    """
    Given an object returned by get_triples, print the object
    """
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    #
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        print "{0:65}".format(p),o
        i = i + 1
    return

def get_organization(organization_uri):
    """
    Given the URI of an organnization, return an object that contains the
    organization it represents.

    As for most of the access functions, additional attributes can be added.
    """
    organization = {}
    organization['uri'] = organization_uri
    organization['sub_organization_within_uris'] = []
    organization['has_sub_organization_uris'] = []
    triples = get_triples(organization_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            organization['label'] = o
        if p == "http://vivoweb.org/ontology/core#subOrganizationWithin":
            organization['sub_organization_within_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#hasSubOrganization":
            organization['has_sub_organization_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#overview":
            organization['overview'] = o
        i = i + 1
    return organization    

def get_person(person_uri,get_publications=False,get_grants=False):
    """
    Given a person URI, return an object that ccontains the persn it represents.
    
    Optionally dereference publications, grants, courses.  Each may add
    significant run time
    """
    person = {}
    person['authorship_uris'] = []
    person['pi_role_uris'] = []
    person['coi_role_uris'] = []
    person['teaching_role_uris'] = []
    person['publications'] = []
    person['grants'] = []
    triples = get_triples(person_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#primaryPhoneNumber":
            person['primary_phone_number'] = o
        if p == "http://vivoweb.org/ontology/core#primaryEmail":
            person['primary_email'] = o
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/ufid":
            person['ufid'] = o
        if p == "http://xmlns.com/foaf/0.1/firstName":
            person['first_name'] = o
        if p == "http://xmlns.com/foaf/0.1/lastName":
            person['last_name'] = o
        if p == "http://vivoweb.org/ontology/core#middleName":
            person['middle_name'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            person['label'] = o
        if p == "http://vivoweb.org/ontology/core#preferredTitle":
            person['preferred_title'] = o
        if p == "http://vivoweb.org/ontology/core#faxNumber":
            person['fax_number'] = o
        if p == "http://vivoweb.org/ontology/core#authorInAuthorship":
            person['authorship_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#hasPrincipalInvestigatorRole":
            person['pi_role_uris'].append(o)
        if p == \
            "http://vivoweb.org/ontology/core#hasCo-PrincipalInvestigatorRole":
            person['coi_role_uris'].append(o)
        if p == "http://vivoweb.org/ontology/core#hasTeacherRole":
            person['teaching_role_uris'].append(o)
        #
        # deref the home department
        if p == "http://vivo.ufl.edu/ontology/vivo-ufl/homeDept":
            home_department = get_organization(o)
            if 'label' in home_department: # home department might be incomplete
                person['home_department_name'] = home_department['label']
        i = i + 1
        
    # deref the authorships
    if get_publications:
        for authorship_uri in person['authorship_uris']:
            authorship = get_authorship(authorship_uri)
            if 'publication_uri' in authorship: # authorship might be incomplete
                publication = get_publication(authorship['publication_uri'])
                person['publications'].append(publication)
            
    # deref the investigator roles
    if get_grants:
        for role_uri in person['pi_role_uris']:
            role = get_role(role_uri)
            if 'grant_uri' in role:  # some roles are broken
                grant = get_grant(role['grant_uri'])
                person['grants'].append(grant)
        for role_uri in person['coi_role_uris']:
            role = get_role(role_uri)
            if 'grant_uri' in role:  # some roles are broken
                grant = get_grant(role['grant_uri'])
                person['grants'].append(grant)
            
    # deref the teaching roles
    return person

def get_role(role_uri):
    """
    Given a URI, return an object that contains the role it represents
    """
    role = {}
    triples = get_triples(role_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#roleIn":
            role['grant_uri'] = o
        if p == "http://vivoweb.org/ontology/core#roleContributesTo":
            role['grant_uri'] = o
        i = i + 1
    return role


def get_authorship(authorship_uri):
    """
    Given a URI, return an object that contains the authorship it represents
    """
    authorship = {}
    triples = get_triples(authorship_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#authorRank":
            authorship['author_rank'] = o
        if p == "http://vivoweb.org/ontology/core#linkedAuthor":
            authorship['author_uri'] = o
        if p == "http://vivoweb.org/ontology/core#linkedInformationResource":
            authorship['publication_uri'] = o
        if p == "http://vivoweb.org/ontology/core#isCorrespondingAuthor":
            authorship['corresponding_author'] = o
        i = i + 1
    return authorship

def get_publication(publication_uri):
    """
    Given a URI, return an object that contains the publication it represents.
    We have to dereference the publication venue to get the journal name, and
    the datetime value to get the date of publication.  We don't rebuild the
    author list (too dang much work, perhaps the author list should just be
    maintained as a property of the publication)

    The resulting object can be displayed using string_from_document
    """
    publication = {'publication_uri':publication_uri} #include the uri
    triples = get_triples(publication_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']

        if p == "http://purl.org/ontology/bibo/doi":
            publication['doi'] = o
        if p == "http://purl.org/ontology/bibo/pmid":
            publication['pmid'] = o
        if p == "http://purl.org/ontology/bibo/pageStart":
            publication['page_start'] = o
        if p == "http://purl.org/ontology/bibo/pageEnd":
            publication['page_end'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            publication['title'] = o
        if p == "http://purl.org/ontology/bibo/volume":
            publication['volume'] = o
        if p == "http://purl.org/ontology/bibo/number":
            publication['number'] = o
        #
        # deref the publication_venue
        if p == "http://vivoweb.org/ontology/core#hasPublicationVenue":
            publication_venue = get_publication_venue(o)
            try:
                publication['journal'] = publication_venue['label']
            except:
                pass
        #
        # deref the datetime
        if p == "http://vivoweb.org/ontology/core#dateTimeValue":
            datetime_value = get_datetime_value(o)
            try:
                publication['date'] = datetime_value['date']
            except:
                pass
        i = i + 1
    return publication

def get_datetime_value(datetime_value_uri):
    """
    Given a URI, return an object that contains the datetime value it
    represents
    """
    datetime_value = {}
    triples = get_triples(datetime_value_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#dateTime":
            datetime_value['datetime'] = o
            year = o[0:4]
            month = o[5:7]
            day = o[8:10]
        if p == "http://vivoweb.org/ontology/core#dateTimePrecision":
            datetime_value['datetime_precision'] = o
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearPrecision":
                datetime_value['datetime_precision'] =  'year'
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearMonthPrecision":
                datetime_value['datetime_precision'] =  'year_month'
            if datetime_value['datetime_precision'] == \
                "http://vivoweb.org/ontology/core#yearMonthDayPrecision":
                datetime_value['datetime_precision'] =  'year_month_day'
        if 'datetime' in datetime_value and 'datetime_precision' in \
            datetime_value:
            if datetime_value['datetime_precision'] == "year":
                datetime_value['date'] = {'year':year}
            if datetime_value['datetime_precision'] == "year_month":
                datetime_value['date'] = {'year':year,'month':month}             
            if datetime_value['datetime_precision'] == "year_month_day":
                datetime_value['date'] = {'year':year,'month':month,'day':day}              
        i = i + 1
    return datetime_value

def get_datetime_interval(datetime_interval_uri):
    """
    Given a URI, return an object that contains the datetime_interval it
    represents
    """
    datetime_interval = {}
    triples = get_triples(datetime_interval_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#start":
            datetime_value = get_datetime_value(o)
            datetime_interval['start_date'] = datetime_value
        if p == "http://vivoweb.org/ontology/core#end":
            datetime_value = get_datetime_value(o)
            datetime_interval['end_date'] = datetime_value
        i = i + 1
    return datetime_interval


def get_publication_venue(publication_venue_uri):
    """
    Given a URI, return an object that contains the publication venue it
    represents
    """
    publication_venue = {}
    triples = get_triples(publication_venue_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://purl.org/ontology/bibo/issn":
            publication_venue['issn'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            publication_venue['label'] = o
        i = i + 1
    return publication_venue

def get_grant(grant_uri):
    """
    Given a URI, return an object that contains the grant it represents
    """
    grant = {}
    triples = get_triples(grant_uri)
    try:
        count = len(triples["results"]["bindings"])
    except:
        count = 0
    i = 0
    while i < count:
        b = triples["results"]["bindings"][i]
        p = b['p']['value']
        o = b['o']['value']
        if p == "http://vivoweb.org/ontology/core#totalAwardAmount":
            grant['award_amount'] = o
        if p == "http://vivoweb.org/ontology/core#sponsorAwardId":
            grant['sponsor_award_id'] = o
        if p == "http://www.w3.org/2000/01/rdf-schema#label":
            grant['title'] = o 
        #
        # deref awarded by
        if p == "http://vivoweb.org/ontology/core#grantAwardedBy":
            awarded_by = get_organization(o)
            grant['awarded_by'] = awarded_by['label']
        #
        # deref datetime interval
        if p == "http://vivoweb.org/ontology/core#dateTimeInterval":
            datetime_interval = get_datetime_interval(o)
            grant['start_date'] = datetime_interval['start_date']
            grant['end_date'] = datetime_interval['end_date']
        i = i + 1
    return grant

def string_from_grant(grant):
    """
    Given a grant object, return a string representing the grant
    """
    s = ""
    if 'awarded_by' in grant:
        s = s + grant['awarded_by'] + '\n'
    if 'sponsor_award_id' in grant:
        s = s + grant['sponsor_award_id']
    if 'pi_name' in grant:
        s = s + '          ' + grant['pi_name']
    if 'award_amount' in grant:
        s = s + ' $' + grant['award_amount']
    if 'start_date' in grant:
        s = s + '          ' + grant['start_date']['date']['month'] + '/' + \
            grant['start_date']['date']['day'] + '/' + \
            grant['start_date']['date']['year']
    if 'end_date' in grant:
        s = s + ' - ' + grant['end_date']['date']['month'] + '/' + \
            grant['end_date']['date']['day'] + '/' + \
            grant['end_date']['date']['year']
    if 'title' in grant:
        s = s + '\n' + grant['title']
    return s

def make_deptid_dictionary(debug=False):
    """
    Make a dictionary for orgs in UF VIVO.  Key is DeptID.  Value is URI.
    """
    query = tempita.Template("""
SELECT ?x ?deptid WHERE
{
?x rdf:type foaf:Organization .
?x ufVivo:deptID ?deptid .
}""")
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    deptid_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        deptid = b['deptid']['value']
        uri = b['x']['value']
        deptid_dictionary[deptid] = uri
        i = i + 1
    return deptid_dictionary

def find_deptid(deptid,deptid_dictionary):
    """
    Given a deptid, find the org with that deptid.  Return True and URI if found.  Return false and None if not found
    """
    try:
        uri = deptid_dictionary[deptid]
        found = True
    except:
        uri = None
        found = False
    return [found,uri]


def make_ufid_dictionary(debug=False):
    """
    Make a dictionary for people in UF VIVO.  Key is UFID.  Value is URI.
    """
    query = tempita.Template("""
    SELECT ?x ?ufid WHERE
    {
    ?x rdf:type foaf:Person .
    ?x ufVivo:ufid ?ufid .
    }""")
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    ufid_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        ufid = b['ufid']['value']
        uri = b['x']['value']
        ufid_dictionary[ufid] = uri
        i = i + 1
    return ufid_dictionary

def find_person(ufid,ufid_dictionary):
    """
    Given a UFID, and a dictionary, find the person with that UFID.  Return True
    and URI if found. Return False and None if not found
    """
    try:
        uri = ufid_dictionary[ufid]
        found = True
    except:
        uri = None
        found = False
    return [found,uri]

def make_doi_dictionary(debug=False):
    """
    Extract all the dois of documents in VIVO and organize them into a dictionary keyed by prepared
    label with value URI
    """
    query = tempita.Template("""
SELECT ?x ?doi WHERE
{
?x rdf:type bibo:Document .
?x bibo:doi ?doi .
}""")
    doi_dictionary = {}
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    doi_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        doi = b['doi']['value']
        uri = b['x']['value']
        doi_dictionary[doi] = uri
        i = i + 1
    return doi_dictionary

def make_title_dictionary(debug=False):
    """
    Extract all the titles of documents in VIVO and organize them into a dictionary keyed by prepared
    label with value URI
    """
    query = tempita.Template("""
SELECT ?x ?label WHERE
{
?x rdf:type bibo:Document .
?x rdfs:label ?label .
}""")
    title_dictionary = {}
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    title_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        title = b['label']['value']
        key = key_string(title)
        uri = b['x']['value']
        title_dictionary[key] = uri
        i = i + 1
    return title_dictionary

def find_title(title,title_dictionary):
    """
    Given a title, and a title dictionary, find the document in VIVO with that
    title.  Return True and URI if found.  Return False and None if not found
    """
    key = key_string(title)
    try:
        uri = title_dictionary[key]
        found = True
    except:
        uri = None
        found = False
    return [found,uri]

def make_publisher_dictionary(debug=False):
    """
    Extract all the publishers from VIVO and organize them into a dictionary keyed by prepared label with value URI
    """
    query = tempita.Template("""
SELECT ?x ?label WHERE
{
?x rdf:type core:Publisher .
?x rdfs:label ?label .
}""")
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    publisher_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        publisher = b['label']['value']
        key = key_string(publisher)
        uri = b['x']['value']
        publisher_dictionary[key] = uri
        i = i + 1
    return publisher_dictionary

def find_publisher(publisher,publisher_dictionary):
    """
    Given a publisher label, and a publisher dictionary, find the publisher in VIVO with
    that label.  Return True and URI if found.  Return False and None if not found
    """
    key = key_string(publisher)
    try:
        uri = publisher_dictionary[key]
        found = True
    except:
        uri = None
        found = False
    return [found,uri]

def make_journal_dictionary(debug=False):
    """
    Extract all the journals from VIVO and organize them into a dictionary keyed
    by ISSN with value URI
    """
    query = tempita.Template("""
SELECT ?x ?issn WHERE
{
?x rdf:type bibo:Journal .
?x bibo:issn ?issn .
}""")
    query = query.substitute()
    result = vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    journal_dictionary = {}
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        issn = b['issn']['value']
        uri = b['x']['value']
        journal_dictionary[issn] = uri
        i = i + 1
    return journal_dictionary

def find_journal(issn,journal_dictionary):
    """
    Given an issn, and a journal_dictinary, find the journal in VIVO with that UFID.
    Return True and URI if found.  Return False and None if not found
    """
    try:
        uri = journal_dictionary[issn]
        found = True
    except:
        uri = None
        found = False
    return [found,uri]

def catalyst_pmid_request(first,middle,last,email,debug=False):
    """
    Give an author name at the University of Florida, return the PMIDs of papers that are
    likely to be the works of the author.  The Harvard Catalyst GETPMIDS service is called.
    
    Uses HTTP XML Post request, by www.forceflow.be
    """
    request = tempita.Template("""
        <?xml version="1.0"?>
        <FindPMIDs>
            <Name>
                <First>{{first}}</First>
                <Middle>{{middle}}</Middle>
                <Last>{{last}}</Last>
                <Suffix/>
            </Name>
            <EmailList>
                <email>{{email}}</email>
            </EmailList>
            <AffiliationList>
                <Affiliation>%university of florida%</Affiliation>
                <Affiliation>%@ufl.edu%</Affiliation>
            </AffiliationList>
            <LocalDuplicateNames>1</LocalDuplicateNames>
            <RequireFirstName>false</RequireFirstName>
            <MatchThreshold>0.98</MatchThreshold>
        </FindPMIDs>""")
    HOST = "profiles.catalyst.harvard.edu"
    API_URL = "/services/GETPMIDs/default.asp"
    request = request.substitute(first=first,middle=middle,last=last,email=email)
    webservice = httplib.HTTP(HOST)
    webservice.putrequest("POST", API_URL)
    webservice.putheader("Host", HOST)
    webservice.putheader("User-Agent","Python post")
    webservice.putheader("Content-type", "text/xml; charset=\"UTF-8\"")
    webservice.putheader("Content-length", "%d" % len(request))
    webservice.endheaders()
    webservice.send(request)
    statuscode, statusmessage, header = webservice.getreply()
    result = webservice.getfile().read()
    if debug:
        print "Request",request
        print "StatusCode, Messgage,header",statuscode, statusmessage, header
        print "result",result
    return result

def document_from_pubmed(record):
    """
    Given a record returned by Entrez for a document in pubmed, pull it apart keeping only the data elements
    useful for VIVO
    """
    d = {}
    d['title']  = record['MedlineCitation']['Article']['ArticleTitle']
    d['date']  = {'month': record['PubmedData']['History'][0]['Month'],
                  'day'  : record['PubmedData']['History'][0]['Day'],
                  'year' : record['PubmedData']['History'][0]['Year']}
    d['journal'] = record['MedlineCitation']['Article']['Journal']['Title']
    
    author_list = list(record['MedlineCitation']['Article']['AuthorList'])
    authors = {}
    i = 0
    for author in author_list:
        i = i + 1
        first = author['ForeName']
        if first.find(' ') >= 0:
            first = first[:first.find(' ')]
        last = author['LastName']
        middle = author['Initials']
        if len(middle) == 2:
            middle = str(middle[1])
        else:
            middle = ""
        key=str(i)
        authors[key] = {'first':first,'middle':middle,'last':last}
    d['authors'] = authors

    d['volume'] = record['MedlineCitation']['Article']['Journal']['JournalIssue']['Volume']
    d['issue'] = record['MedlineCitation']['Article']['Journal']['JournalIssue']['Issue']   
    d['issn'] = str(record['MedlineCitation']['Article']['Journal']['ISSN'])

    article_id_list = record['PubmedData']['ArticleIdList']
    for article_id in article_id_list:
        attributes = article_id.attributes
        if 'IdType' in attributes:
            if attributes['IdType'] == 'pubmed':
                d['pmid'] = str(article_id)
            elif attributes['IdType'] == 'doi':
                d['doi'] = str(article_id)
    
    pages = record['MedlineCitation']['Article']['Pagination']['MedlinePgn']
    pages_list = pages.split('-')
    try:
        start = pages_list[0]
        try:
            istart = int(start)
        except:
            istart = -1
    except:
        start = ""
        istart = -1
    try:
        end = pages_list[1]
        if end.find(';') > 0:
            end = end[:end.find(';')]
    except:
        end = ""
    if start != "" and istart > -1 and end != "":
        if int(start) > int(end):
            if int(end) > 99:
                end = str(int(start) - (int(start) % 1000) + int(end))
            elif int(end) > 9:
                end = str(int(start) - (int(start) % 100) + int(end))
            else:
                end = str(int(start) - (int(start) % 10) + int(end))
    d['page_start'] = start
    d['page_end'] = end
            
    return d

def string_from_document(doc):
    """
    Given a doc structure, create a string representation for printing
    """
    s = ""
    if 'authors' in doc:
        author_list = doc['authors']
        for key in sorted(author_list.keys()):
            value = author_list[key]
            s = s + value['last']
            if value['first'] == "":
                s = s + ', '
                continue
            else:
                s = s + ', ' + value['first']
            if value['middle'] == "":
                s = s + ', '
            else:
                s = s + ' ' + value['middle'] + ', '
    if 'title' in doc:
        s = s + '"' + doc['title']+'"'
    if 'journal' in doc:
        s = s + ', ' + doc['journal']
    if 'volume' in doc:
        s = s + ', ' + doc['volume']
    if 'issue' in doc:
        s = s + '(' + doc['issue'] + ')'
    if 'number' in doc:
        s = s + '(' + doc['number'] + ')'
    if 'date' in doc:
        s = s + ', ' + doc['date']['year']
    if 'page_start' in doc:
        s = s + ', pp ' + doc['page_start']
    if 'page_end' in doc:
        s = s + '-' + doc['page_end'] + '.'
    if 'doi' in doc:
        s = s + ' doi: ' + doc['doi']
    if 'pmid' in doc:
        s = s + ' pmid: ' + doc['pmid']
    return s


def make_harvest_datetime():
    dt = datetime.now()
    return dt.isoformat()

def vivo_find_result(type="core:Publisher",label="Humana Press",debug=False):
    """
    Look for entities having the specified type and the specifed label.
    If you find any, return the json object
    """
    query_template = Template(
    """
    SELECT ?x WHERE {
      ?x rdf:type $type .
      ?x rdfs:label '''$label''' .
      }
    """
    )
    query = query_template.substitute(type=type,label=label)
    if debug:
        print query
    result = vivo_sparql_query(query)
    if debug:
        print result
    return result


def vivo_find(type="core:Publisher",label="Humana Press",debug=False):
    """
    Look for entities having the specified type and the specifed label.
    If you find any, return true (found).  Otherwise return false (not found)
    """
    query_template = Template(
    """
    SELECT COUNT(?s) WHERE {
      ?s rdf:type $type .
      ?s rdfs:label '''$label''' .
      }
    """
    )
    query = query_template.substitute(type=type,label=label)
    if debug:
        print query
    response = vivo_sparql_query(query)
    if debug:
        print response
    try:
        return int(response["results"]["bindings"][0]['.1']['value']) != 0
    except:
        return False

def get_vivo_uri(prefix="http://vivo.ufl.edu/individual/n"):
    """
    Find an unused VIVO URI at the site with the specified prefix
    """
    test_uri = prefix + str(random.randint(1,9999999999))
    query = """
	SELECT COUNT(?z) WHERE {
	<""" + test_uri + """> ?y ?z
	}"""
    response = vivo_sparql_query(query)
    while (int(response["results"]["bindings"][0]['.1']['value']) != 0):
        test_uri = prefix + str(random.randint(1,9999999999))
        query = """
            SELECT COUNT(?z) WHERE {
            <""" + test_uri + """> ?y ?z
            }""" 
        response = vivo_sparql_query(query) 
    return test_uri   

def vivo_sparql_query(query, baseURL="http://sparql.vivo.ufl.edu:3030/VIVO/sparql" ,
    format="application/sparql-results+json"):
    
    """
    Given a SPARQL query string return result set of the SPARQL query.  Default
    is to call the UF VIVO SPAQRL endpoint and receive results in JSON format
    """

    prefix = """
    PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:     <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl:     <http://www.w3.org/2002/07/owl#>
    PREFIX swrl:    <http://www.w3.org/2003/11/swrl#>
    PREFIX swrlb:   <http://www.w3.org/2003/11/swrlb#>
    PREFIX vitro:   <http://vitro.mannlib.cornell.edu/ns/vitro/0.7#>
    PREFIX bibo:    <http://purl.org/ontology/bibo/>
    PREFIX dcelem:  <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX event:   <http://purl.org/NET/c4dm/event.owl#>
    PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
    PREFIX geo:     <http://aims.fao.org/aos/geopolitical.owl#>
    PREFIX pvs:     <http://vivoweb.org/ontology/provenance-support#>
    PREFIX ero:     <http://purl.obolibrary.org/obo/>
    PREFIX scires:  <http://vivoweb.org/ontology/scientific-research#>
    PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
    PREFIX ufVivo:  <http://vivo.ufl.edu/ontology/vivo-ufl/>
    PREFIX vitro:   <http://vitro.mannlib.cornell.edu/ns/vitro/public#>
    PREFIX vivo:    <http://vivoweb.org/ontology/core#>
    PREFIX core:    <http://vivoweb.org/ontology/core#>
    """
    params={
        "default-graph": "",
        "should-sponge": "soft",
        "query": prefix+query,
        "debug": "on",
        "timeout": "7000",  # 7 seconds
        "format": format,
        "save": "display",
        "fname": ""
    }
    querypart = urllib.urlencode(params)
    start = 2.0
    retries = 10
    count = 0
    while True:
        try:
            response = urllib.urlopen(baseURL,querypart).read()
            break
        except:
            count = count + 1
            if count > retries:
                break
            sleep_seconds = start**count
            print "<!-- Failed query. Count = "+str(count)+" Will sleep now for "+str(sleep_seconds)+" seconds and retry -->"
            time.sleep(sleep_seconds) # increase the wait time with each retry
     
    try:
        return json.loads(response)
    except:
        return None

