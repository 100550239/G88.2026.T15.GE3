"""Module for managing the projects JSON storage"""
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException
from uc3m_consulting.enterprise_manager_config import PROJECTS_STORE_FILE
from uc3m_consulting.json_store import JsonStore

class ProjectJsonStore:
    """Class responsible for project data persistence"""

    __instance = None

    def __new__(cls):
        """Ensures a single instance for project storage"""
        if cls.__instance is None:
            cls.__instance = super(ProjectJsonStore, cls).__new__(cls)
        return cls.__instance


    @staticmethod
    def add_project(project_json: dict):
        """Adds a new project to the JSON file verifying duplicates"""
        projects_list = JsonStore.read_json_file(PROJECTS_STORE_FILE)

        for project_item in projects_list:
            if project_item == project_json:
                raise EnterpriseManagementException("Duplicated project in projects list")

        projects_list.append(project_json)
        JsonStore.write_json_file(PROJECTS_STORE_FILE, projects_list)
