import xml.etree.cElementTree as ET
import pprint
import re
from collections import defaultdict

# We are following the same procedure as in the audit_street_names.py
# script, but this time we will audit and update postal codes.
osm_filename = 'bristol_map.osm'

# Regular expression to look for postal code in-line with UK formatting
# Sourced from https://gist.github.com/simonwhitaker/5748487
post_code_re = re.compile('^[A-Z]{1,2}[0-9]{1,2}[A-Z]? [0-9][A-Z]{2}$')

# Once post code data audited, unusual values have been mapped to correct values in the following dictionary
mapping = {"BS4 1104": "BS4",
           "BS1 3PH;BS1 3PJ": "BS1 3PJ",
           "BS5 0SA;BS5 0RX;BS5 0RZ": "BS5 0RX",
           "BS5 0UE;BS5 0UP": "BS5 0UP",
           "BS7 9DE;BS7 9DB;BS7 9DA": "BS7 9DA"
           }


# Function to check whether an element in XMl data is effectively a post code
def is_post_code(elem):
    """check if elem is a postcode"""
    return elem.attrib['k'] == "addr:postcode" or elem.attrib['k'] == "postal_code"


# Function to check then collect weird post code formats, for a given post code
def audit_post_code(post_codes, post_code):
    """Build set of unexpected post codes.
    Args:
        post_codes (set): unexpected post codes.
        post_code (str): post code data.
    """
    m = post_code_re.match(post_code)
    if not m:
        post_codes.add(post_code)


# Function to check then collect weird post codes in the osm_file, which calls audit_post_code
def audit_post_codes(osmfile):
    """
        returns me a dictionary that match the above function conditions
    """
    osm_file = open(osmfile, "r")
    post_codes = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_post_code(tag):
                    audit_post_code(post_codes, tag.attrib['v'])
    osm_file.close()
    return post_codes


# Function to check whether an XML element value matches a given post code
def is_postcode_matched(elem, post_code):
    """
    """
    return is_post_code(elem) and elem.attrib['v'] == post_code


# Function to retrieves additional information stored in tags adjacent to a given post code tag
# This helps to get more insight about a given post code, such as, street name, house number, etc
def check_postcode_details(osmfile, post_code):
    osm_file = open(osmfile, "r")
    tags = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode_matched(tag, post_code):
                    for t in elem.iter("tag"):
                        tags[t.attrib['k']] = t.attrib['v']
    osm_file.close()

    return tags


# Function to update post code
def update_post_code(post_code, mapping):
    """takes an old name to mapping dictionary, and update to a new one"""
    for a in mapping:
        if post_code == a:
            post_code = mapping[a]
    post_code_temp = post_code.split(";")
    if not post_code_temp[0][-1].isdigit():
        post_code = post_code_temp[0]
    return post_code


if __name__ == "__main__":
    post_codes = audit_post_codes(osm_filename)
    pprint.pprint(post_codes)
    #
    # tags = check_postcode_details(osm_filename, 'BS7 9DE;BS7 9DB;BS7 9DA')
    # pprint.pprint(tags)
    # 'BS10; BS9'
    # 'BS3 1SH;BS3 1SJ;BS3 1SL;BS3 1SQ'
    # p = update_post_code("BS4 1104")
    # print(p)