#!/user/bin/env/python
"""
    repair-phone-numbers.py -- Replace poorly formatted phone numbers with
    improved formatted phone numbers

    At UF, phone numbers in VIVO come from a variety of sources.  Some come
    from the UF directory, which itself gathers from various sources, some are
    self-edited, while others are proxy edited.  VIVO supports an open-text
    box for phone numbers leading to a wide variety of inputs.

    This software repairs VIVO phone numbers as needed to comply with ITU
    recommended standards.  Resulting phone numbers
    will have one of the following formats:

    (xxx) xxx-xxxx ext. xxxx where area code and/or extension are optional
    +xx xxx xxxx xx xxx      where spacing between number groups is according
                             to local stadards

    References
    International Telecommunications Union, Notation for national and
    international telephone numbers, e-mail addresses and web addresses
    http://www.itu.int/rec/T-REC-E.123-200102-I/en

    Madey, John Suncom Number Changes, March 21, 2008.
    http://www.admin.ufl.edu/ddd/default.asp?doc=13.9.2206.7

    All vivo:phoneNumber and vivo:phoneNumber values are considered and
    replaced as needed.

    Version 0.95 MC 2013-03-02
    --  Query VIVO, process phone numbers and replace as necessary

        To do:

        -- test deploy in staging
        -- move to production
        -- establish documented operational procedure

    Version 0.96 NR 2013-03-08
    --  modified to use a list of dictionaries to avoid overwriting entries with the same URI.
    --  tested on staging and applied to prod data.
    
"""

__author__      = "Michael Conlon"
__copyright__   = "Copyright 2013, University of Florida"
__license__     = "BSD 3-Clause license"

import tempita
import vivotools as vt

def make_phone_list(phone_list = [],debug=False):
    """
    Extract all phone numbers in VIVO and organize them into a list of dictionaries keyed by URI
    """
    query = tempita.Template("""
    SELECT ?uri ?phone ?primary
    WHERE {
    {?uri vivo:phoneNumber ?phone .} UNION {?uri vivo:primaryPhoneNumber ?primary .}
    }""")
    query = query.substitute()
    result = vt.vivo_sparql_query(query)
    try:
        count = len(result["results"]["bindings"])
    except:
        count = 0
    if debug:
        print query,count,
        result["results"]["bindings"][0],result["results"]["bindings"][1]
    #
    i = 0
    while i < count:
        b = result["results"]["bindings"][i]
        uri = b['uri']['value']
        dict = {}
        if 'phone' in b:
            dict['phone'] = b['phone']['value']
        if 'primary' in b:
            dict['primary'] = b['primary']['value']
        if dict != {}:
            dict['uri'] = uri
            phone_list.append(dict)
        i = i + 1    
    return phone_list


def repair_phone_number(phone,debug=False):
    """
    Given an arbitrary string that attempts to represent a phone number,
    return a best attempt to format the phone number according to ITU standards
    """
    phone_text = phone.encode('ascii','ignore') # encode to ascii
    phone_text = phone_text.lower()
    phone_text = phone_text.strip()
    extension_digits = None
    #
    # strip off US international country code
    #
    if phone_text.find('+1 ') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('+1-') == 0:
        phone_text = phone_text[3:]
    if phone_text.find('(1)') == 0:
        phone_text = phone_text[3:]
    digits = []
    for c in list(phone_text): 
        if c in ['0','1','2','3','4','5','6','7','8','9']:
            digits.append(c)
    if len(digits) > 10:
        # pull off the extension
        i = phone_text.rfind(' ') # last blank
        if i > 0:
            extension = phone_text[i+1:]
            extension_digits = []
            for c in list(extension): 
                if c in ['0','1','2','3','4','5','6','7','8','9']:
                    extension_digits.append(c)
            digits = [] # recalc the digits
            for c in list(phone_text[:i+1]): 
                if c in ['0','1','2','3','4','5','6','7','8','9']:
                    digits.append(c)
        elif phone_text.rfind('x')>0:
            i = phone_text.rfind('x')
            extension = phone_text[i+1:]
            extension_digits = []
            for c in list(extension): 
                if c in ['0','1','2','3','4','5','6','7','8','9']:
                    extension_digits.append(c)
            digits = [] # recalc the digits
            for c in list(phone_text[:i+1]): 
                if c in ['0','1','2','3','4','5','6','7','8','9']:
                    digits.append(c)
    if len(digits) == 7:
        updated_phone = '(352) ' + "".join(digits[0:3])+'-'+"".join(digits[3:7])
    elif len(digits) == 10:
        updated_phone = '('+"".join(digits[0:3])+') '+"".join(digits[3:6])+ \
            '-'+"".join(digits[6:10])
    elif len(digits) == 5 and digits[0] == '2': # UF special
        updated_phone = '(352) 392' + "".join(digits[1:5])
    elif len(digits) == 5 and digits[0] == '3': # another UF special
        updated_phone = '(352) 273' + "".join(digits[1:5])
    else:
        updated_phone = phone # no repair
        extension_digits = None
        if len(digits)>0:
            print "Unable to repair the following:"
    if extension_digits != None and len(extension_digits)>0:
        updated_phone = updated_phone+' ext. '+"".join(extension_digits)
    if debug:
        print phone.ljust(25),updated_phone.ljust(25)
    return updated_phone
#
#  Start here
#
print "Making phone list"
phone_list = make_phone_list(debug=True)
print "Phone list has ",len(phone_list)," entries."
ardf = vt.rdf_header()
srdf = vt.rdf_header()
i = 0
na = 0
ns = 0

while (len(phone_list) > 0):
    i = i + 1
    if i > 200000:
        break
    result = phone_list.pop()
    uri = result['uri']
    if 'phone' in result:
        updated_phone = repair_phone_number(result['phone'],debug=True)
        [add,sub] = vt.update_data_property(uri,'vivo:phoneNumber',
                                         result['phone'],updated_phone)
        ardf = ardf + add
        srdf = srdf + sub
    if 'primary' in result:
        updated_phone = repair_phone_number(result['primary'],debug=True)
        [add,sub] = vt.update_data_property(uri,'vivo:primaryPhoneNumber',
                                         result['primary'],updated_phone)
        if add != "":
            na = na + 1
        if sub != "":
            ns = ns + 1
        ardf = ardf + add
        srdf = srdf + sub
srdf = srdf + vt.rdf_footer()
ardf = ardf + vt.rdf_footer()
print "<!-- Addition RDF -->"
print ardf
print "<!-- Subtraction RDF -->"
print srdf
print "Number to add = ",na
print "Number to subtract = ",ns

        

                 

                 
