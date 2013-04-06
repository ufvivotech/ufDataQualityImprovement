# VIVO URI tester
# usage: python uritester.py (integer) > outputfile
# specify the number of URIs desired in (integer), and write to outputfile

import vivotools
print vivotools.get_vivo_uri()
print vivotools.get_vivo_uri()

query="""
#search on last, first initial, middle initial
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
FILTER (regex(?fname, "^D", "i"))
FILTER (regex(?lname, "Nelson", "i"))
}"""
result = vivotools.vivo_sparql_query(query)
print result
