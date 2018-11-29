#!/usr/bin/python
from __future__ import unicode_literals
import codecs
import xml.etree.ElementTree as ET
import argparse

arg_parser = argparse.ArgumentParser(
    description='Converts jira xml to DOT graph of blockers')
arg_parser.add_argument(
    'jira_xml', help='XML File exported from JIRA issue search')
parsed_args = arg_parser.parse_args()


def get_root():
    with codecs.open(parsed_args.jira_xml, 'r', 'utf-8') as xmlfile:
        # create element tree object
        tree = ET.parse(xmlfile)
        # get root element
        root = tree.getroot()
        return root

root = get_root()

out_file = '{}.gv'.format(parsed_args.jira_xml)

with codecs.open(out_file, 'w', 'utf-8') as out:
    def wl(string):
        out.write(string + '\n')

    def wl_indented(string):
        wl('    {}'.format(string))

    query_link = root.find('./channel/link').text

    header = """digraph g {{
    /* splines=ortho; */
    label="Dependency Graph for {}"
    rankdir=LR;
    nodesep=0.75;
    node[shape = record];
    """.format(query_link)
    wl(header)

    for item in root.findall('./channel/item'):
        summary = item.find('./summary').text.replace('"', '\\"')
        key = item.find('./key').text

        priority = item.find('./priority')
        priority = priority.text if priority is not None else "N/A"

        name = '"{}" [label="{}|{}|{}"];'.format(
            key, key, priority, summary)

        wl_indented(name)

        outwardlinks = item.find(
            "./issuelinks/issuelinktype[name='Blocks']/outwardlinks")
        if outwardlinks is not None:
            blockers = outwardlinks.findall('./issuelink/issuekey')
            for blocker in blockers:
                wl_indented('"{}" -> "{}"'.format(key, blocker.text))

    wl("}")
