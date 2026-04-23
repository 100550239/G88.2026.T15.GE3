"""Module for managing the enterprise projects and documents"""
import re

from datetime import datetime, timezone
from freezegun import freeze_time
from uc3m_consulting.enterprise_project import EnterpriseProject
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import (PROJECTS_STORE_FILE,
                                                       TEST_DOCUMENTS_STORE_FILE,
                                                       TEST_NUMDOCS_STORE_FILE)
from uc3m_consulting.project_document import ProjectDocument
from uc3m_consulting.json_store import JsonStore
from uc3m_consulting.validate_cif import ValidateCIF


class EnterpriseManager:
    """Class for providing the methods for managing the orders"""
    def __init__(self):
        pass

    @staticmethod
    def _validate_date_format(date_str: str):
        # it validates the date format for finding documents
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        is_date_valid = date_pattern.fullmatch(date_str)
        if not is_date_valid:
            raise EnterpriseManagementException("Invalid date format")

        try:
            datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

    @staticmethod
    def _count_valid_documents(documents_list: list, date_str: str) -> int:
        # it counts the valid documents for a specific date checking signatures
        documents_found = 0
        for document_record in documents_list:
            timestamp_value = document_record["register_date"]
            doc_date_str = datetime.fromtimestamp(timestamp_value).strftime("%d/%m/%Y")

            if doc_date_str == date_str:
                document_date_object = datetime.fromtimestamp(timestamp_value, tz=timezone.utc)
                with freeze_time(document_date_object):
                    project_document = ProjectDocument(document_record["project_id"],
                                                       document_record["file_name"])
                    if project_document.document_signature == document_record["document_signature"]:
                        documents_found += 1
                    else:
                        raise EnterpriseManagementException("Inconsistent document signature")

        if documents_found == 0:
            raise EnterpriseManagementException("No documents found")

        return documents_found

    @staticmethod
    def _save_search_report(date_str: str, documents_found: int):
        # it saves the search report to the JSON store
        current_timestamp = datetime.now(timezone.utc).timestamp()
        report_entry = {
            "Querydate": date_str,
            "ReportDate": current_timestamp,
            "Numfiles": documents_found
        }

        reports_list = JsonStore.read_json_file(TEST_NUMDOCS_STORE_FILE)
        reports_list.append(report_entry)
        JsonStore.write_json_file(TEST_NUMDOCS_STORE_FILE, reports_list)

    @staticmethod
    def validate_project_acronym(project_acronym: str):
        """validates the project acronym using regex"""

        acronym_pattern = re.compile(r"^[a-zA-Z0-9]{5,10}$")
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


    @staticmethod
    def validate_department(department: str):
        """validates the department"""

        department_pattern = re.compile(r"(HR|FINANCE|LEGAL|LOGISTICS)")
        is_valid_department = department_pattern.fullmatch(department)
        if not is_valid_department:
            raise EnterpriseManagementException("Invalid department")


    @staticmethod
    def validate_budget(budget: str):
        """validates the budget amount"""

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

    @staticmethod
    def validate_starting_date(date_str: str):
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

        ValidateCIF.validate_company_cif(company_cif)

        self.validate_project_acronym(project_acronym)

        self.validate_project_description(project_description)

        self.validate_department(department)

        self.validate_starting_date(date)

        self.validate_budget(budget)

        new_project = EnterpriseProject(company_cif=company_cif,
                                        project_acronym=project_acronym,
                                        project_description=project_description,
                                        department=department,
                                        starting_date=date,
                                        project_budget=budget)

        # Storage logic
        projects_list = JsonStore.read_json_file(PROJECTS_STORE_FILE)

        for project_item in projects_list:
            if project_item == new_project.to_json():
                raise EnterpriseManagementException("Duplicated project in projects list")

        projects_list.append(new_project.to_json())

        JsonStore.write_json_file(PROJECTS_STORE_FILE, projects_list)

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
        self._validate_date_format(date_str)

        documents_list = JsonStore.read_json_file(TEST_DOCUMENTS_STORE_FILE)

        documents_found = self._count_valid_documents(documents_list, date_str)

        self._save_search_report(date_str, documents_found)

        return documents_found