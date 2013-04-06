import json, vivotools

query = """
    SELECT ?x ?lname WHERE
    {
    ?x rdf:type foaf:Person .
    ?x foaf:lastName ?lname .
    FILTER (regex(?lname,"Conlon","i"))
    }
"""

print vivotools.get_vivo_uri()
print vivotools.get_vivo_uri()
data=vivotools.vivo_sparql_query(query)                                 # issue the query, return the data
print "Retrieved data:\n" + json.dumps(data, sort_keys=True, indent=4)  # show the returned json object
print "Items found = ",len(data["results"]["bindings"])                 # count the items in the result set
for item in data["results"]["bindings"]:                                # for each item, show the uri and last name
    print item["x"]["value"],item["lname"]["value"]

