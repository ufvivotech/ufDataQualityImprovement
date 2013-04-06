import vivotools

#  Test cases for access and display functions

print "\nDateTime"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n7860108656"))
datetime_value = vivotools.get_datetime_value("http://vivo.ufl.edu/individual/n7860108656")
print datetime_value

print "\nDateTimeInterval"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n182882417"))
datetime_interval = vivotools.get_datetime_interval("http://vivo.ufl.edu/individual/n182882417")
print datetime_interval

print "\nOrganization"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n8763427"))
organization = vivotools.get_organization("http://vivo.ufl.edu/individual/n8763427")
print organization

print "\nAuthorship"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n148010391"))
authorship = vivotools.get_authorship("http://vivo.ufl.edu/individual/n148010391")
print authorship

print "\nRole"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n1864549239"))
role = vivotools.get_role("http://vivo.ufl.edu/individual/n1864549239")
print role

print "\nPerson"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n39051"))
person = vivotools.get_person("http://vivo.ufl.edu/individual/n39051",get_grants=True)
print person
for grant in person['grants']:
    print '\n',vivotools.string_from_grant(grant)

print "\nNot Found"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/notfound"))

print "\nPublication Venue"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n378789540"))
publication_venue = vivotools.get_publication_venue("http://vivo.ufl.edu/individual/n378789540")
print publication_venue

print "\nPaper"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n4703866415"))
pub = vivotools.get_publication("http://vivo.ufl.edu/individual/n4703866415")
print vivotools.string_from_document(pub)

print "\nGrant"
vivotools.show_triples(vivotools.get_triples("http://vivo.ufl.edu/individual/n614029206"))
grant = vivotools.get_grant("http://vivo.ufl.edu/individual/n614029206")
print grant
print vivotools.string_from_grant(grant)
