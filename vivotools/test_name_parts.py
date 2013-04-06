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

#
#  Test cases
#

print name_parts("Childs, Amy Baker")
print name_parts("Childs")
print name_parts("Childs, A.")
print name_parts("de Jesus, Mario A. E. P.")
print name_parts("Childs, Amy")
print name_parts("Childs, A. Baker")
print name_parts("Childs, A. B.")
print name_parts("Childs, Amy B.")
print name_parts("IFTC")
print name_parts("VIVO Collaboration")
print name_parts("The VIVO Collaboration")
print name_parts("Gonzalez-Rothi, Leslie")
print name_parts("de la Cruz, Emily")
