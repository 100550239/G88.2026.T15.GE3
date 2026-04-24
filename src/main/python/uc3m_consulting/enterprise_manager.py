"""Module for managing the enterprise projects and documents"""
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
from uc3m_consulting.project_validator import ProjectValidator


class EnterpriseManager:
    """Class for providing the methods for managing the orders"""

    def __init__(self):
        pass

    @staticmethod
    def _count_valid_documents(documents_list: list, date_str: str) -> int:
        """Counts the valid documents for a specific date checking signatures"""

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
        """Saves the search report to the JSON store"""
        current_timestamp = datetime.now(timezone.utc).timestamp()
        report_entry = {
            "Querydate": date_str,
            "ReportDate": current_timestamp,
            "Numfiles": documents_found
        }

        reports_list = JsonStore.read_json_file(TEST_NUMDOCS_STORE_FILE)
        reports_list.append(report_entry)
        JsonStore.write_json_file(TEST_NUMDOCS_STORE_FILE, reports_list)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def register_project(self,
                         company_cif: str,
                         project_acronym: str,
                         project_description: str,
                         department: str,
                         date: str,
                         budget: str):
        """Registers a new project"""

        ValidateCIF.validate_company_cif(company_cif)
        ProjectValidator.validate_project_acronym(project_acronym)
        ProjectValidator.validate_project_description(project_description)
        ProjectValidator.validate_department(department)
        ProjectValidator.validate_starting_date(date)
        ProjectValidator.validate_budget(budget)

        new_project = EnterpriseProject(company_cif=company_cif,
                                        project_acronym=project_acronym,
                                        project_description=project_description,
                                        department=department,
                                        starting_date=date,
                                        project_budget=budget)


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
        """
        ProjectValidator.validate_date_format(date_str)

        documents_list = JsonStore.read_json_file(TEST_DOCUMENTS_STORE_FILE)
        documents_found = self._count_valid_documents(documents_list, date_str)
        self._save_search_report(date_str, documents_found)

        return documents_found
