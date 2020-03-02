import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import schema
import cerberus
from audit_street_name import update_street_name
from audit_postal_code import update_post_code
from audit_house_number import update_house_number
from audit_amenities import update_amenity
from collections import defaultdict

# Script taken from UDacity tutorial, function shape_element has been modified to update names for: Street, postal code,
# house numbers and amenities
OSM_PATH = "bristol_map.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


# Corrections to be made on street names
street_mapping = {"St": "Street",
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

# Corrections to be made to amenities
amenity_mapping = {
    "court_yard": "courtyard",
    "grave_yard": "graveyard",
    "stripclub": "strip_club",
}

# Corrections to be made to post codes
pc_mapping = {"BS4 1104": "BS4",
           "BS1 3PH;BS1 3PJ": "BS1 3PJ",
           "BS5 0SA;BS5 0RX;BS5 0RZ": "BS5 0RX",
           "BS5 0UE;BS5 0UP": "BS5 0UP",
           "BS7 9DE;BS7 9DB;BS7 9DA": "BS7 9DA"
           }

# Make sure the fields order in the csvs matches the column order in the
# sql table schema
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        # 1st level
        for i in node_attr_fields:
            node_attribs[i] = element.attrib[i]
        # 2nd level
        for tag in element.iter("tag"):
            problem = problem_chars.search(tag.attrib['k'])
            if not problem:
                node_tag = {}
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = update_amenity(tag.attrib['v'], amenity_mapping) if tag.attrib['k'] == "amenity" else tag.attrib['v']

                match = LOWER_COLON.search(tag.attrib['k'])
                if not match:
                    node_tag['type'] = 'regular'
                    node_tag['key'] = tag.attrib['k']
                else:
                    bef_colon = re.findall('^(.+):', tag.attrib['k'])
                    aft_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])
                    node_tag['type'] = bef_colon[0]
                    node_tag['key'] = aft_colon[0]
                    if node_tag['type'] == "addr" and node_tag['key'] == "street":
                        # update street name
                        node_tag['value'] = update_street_name(tag.attrib['v'], street_mapping)
                    elif node_tag['type'] == "addr" and node_tag['key'] == "postcode":
                        # update post code
                        node_tag['value'] = update_post_code(tag.attrib['v'], pc_mapping)
                    elif node_tag['type'] == "addr" and node_tag['key'] == "housenumber":
                        # update house number
                        node_tag['value'] = update_house_number(tag.attrib['v'])
            tags.append(node_tag)

        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i] = element.attrib[i]
        for tag in element.iter("tag"):
            problem = PROBLEMCHARS.search(tag.attrib['k'])
            if not problem:
                way_tag = {}
                way_tag['id'] = element.attrib['id']
                way_tag['value'] = update_amenity(tag.attrib['v'], amenity_mapping) if tag.attrib['k'] == "amenity" else tag.attrib['v']
                match = LOWER_COLON.search(tag.attrib['k'])
                if not match:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = tag.attrib['k']
                else:
                    bef_colon = re.findall('^(.+?):+[a-z]', tag.attrib['k'])
                    aft_colon = re.findall('^[a-z|_]+:(.+)', tag.attrib['k'])

                    way_tag['type'] = bef_colon[0]
                    way_tag['key'] = aft_colon[0]
                    if way_tag['type'] == "addr" and way_tag['key'] == "street":
                        way_tag['value'] = update_street_name(tag.attrib['v'], street_mapping)
                    elif way_tag['type'] == "addr" and way_tag['key'] == "postcode":
                        way_tag['value'] = update_post_code(tag.attrib['v'], pc_mapping)
                    elif way_tag['type'] == "addr" and way_tag['key'] == "housenumber":
                        # update house number
                        way_tag['value'] = update_house_number(tag.attrib['v'])
            tags.append(way_tag)
        position = 0
        for tag in element.iter("nd"):
            nd = {}
            nd['id'] = element.attrib['id']
            nd['node_id'] = tag.attrib['ref']
            nd['position'] = position
            position += 1

            way_nodes.append(nd)

        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'w') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)
