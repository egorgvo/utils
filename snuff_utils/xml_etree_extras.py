#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Module with CDATA implementation
Usage:
from snuff_utils.xml_etree_extras import ElementTree, CDATA
root = ElementTree.Element('Root')
tag = SubElement(ad, "Description")
cdata_raw = "<p>text</p>"
cdata = CDATA(cdata_raw)
tag.append(cdata)
"""

import xml.etree.ElementTree as ElementTree
from xml.etree.ElementTree import _escape_cdata


def CDATA(text=None):
    element = ElementTree.Element('![CDATA[')
    element.text = text
    return element


def _serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs):

    if elem.tag == '![CDATA[':
        write("\n<{}{}]]>\n".format(elem.tag, elem.text))
        if elem.tail:
            write(_escape_cdata(elem.tail))
    else:
        return ElementTree._original_serialize_xml(write, elem, qnames, namespaces,short_empty_elements, **kwargs)


ElementTree._original_serialize_xml = ElementTree._serialize_xml
ElementTree._serialize_xml = ElementTree._serialize['xml'] = _serialize_xml
