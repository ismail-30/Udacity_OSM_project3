import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# Scrip to audit street names, based on Udacity tutorial
osm_filename = "bristol_map.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Causeway", "CLose", "Crescent", "Grove", "Way", "Terrace", "Walk", "View",
            "Park", "Parade", "Mews", "Hill", "Gardens", "East", "West", "South", "North", "Croft", "Close", "Approach",
            "Gate", "Mead", "Wharf", "Yard", "Steps", "Quay", "Commons", "Cottages", "Buildings", "Barton", "Row"]

# Corrections to be made on street names
# This list have been created once OSM has been audited and unusual street names have been collected
mapping = {"St": "Street",
           "St.": "Street",
           "Crescentq": "Crescent",
           "Courtq": "Court",
           "A": "Southmead Road",
           "B": "Southmead Road",
           "C": "Southmead Road",
           "D": "Southmead Road",
           "E": "Southmead Road",
           "F": "Southmead Road",
           "street": "Street",
           "hill": "Hill",
           "Steppingstones": "Stepping Stones"
           }


# Function to check if a street name is as expected, otherwise the value is stored in a dictionary
def audit_street_type(street_types, street_name):
    """
       collects the last words in the "street_name" strings, if they are not
       within the expected list, then stores them
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


# Function to ascertain whether an element key is effectively a street name
def is_street_name(elem):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return elem.attrib['k'] == "addr:street"


# Function added because it was observed that some street names consists only of a single letter "A" to "F"
# This Function locates which element in the OSM file has a letter in the street name
def is_street_name_letter(elem, letter):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return elem.attrib['k'] == "addr:street" and elem.attrib['v'] == letter


# Function to audit street names in the OSM file then collect and store unusual street names in a dictionary
def audit_street_name(osmfile):
    """
        returns me a dictionary that match the above function conditions
    """
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


# Function to update street names following the mapping in a dictionary
def update_street_name(name, mapping):
    """takes an old name to mapping dictionary, and update to a new one"""

    m = street_type_re.search(name)
    if m:
        for a in mapping:
            if a == m.group():
                name = re.sub(street_type_re, mapping[a], name)
                if "west" in name:
                    name = name.replace("west", "West")
    if "Annes" in name:
        name = name.split(',')[0]
    if "UK" in name:
        name = name.split(',')[0][3:]  # Remove digit, to keep only street name in "15 Douglas Road"
    return name


# Function to retrieves additional information stored in tags adjacent to a given street name tag
# This helps to get more insight about a given street name, such as, postal code, type of building, etc
def check_street_details(osmfile, letter):
    osm_file = open(osmfile, "r")
    tags = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name_letter(tag, letter):
                    for t in elem.iter("tag"):
                        tags[t.attrib['k']] = t.attrib['v']
    osm_file.close()

    return tags


if __name__ == "__main__":
    street_types = audit_street_name(osm_filename)
    pprint.pprint(street_types)
    # for letter in ["A", "B", "C", "D", "E", "F"]:
    #     tags = check_street_details(osm_filename, letter)
    #     pprint.pprint(tags)
    # name1 = update_street_name('Hope Chapel hill', mapping)
    # name2 = update_street_name('west street', mapping)
    # name3 = update_street_name('15 Douglas Road, Bristol, BS15 8NH, UK', mapping)
    # print(name1)
    # print(name2)
    # print(name3)
