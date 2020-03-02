import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# We are following the same procedure as in the audit_street_names.py
# script, but this time we will audit and update amenities.

osm_filename = "bristol_map.osm"
amenity_re = re.compile(r'\S+(\s\S+)*')
amenities = defaultdict(set)

# Expected amenities
expected_amenities = ["ambulance_station", "arts_center", "atm", "bank", "bar",
                      "beauty salon", "bowling club", "bus_station", "cafe",
                      "car_rental", "casino", "cinema", "club", "club_house",
                      "college", "dentist", "doctors", "fast_food",
                      "fire_station", "fuel", "hospital", "nightclub", "park",
                      "pharmacy", "police", "post_office", "pub",
                      "restaurant", "school", "taxi", "telephone", "taxi",
                      "theatre", "university"]


# Function used to audit / collect unusual, not expected amenity
def audit_amenity(amenities, amenity_name):
    n = amenity_re.search(amenity_name)
    if n:
        amenity_found = n.group()
        if amenity_found not in expected_amenities:
            amenities[amenity_found].add(amenity_name)


# Function to ascertain whether an element in XML data is effectively an amenity
def is_amenity(elem):
    return elem.attrib['k'] == "amenity"


# Function to audit / collect unsual, unexpected amenities, which is calls upon audit_amenity function
def audit_amenities(osm_filename):
    osm_file = open(osm_filename, "r")
    amenities = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_amenity(tag):
                    audit_amenity(amenities, tag.attrib['v'])
    pprint.pprint(dict(amenities))


# After auditing the file for amenities, it appears only few have slight deviation
# These have been stored in the following dictionary and mapped to their correct substitute
amenity_mapping = {
    "court_yard": "courtyard",
    "grave_yard": "graveyard",
    "stripclub": "strip_club",
}


# Function used to update amenities, following mapping dictionary
def update_amenity(name, amenity_mapping):
    for amenity in amenity_mapping:
        if amenity in name:
            name = re.sub(r'\b' + re.escape(amenity), amenity_mapping[amenity], name)
    return name


# Function to ascertain whether an element value of XML data matches a given amenity
def is_amenity_matched(elem, amenity):
    """
        looks for tags that specify street names(k="addr:street")
    """
    return is_amenity(elem) and elem.attrib['v'] == amenity


# Function to retrieves additional information stored in tags adjacent to a given amenity tag
# This helps to get more insight about a given amenity, such as, postal code, type of building, etc
def check_amenity_details(osmfile, amenity):
    osm_file = open(osmfile, "r")
    tags = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_amenity_matched(tag, amenity):
                    for t in elem.iter("tag"):
                        tags[t.attrib['k']] = t.attrib['v']
    osm_file.close()

    return tags


if __name__ == '__main__':
    audit_amenities(osm_filename)
    # amn = check_amenity_details(osm_filename, "atm; telephone")
    # pprint.pprint(amn)
