#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 26 12:32:08 2017

@author: gliar
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
OSMFILE = "/Users/gliar/Documents/Python Stuff/chicago_illinois.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Rd.": "Road",
            }


def count_tags(filename):
    dict_tagscount = {}
    for event, elem in ET.iterparse(filename):
        try:
            if type(dict_tagscount[elem.tag]) == type(int()):
                dict_tagscount[elem.tag] += 1
        except:
            dict_tagscount[elem.tag] = 1
    return dict_tagscount

def key_type(element, keys):
    if element.tag == "tag":
        tag_k_attrib = element.attrib['k']
        if (lower.search(tag_k_attrib)):
            keys["lower"] += 1
        elif (lower_colon.search(tag_k_attrib)):
            keys["lower_colon"] += 1
        elif (problemchars.search(tag_k_attrib)):
            keys["problemchars"] += 1
        else:
            keys["other"] += 1
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


def update_name(name, mapping):
    m = street_type_re.search(name)
    street_type = m.group()
    new_street_type = mapping[street_type]
    better_name = name[:-len(street_type)]
    better_name = better_name+new_street_type
    # YOUR CODE HERE

    return better_name

def shape_element(element):
    node = {}
    created_dict={}
    node_refs = []
    address_dict={}
    if element.tag == "node" or element.tag == "way" :
        node["id"] = element.attrib["id"]
        node["type"] = element.tag
        try:
            node["visible"] = element.attrib["visible"]
        except:
            pass
        for item in CREATED:
            created_dict[item] = element.attrib[item]
        node["created"] = created_dict
        try:
            lat = float(element.attrib["lat"])
            lon = float(element.attrib["lon"])
            node["pos"] = [lat, lon]
        except:
            for node_ref in element.iter("nd"):
                node_refs.append(node_ref.attrib["ref"])
            node["node_refs"] = node_refs
        for tag in element.iter("tag"):
            tag_k_list = tag.attrib['k'].split(':')
            if (len(tag_k_list) == 3):
                pass
            elif (len(tag_k_list) == 2 ) and (tag_k_list[0] == 'addr'):
                address_dict[tag_k_list[1]] = tag.attrib['v']
            elif (len(tag_k_list) == 2 ):
                node[tag_k_list[0]+'_'+tag_k_list[1]] = tag.attrib['v']
            elif (len(tag_k_list) == 1 ):
                node[tag.attrib['k']] = tag.attrib['v']
        if address_dict:
            node["address"] = address_dict
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

if False:
    tags = count_tags(OSMFILE)
    pprint.pprint(tags)
    keys = process_map(OSMFILE)
    pprint.pprint(keys)
    st_types = audit(OSMFILE)
    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
    data = process_map(OSMFILE, False)

