from vivotools import get_pubmed_values_from_pubmed
#
#  Test cases
#

print get_pubmed_values_from_pubmed("10.1111/j.1752-8062.2011.00348.x")
print get_pubmed_values_from_pubmed("10.1016/j.arcmed.2006.09.002")
print get_pubmed_values_from_pubmed("unfindable")
print get_pubmed_values_from_pubmed("10.1111/j.1365-2036.2010.04512.x")
