"""Module for managing the JSON files"""
import json
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException

class JsonStore:
    """Class for providing the methods for managing the JSON files"""

    @staticmethod
    def read_json_file(file_path: str):
        """Reads a JSON file and returns its content as a list"""
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

    @staticmethod
    def write_json_file(file_path: str, data: list):
        """Writes a list of data to a JSON file"""
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                json.dump(data, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex
