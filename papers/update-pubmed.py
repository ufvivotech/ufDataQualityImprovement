"""
    update-pubmed.py -- provide PubMed attributes for papers in VIVO

    Provide PMID, PMCID, Grants Cited and Full Text URL for papers in VIVO.
    Create subtraction RDF and addition RDF by comparing values for each
    property in VIVO with corresponding properties in PubMed.  The table below
    summarizes actions taken based on property values:

    VIVO   PubMed   Action
    null   null     None
    null   x        ADD x
    x      null     SUB x
    x      x        None
    x      y        SUB x, ADD y

    Version 1.0 MC 2012-10-23
    --  Initial version.  inspect each paper in VIVO with a DOI.  Update PMID,
        PMCID, Grants Cited and Full text link assertions as needed.

    Proposed future features
    --  Develop reusable five case logic functions
    --  Add PubMed keywords, abstract
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"

import tempita
import vivotools



def assert_pmid(paper_uri,pmid):
    """
    Given the URI of a paper in VIVO, and the value of a pubmid ID (pmid),
    return rdf to assert that the paper has the PMID
    """
    if pmid == None:
        return ""
    pmid_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{paper_uri}}">
        <bibo:pmid>{{pmid}}</bibo:pmid>
    </rdf:Description>""")
    rdf = pmid_rdf_template.substitute(paper_uri=paper_uri,pmid=pmid)
    return rdf

def assert_pmcid(paper_uri,pmcid):
    """
    Given the URI of a paper in VIVO, and the value of a pubmed central ID (pmcid),
    return rdf to assert that the paper has the PMCID
    """
    if pmcid == None:
        return ""
    pmcid_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{paper_uri}}">
        <vivo:pmcid>{{pmcid}}</vivo:pmcid>
    </rdf:Description>""")
    rdf = pmcid_rdf_template.substitute(paper_uri=paper_uri,pmcid=pmcid)
    return rdf

def assert_grants_cited(paper_uri,grants_cited):
    """
    Given the URI of a paper in VIVO, and a list of grants cited,
    return rdf to assert that the paper cites the listed grants
    """
    if grants_cited == []:
        return ""
    grants_cited_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{paper_uri}}">
    {{for sponsorID in grants_cited}}
        <ufVivo:citesGrant>{{sponsorID}}</ufVivo:citesGrant>
    {{endfor}}
    </rdf:Description>""")
    rdf = grants_cited_rdf_template.substitute(paper_uri=paper_uri,grants_cited=grants_cited)
    return rdf

def make_full_text_url_rdf(full_text_url,linkAnchorText = "PubMed Central Full Text Link",rank="1"):
    """
    Given a full text URL, create a web page entity with the full text URL and the given label
    """
    if full_text_url == None:
        return None
    full_text_url_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{full_text_url_uri}}">
        <rdf:type rdf:resource="http://www.w3.org/2002/07/owl#Thing"/>
        <rdf:type rdf:resource="http://vivoweb.org/ontology/core#URLLink"/>
        <rdf:type rdf:resource="http://vivo.ufl.edu/ontology/vivo-ufl/FullTextURL"/>
        <vivo:linkURI rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">{{full_text_url}}</vivo:linkURI>

        <vivo:rank rdf:datatype="http://www.w3.org/2001/XMLSchema#int">{{rank}}</vivo:rank>
        <vivo:linkAnchorText rdf:datatype="http://www.w3.org/2001/XMLSchema#anyURI">{{linkAnchorText}}</vivo:linkAnchorText>
        <ufVivo:harvestedBy>Python PubMed version 1.0</ufVivo:harvestedBy>
        <ufVivo:dateHarvested>{{harvest_datetime}}</ufVivo:dateHarvested>
    </rdf:Description>""")
    full_text_url_uri = vivotools.get_vivo_uri()
    harvest_datetime = vivotools.make_harvest_datetime()
    rdf = full_text_url_rdf_template.substitute(full_text_url_uri=full_text_url_uri,
                                            full_text_url=full_text_url,
                                            resource_uri=resource_uri,
                                            rank=rank,
                                            linkAnchorText=linkAnchorText,
                                            harvest_datetime=harvest_datetime)
    return [rdf,full_text_url_uri]

def assert_full_text_url_uri(paper_uri,full_text_url_uri):
    """
    Given the URI of a paper in VIVO, and the URI of an entity describing the full text link
    of the paper, return rdf to assert that the paper has the web page and vice versa
    """
    if full_text_url_uri == "":
        return ""
    full_text_url_uri_rdf_template = tempita.Template("""
    <rdf:Description rdf:about="{{paper_uri}}">
        <vivo:webpage rdf:resource="{{full_text_url_uri}}"/>
    </rdf:Description>
    <rdf:Description rdf:about="{{full_text_url_uri}}">
        <vivo:webpageOf rdf:resource="{{paper_uri}}"/>
    </rdf:Description>""")
    rdf = full_text_url_uri_rdf_template.substitute(paper_uri=paper_uri,full_text_url_uri=full_text_url_uri)
    return rdf

def pubmed_update_report():
    return None
#
#  Start Here
#

srdf = """
<-- Subtraction RDF -->
<rdf:RDF
  xmlns:rdf    = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs   = "http://www.w3.org/2000/01/rdf-schema#"
  xmlns:foaf   = "http://xmlns.com/foaf/0.1/"
  xmlns:owl    = "http://www.w3.org/2002/07/owl#"
  xmlns:ufVivo = "http://vivo.ufl.edu/ontology/vivo-ufl/"
  xmlns:bibo   = "http://purl.org/ontology/bibo/"
  xmlns:vivo   = "http://vivoweb.org/ontology/core#">"""

ardf = """
<-- Addition RDF -->
<rdf:RDF
  xmlns:rdf    = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs   = "http://www.w3.org/2000/01/rdf-schema#"
  xmlns:foaf   = "http://xmlns.com/foaf/0.1/"
  xmlns:owl    = "http://www.w3.org/2002/07/owl#"
  xmlns:ufVivo = "http://vivo.ufl.edu/ontology/vivo-ufl/"
  xmlns:bibo   = "http://purl.org/ontology/bibo/"
  xmlns:vivo   = "http://vivoweb.org/ontology/core#">"""

rdf_footer = """
</rdf:RDF>"""

print "Making doi dictionary"
doi_dictionary = vivotools.make_doi_dictionary()
print "Dictionary has ",len(doi_dictionary),"entries"

i = 0
for doi in doi_dictionary.keys():
    i = i + 1
    # do 50 papers in the specified range
    if i < 1000:
        continue
    if i > 1050:
        break
    paper_uri = doi_dictionary[doi]
    [vivo_pmid,vivo_pmcid,vivo_grants_cited,vivo_full_text_url,vivo_full_text_url_uri] = vivotools.get_pubmed_values_from_vivo(paper_uri)
    [pubmed_pmid,pubmed_pmcid,pubmed_grants_cited,pubmed_full_text_url] = vivotools.get_pubmed_values_from_pubmed(doi)
    if pubmed_pmid == None:
        print i,doi,"not found"
        continue # doi not found in pubmed, continue to next paper
    #
    if vivo_pmid == None:
        ardf = ardf + assert_pmid(paper_uri,pubmed_pmid)
    elif vivo_pmid != pubmed_pmid:
        srdf = srdf + assert_pmid(paper_uri,vivo_pmid)
        ardf = ardf + assert_pmid(paper_uri,pubmed_pmid)
    #
    if vivo_pmcid == None:
        ardf = ardf + assert_pmcid(paper_uri,pubmed_pmcid)
    elif vivo_pcmid != pubmed_pmcid:
        srdf = srdf + assert_pmcid(paper_uri,vivo_pmcid)
        ardf = ardf + assert_pmcid(paper_uri,pubmed_pmcid)
    #
    if vivo_grants_cited == None:
        ardf = ardf + assert_grants_cited(paper_uri,pubmed_grants_cited)
    elif vivo_grants_cited != pubmed_grants_cited:
        srdf = srdf + assert_grants_cited(paper_uri,vivo_grants_cited)
        ardf = ardf + assert_grants_cited(paper_uri,pubmed_grants_cited)
    #
    #   Always assert the pubmed web page.  a separate clean-up process will need
    #   to periodically query web pages, find and remove web pages that no other
    #   objects have as subjects or predicates
    #
    wrdf = ""
    pubmed_full_text_url_uri = ""
    if pubmed_full_text_url != None:
        [wrdf,pubmed_full_text_url_uri] = make_full_text_url_rdf(pubmed_full_text_url)
        ardf = ardf + wrdf
    #
    if vivo_full_text_url == None:
        ardf = ardf + assert_full_text_url_uri(paper_uri,pubmed_full_text_url_uri)
    elif vivo_full_text_url != pubmed_full_text_url:
        srdf = srdf + assert_full_text_url_uri(paper_uri,vivo_full_text_url_uri)
        ardf = ardf + assert_full_text_url_uri(paper_uri,pubmed_full_text_url_uri)
    #
    print i,doi,"pmid",vivo_pmid,":",pubmed_pmid,"pmcid",vivo_pmcid,":",pubmed_pmcid,"Grants cited",vivo_grants_cited,":",pubmed_grants_cited,"Full text url",vivo_full_text_url,":",pubmed_full_text_url
print srdf,"\n",rdf_footer
print ardf,"\n",rdf_footer
pubmed_update_report()
