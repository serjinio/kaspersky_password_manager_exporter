"""
Script to migrate txt export of Kaspersky password manager key vault to KeePass format.

Usage: Export your passwords from Kaspersky password manger and run this script 
to produce CSVs compatible for importing into the KeePass (general CSV import).
"""

import csv
import logging
from dataclasses import dataclass, asdict
from typing import Any, List

import click
import pyparsing as pp

logging.basicConfig(level=logging.INFO)

pp.ParserElement.setDefaultWhitespaceChars(" \t")
NL = pp.LineEnd()


@dataclass
class Field:
    name: str
    value: str


@dataclass
class Credential:
    name: str
    fields: List[Field]


@dataclass
class Section:
    name: str
    credentials: List[Credential]


def concat_words(string, loc, toks):
    return " ".join(toks).strip()


def concat_value(string, loc, toks):
    return " ".join(toks.asList()).strip()


def make_section(string, loc, toks):
    return Section(name=toks[0], credentials=toks[1:])


def make_credential(string, loc, toks):
    return Credential(name=toks[0].value.strip(), fields=toks)


def make_field(string, loc, toks):
    return Field(name=toks[0], value=toks[1])


value = (
    pp.ZeroOrMore(pp.Word(pp.alphas)).setParseAction(concat_words)
    + pp.Literal(":").suppress()
    + pp.rest_of_line.setParseAction(concat_value)
    + NL.suppress()
).setParseAction(make_field)

value_group_sep = (pp.ZeroOrMore(NL) + pp.Literal("---") + pp.ZeroOrMore(NL)).suppress()
values_group = (
    pp.ZeroOrMore(NL).suppress()
    + pp.ZeroOrMore(value).addParseAction(make_credential)
    + value_group_sep
)
creds_group = pp.ZeroOrMore(values_group)

section_name = pp.Word(pp.alphas) + NL.suppress()
section = (section_name + pp.ZeroOrMore(NL).suppress() + creds_group).setParseAction(
    make_section
)

creds_file = pp.ZeroOrMore(section)


KEEPASS_FIELD_MAPPING = {
    "Application": "Title",
    "Website name": "Title",
    "Login": "User Name",
    "Password": "Password",
    "Website URL": "URL",
    "Comment": "Notes",
}


@click.command()
@click.option(
    "--infile",
    help="Input filename from Kaspersky PM export",
)
def convert(infile):
    """Converts input Kaspersky PM export file to CSV format"""
    if infile is None:
        print("ERROR: Input file must be provided. Use --help for more info.")
        return
    logging.info("Will convert input file: %s...", infile)
    cred_records = open(infile, "rt").read()
    parsed_records: List[Section] = creds_file.parse_string(cred_records)
    for el in parsed_records:
        print(el)
    for section in parsed_records:
        if not section.credentials:
            continue
        with open(section.name + ".csv", "w", newline="") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                delimiter="\t",
                fieldnames=[
                    KEEPASS_FIELD_MAPPING[f.name]
                    for f in section.credentials[0].fields
                    if f.name != "Login name"
                ],
            )
            writer.writeheader()
            for cred in section.credentials:
                writer.writerow(
                    {
                        str(KEEPASS_FIELD_MAPPING[f.name]).strip(): str(f.value).strip()
                        for f in cred.fields
                        if f.name != "Login name"
                    }
                )


if __name__ == "__main__":
    convert()
