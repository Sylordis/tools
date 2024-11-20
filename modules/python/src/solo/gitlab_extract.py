#!/usr/bin/env python3

# This small program allows to export issues from a Gitlab project using the Gitlab API.
# You can then export it in a specific format.
# Run this script with --help for full help.
# Python dependencies to install (pip install <dependency>):
# - requests

import argparse
import csv
from dataclasses import dataclass
from enum import StrEnum
import json
import logging
from pathlib import Path
from requests import Response
import requests
import sys
from typing import Any


class ArgParser:
    """
    Class to organise and setup the different options for the software.
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=Path(__file__).name, description="Gets issues from Gitlab and can output them."
        )
        self.parser.add_argument("url",
            help="Gitlab API URL (example: https://gitlab-example.com/api/v4).")
        self.parser.add_argument("project_id",
            help="Project ID you want to extract from.")
        self.parser.add_argument("issues_id", nargs="+", help="Issues IDs to import from the project.")
        self.parser.add_argument("-l", "--log",
            help="Sets the log level.", default="info", metavar="LEVEL", dest="loglevel", choices=["debug", "info", "warning", "error"],
        )
        self.parser.add_argument("--debug",
            help="Sets debug mode (equivalent to '--log debug').", action="store_const", dest="loglevel", const="debug",
        )
        self.parser.add_argument("-t", "--token", help="Gitlab token or path to a file containing it (need at least 'read_api' authorization).")
        self.parser.add_argument("-o", "--output", help="Output file. If not provided, software outputs the JSON response.")
        self.parser.add_argument("-f", "--fields",
            help="JSON fields to get for each issue, comma separated value.\nIdentifiers work as: 'field1.subfield2.subfield3' for example.")

    def parse(self):
        return self.parser.parse_args()


@dataclass
class GitlabAuthentifier:
    """
    Holds Gitlab authentication method. It can either hold the token or the path to a file containing it.

    Attributes
    ---
    token: str | None
        Gitlab token or path to a file containing it.
    """

    token: str | None = None
    "Gitlab token or path to a file containing it."

    def get_token(self) -> str | None:
        """
        Gets the token to be used by either reading a file with the token or the output the token itself.

        :return: the gitlab token
        """
        token = self.token
        if Path(token).exists():
            with open(Path(self.token), "r", encoding="utf-8", newline="\n") as file:
                token = file.readline().strip('\n')
        return token


class GitlabIssuesImporter:
    """
    Imports issues from a Gitlab's project with a POST request.

    Attributes
    ---
    auth: GitlabAuthentifier
        Authentification for Gitlab.
    issue_ids: list[int]
        List of issues to import.
    project: int
        Gitlab project ID to import the issues from.
    url: str
        Gitlab API URL.
    """

    def __init__(self, url:str, project: int, ids: list[int], auth: GitlabAuthentifier = None):
        self.auth = auth
        "Authentification for Gitlab."
        self.issue_ids = ids
        "List of issues to import."
        self.project = project
        "Gitlab project ID to import the issues from."
        self.url = url
        "Gitlab API URL."
        self._log = logging.getLogger(self.__class__.__name__)
        "Class logger."

    def import_issues(self) -> Response:
        """
        Proceeds on doing the POST request. Raises an exception in case of a status code not "OK" (a.k.a. 200).

        :return: the POST request response.
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        if self.auth.token is not None:
            headers["PRIVATE-TOKEN"] = f"{self.auth.get_token()}"

        data = ["scope=all"]
        data += [f"iids[]={id}" for id in self.issue_ids]
        data = "&".join(data)

        response = requests.get(f"{self.url}/projects/{self.project}/issues", headers=headers, data=data, verify=False)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
        return response


class DataExporter():
    "Interface for data exporters."

    def configure_exporter(self, **kwargs):
        """
        Call this method to update the current exporter's dictionary.

        :param kwargs: Dictionary to update values.
        """
        # Redefine this method if needed
        self.__dict__.update(kwargs)

    def export(self, output: Path, data: Response):
        """
        Exports the provided data to the output file in the requested format.

        :param output: path to the output file.
        :param data: data returned by the post request.
        """
        # Redefine this method
        pass


class CSVExporter(DataExporter):
    """
    Exporter for CSV files.

    Attributes
    ---
    fields: list[str] | None
        JSON fields to get the value from for each item.
    """

    def __init__(self):
        self.fields: list[str] | None = None
        "JSON fields to get the value from for each item."
        self._log = logging.getLogger(self.__class__.__name__)
        "Class logger."

    def configure_exporter(self, **kwargs):
        if "fields" in kwargs:
            self.fields = kwargs.get("fields").split(",")

    def export(self, output: Path, data: Response):
        with open(output, "w", newline='') as target:
            writer = csv.writer(target)
            writer.writerow(self.fields)
            for item in data.json():
                row = [self.get_value_from_key(field, item) for field in self.fields]
                writer.writerow(row)

    def get_value_from_key(self, key:str, json_data) -> Any:
        """
        Gets a value from json data based on a possible nested key.
        For example, a key "a.b.c" will retrieve the value of the key "c" nested in "b" nested in "a".

        ```json
        {
            "a":
                {
                    "a": "hello"
                    "b":
                    {
                        "b": "foo"
                        "c": "bar"
                    }
                }
        }
        ```
        With previous example it would return "bar".

        :param key: the path to the desired value.
        :param json_data: the json data to find the value in.
        :return: the value of the series of keys, None if it could not be found.
        """
        keys = key.split(".")
        it = iter(keys)
        item = json_data
        while (x := next(it, None)) is not None and item is not None:
            item = item.get(x, None)
        return item


class JSONExporter(DataExporter):
    "Exporter for JSON format."

    def export(self, output: Path, data: Response):
        with open(output, "w") as target:
            json.dump(data.json(), target)


class ExporterFactory():
    "Factory to get the correct exporter according to file extension."

    def __init__(self):
        self._exporters: dict[str, Any] = {
            "csv": CSVExporter,
            "json": JSONExporter,
        }
        self._log = logging.getLogger(self.__class__.__name__)

    def get_exporter(self, target: Path) -> DataExporter | None:
        """
        Gets an exporter according to the extension of the target if it is configured.

        :param target: path to target file.
        :out: an instanciated exporter or None if none could be found.
        """
        exporter = None
        extension = target.suffix[1:].lower()
        if extension in self._exporters:
            exporter_class = self._exporters.get(extension)
            if exporter_class is not None:
                exporter = exporter_class()
        if exporter is None:
            self._log.error(f"Could not find exporter for extension '{extension}', only possible: {list(self._exporters.keys())} (or implement it yourself).")
        return exporter


def main():
    args = ArgParser().parse()
    logging.basicConfig(level=getattr(logging, args.loglevel.upper(), None))
    logger = logging.getLogger(__name__)
    auth = None
    if args.token:
        auth = GitlabAuthentifier(args.token)
    try:
        importer = GitlabIssuesImporter(args.url, args.project_id, args.issues_id, auth)
        response = importer.import_issues()
        if args.output is not None:
            target = Path(args.output)
            exporter = ExporterFactory().get_exporter(target)
            if exporter is not None:
                exporter.configure_exporter(**vars(args))
                exporter.export(target, response)
                logger.info(f"Target file written {target.resolve()}")
        else:
            json.dump(response.json(), sys.stdout)
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    main()
