import tempita
import vivotools

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

def case0(last,first,middle,debug):
    query = tempita.Template("""
#search on last name
SELECT ?x ?lname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:lastName ?lname .
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result


def case1(last,first,middle,debug):
    query = tempita.Template("""
#search on last name and first initial
SELECT ?x ?fname ?lname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result
    
def case2(last,first,middle,debug):
    query = tempita.Template("""
#search on first name and last name.
SELECT ?x ?fname ?lname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case3(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first initial, middle initial
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?mname, '''^{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case4(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first initial, middle name
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?mname, '''{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case5(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first, middle initial
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?mname, '''^{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case6(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first, middle name
SELECT ?x ?fname ?lname ?mname WHERE
{
?x rdf:type core:FacultyMember .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?mname, '''{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result    
    return result

def case01(last,first,middle,debug):
    query = tempita.Template("""
#search on last name
SELECT ?x ?lname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:lastName ?lname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result


def case11(last,first,middle,debug):
    query = tempita.Template("""
#search on last name and first initial
SELECT ?x ?fname ?lname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result
    
def case21(last,first,middle,debug):
    query = tempita.Template("""
#search on first name and last name.
SELECT ?x ?fname ?lname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case31(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first initial, middle initial
SELECT ?x ?fname ?lname ?mname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?mname, '''^{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case41(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first initial, middle name
SELECT ?x ?fname ?lname ?mname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''^{{first}}''', "i"))
FILTER (regex(?mname, '''{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case51(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first, middle initial
SELECT ?x ?fname ?lname ?mname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?mname, '''^{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result
    return result

def case61(last,first,middle,debug):
    query = tempita.Template("""
#search on last, first, middle name
SELECT ?x ?fname ?lname ?mname ?ufid WHERE
{
?x rdf:type foaf:Person .
?x foaf:firstName ?fname .
?x foaf:lastName ?lname .
?x core:middleName ?mname .
?x ufVivo:ufid ?ufid .
FILTER (regex(?fname, '''{{first}}''', "i"))
FILTER (regex(?mname, '''{{middle}}''', "i"))
FILTER (regex(?lname, '''{{last}}''', "i"))
}""")
    query = query.substitute(last=last,first=first,middle=middle)
    result = vivotools.vivo_sparql_query(query)
    if debug:
        print query,result    
    return result

def find_author(author,debug=False):
    """
    Given an author name, generate SPARQL to
    attempt to find a person with the specified name in VIVO.
    """
    [last,first,middle,case] = name_parts(author)
    sparql_function = {0:case0,1:case1,2:case2,3:case3,4:case4,5:case5,6:case6}
    result = sparql_function[case](last,first,middle,debug)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if count == 0:
        # try again
        sparql_function = {0:case01,1:case11,2:case21,3:case31,4:case41,5:case51,6:case61}
        result = sparql_function[case](last,first,middle,debug)
    return result


#
# Test cases
# 
print find_author('Conlon, M',debug=True)  # Single
print find_author('Johnson, J',debug=True) # Multiple 
print find_author('Rejack, N',debug=True)  # Zero in Faculty, will be found in staff
print find_author('Gargle, G',debug=True)  # Zero regardless of technique
