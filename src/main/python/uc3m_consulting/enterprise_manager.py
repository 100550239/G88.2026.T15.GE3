"""Module """
import re
import json

from datetime import datetime, timezone
from freezegun import freeze_time
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (PROJECTS_STORE_FILE,
                                                       TEST_DOCUMENTS_STORE_FILE,
                                                       TEST_NUMDOCS_STORE_FILE)
from uc3m_consulting.project_document import ProjectDocument

class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    @staticmethod
    def read_json_file(file_path: str):
        # reads a JSON file and returns its content as a list
        try:
            with open(file_path, "r", encoding="utf-8", newline="") as file:
                return json.load(file)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

    @staticmethod
    def write_json_file(file_path: str, data: list):
        # writes a list of data to a json file
        try:
            with open(file_path, "w", encoding="utf-8", newline="") as file:
                json.dump(data, file, indent=2)
        except FileNotFoundError as ex:
            raise EnterpriseManagementException("Wrong file  or file path") from ex
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException("JSON Decode Error - Wrong JSON Format") from ex

    @staticmethod
    def calculate_control_digit(numbers: str):
        """ Implementation for calculating control digit"""

        sum_odd = 0
        sum_even = 0

        length_numbers = len(numbers)

        for index in range(length_numbers):
            if index % 2 == 0:
                doubled_digit = int(numbers[index]) * 2
                if doubled_digit > 9:
                    sum_odd = sum_odd + (doubled_digit // 10) + (doubled_digit % 10)
                else:
                    sum_odd = sum_odd + doubled_digit
            else:
                sum_even = sum_even + int(numbers[index])

        total_sum = sum_odd + sum_even
        remainder = total_sum % 10
        control_digit = 10 - remainder

        if control_digit == 10:
            control_digit = 0

        return control_digit

    @staticmethod
    def validate_company_cif(cif: str):
        """validates a cif number """
        if not isinstance(cif, str):
            raise EnterpriseManagementException("CIF code must be a string")
        cif_pattern = re.compile(r"^[ABCDEFGHJKNPQRSUVW]\d{7}[0-9A-J]$")
        if not cif_pattern.fullmatch(cif):
            raise EnterpriseManagementException("Invalid CIF format")

        first_letter = cif[0]
        numbers = cif[1:8]
        control = cif[8]

        control_digit = EnterpriseManager.calculate_control_digit(numbers)

        letters = "JABCDEFGHI"

        if first_letter in ('A', 'B', 'E', 'H'):
            if str(control_digit) != control:
                raise EnterpriseManagementException("Invalid CIF character control number")
        elif first_letter in ('P', 'Q', 'S', 'K'):
            if letters[control_digit] != control:
                raise EnterpriseManagementException("Invalid CIF character control letter")
        else:
            raise EnterpriseManagementException("CIF type not supported")
        return True
    

    @staticmethod
    def validate_project_acronym(project_acronym: str):
        """validates the project acronym using regex"""

        acronym_pattern = re.compile(r"^[a-zA-Z0-9]{5,10}")
        is_valid_acronym = acronym_pattern.fullmatch(project_acronym)

        if not is_valid_acronym:
            raise EnterpriseManagementException("Invalid acronym")
    
    @staticmethod
    def validate_project_description(project_description: str):
        """validates the project description using regex"""
        
        description_pattern = re.compile(r"^.{10,30}$")
        is_valid_description = description_pattern.fullmatch(project_description)
        if not is_valid_description:
            raise EnterpriseManagementException("Invalid description format")


    def validate_starting_date(self, date_str: str):
        """validates the  date format  using regex"""
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        is_date_valid = date_pattern.fullmatch(date_str)
        if not is_date_valid:
            raise EnterpriseManagementException("Invalid date format")

        try:
            my_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        if my_date < datetime.now(timezone.utc).date():
            raise EnterpriseManagementException("Project's date must be today or later.")

        if my_date.year < 2025 or my_date.year > 2050:
            raise EnterpriseManagementException("Invalid date format")
        return date_str
    
    #pylint: disable=too-many-arguments, too-many-positional-arguments
    def register_project(self,
                         company_cif: str,
                         project_acronym: str,
                         project_description: str,
                         department: str,
                         date: str,
                         budget: str):
        """Registers a new project"""
        self.validate_company_cif(company_cif)

        self.validate_project_acronym(project_acronym)

        self.validate_project_description(project_description)

        # Validate department
        department_pattern = re.compile(r"(HR|FINANCE|LEGAL|LOGISTICS)")
        is_valid_department = department_pattern.fullmatch(department)
        if not is_valid_department:
            raise EnterpriseManagementException("Invalid department")

        self.validate_starting_date(date)

        # Validate budget
        try:
            parsed_budget = float(budget)
        except ValueError as exc:
            raise EnterpriseManagementException("Invalid budget amount") from exc

        budget_string = str(parsed_budget)
        if '.' in budget_string:
            decimal_places = len(budget_string.split('.')[1])
            if decimal_places > 2:
                raise EnterpriseManagementException("Invalid budget amount")

        if parsed_budget < 50000 or parsed_budget > 1000000:
            raise EnterpriseManagementException("Invalid budget amount")

        new_project = EnterpriseProject(company_cif=company_cif,
                                        project_acronym=project_acronym,
                                        project_description=project_description,
                                        department=department,
                                        starting_date=date,
                                        project_budget=budget)

        # Storage logic
        projects_list = self.read_json_file(PROJECTS_STORE_FILE)

        for project_item in projects_list:
            if project_item == new_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

        projects_list.append(new_project.to_json())

        self.write_json_file(PROJECTS_STORE_FILE, projects_list)

        return new_project.project_id


    def find_docs(self, date_str):
        """
        Generates a JSON report counting valid documents for a specific date.

        Checks cryptographic hashes and timestamps to ensure historical data integrity.
        Saves the output to 'resultado.json'.

        Args:
            date_str (str): date to query.

        Returns:
            number of documents found if report is successfully generated and saved.

        Raises:
            EnterpriseManagementException: On invalid date, file IO errors,
                missing data, or cryptographic integrity failure.
        """
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        is_date_valid = date_pattern.fullmatch(date_str)
        if not is_date_valid:
            raise EnterpriseManagementException("Invalid date format")

        try:
            my_date = datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

        # open documents
        documents_list = self.read_json_file(TEST_DOCUMENTS_STORE_FILE)

        documents_found = 0

        # loop to find
        for document_record in documents_list:
            timestamp_value = document_record["register_date"]

            # string conversion for easy match
            doc_date_str = datetime.fromtimestamp(timestamp_value).strftime("%d/%m/%Y")

            if doc_date_str == date_str:
                document_date_object = datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
                with freeze_time(document_date_object):
                    # check the project id (thanks to freezetime)
                    # if project_id are different then the data has been
                    # manipulated
                    project_document = ProjectDocument(document_record["project_id"], document_record["file_name"])
                    if project_document.document_signature == document_record["document_signature"]:
                        documents_found = documents_found + 1
                    else:
                        raise EnterpriseManagementException("Inconsistent document signature")

        if documents_found == 0:
            raise EnterpriseManagementException("No documents found")

        # prepare json text
        current_timestamp = datetime.now(timezone.utc).timestamp()
        report_entry = {"Querydate": date_str,
                        "ReportDate": current_timestamp,
                        "Numfiles": documents_found
                            }

        reports_list = self.read_json_file(TEST_NUMDOCS_STORE_FILE)
        reports_list.append(report_entry)
        self.write_json_file(TEST_NUMDOCS_STORE_FILE, reports_list)

        return documents_found
