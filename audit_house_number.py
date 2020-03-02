import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# We are following the same procedure as in the audit_street_names.py
# script, but this time we will audit and update house numbers.
osm_filename = "bristol_map.osm"
house_num1_re = re.compile(r'\d+\w?$', re.IGNORECASE)
house_num2_re = re.compile(r'\d+\w?-\d+\w?$', re.IGNORECASE)


# Function to check whether an element of XML is effectively a house number
def is_house_number(elem):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return elem.attrib['k'] == "addr:housenumber"


# Function to verify and collect weird/unacceptable house number (acceptable house number is defined by regex function)
def audit_house_number(house_numbers, house_number):
    """Build set of unexpected post codes.
    Args:
        post_codes (set): unexpected post codes.
        post_code (str): post code data.
    """
    m1 = house_num1_re.match(house_number)
    m2 = house_num2_re.match(house_number)

    if not (m1 or m2):
        house_numbers.add(house_number)


# Function to audit then collect weird house numbers, which calls the audit_house_number function
def audit_house_numbers(osmfile):
    """
        returns me a dictionary that match the above function conditions
    """
    osm_file = open(osmfile, "r")
    house_numbers = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_house_number(tag):
                    audit_house_number(house_numbers, tag.attrib['v'])
    osm_file.close()
    return house_numbers


# Checks whether a given house number is matched in a given XML element
def is_house_number_matched(elem, number):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return elem.attrib['k'] == "addr:housenumber" and elem.attrib['v'] == number


# Function which retrieves additional information stored in tags adjacent to a given house number tag
# This helps to get more insight about a given house number, such as, postal code, type of building, etc
def check_house_details(osmfile, number):
    osm_file = open(osmfile, "r")
    tags = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_house_number_matched(tag, number):
                    for t in elem.iter("tag"):
                        tags[t.attrib['k']] = t.attrib['v']
    osm_file.close()

    return tags


# Function to correct unusual house numbers, which have been spotted during data auditing
def update_house_number(number):
    """takes an old name to mapping dictionary, and update to a new one"""
    number = number.strip()
    number = number.replace(" ", "")
    number_temp = number.split(";")

    if len(number_temp) == 2:
        number = number.replace(";", "-")
        number = number.upper() # Change number from 23a to 23A

    # Transform  case "9A-C" to "9A-9C"
    number_temp = number.split("-")
    if len(number_temp) == 2:
        if not number_temp[1].isdigit():
            number = number_temp[0] + '-' + number_temp[0][0] + number_temp[1]

    # Transform "1 to 4" to "1-4"
    number_temp = number.split("to")
    if len(number_temp) == 2:
        number = number_temp[0] + '-' + number_temp[1]

    # Transform "284--288" to "284-288"
    number_temp = number.split("--")
    if len(number_temp) == 2:
        number = number_temp[0] + '-' + number_temp[1]
    return number


if __name__ == "__main__":
    house_numbers = audit_house_numbers(osm_filename)
    pprint.pprint(house_numbers)
    # for number in house_numbers:
    #     tags = check_house_details(osm_filename, '60 The General')
    #     pprint.pprint(tags)
    # n = update_house_number('284--288')
    # print(n)
