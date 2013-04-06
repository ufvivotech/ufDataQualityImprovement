# Test tempita

import tempita


query=tempita.Template("""
#search on last, first initial, middle initial
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
{{if len(first) != 0:}}
FILTER (regex(?fname, "{{first}}", "i"))
{{endif}}
FILTER (regex(?lname, "{{last}}", "i"))
}""")

a = query.substitute(first="",last="Conlon")
print a
