"""Module for validating project data"""
import re
from datetime import datetime, timezone
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException

class ProjectValidator:
    """Class for validating project related data"""

    @staticmethod
    def validate_date_format(date_str: str):
        """Validates the date format for finding documents"""
        date_pattern = re.compile(r"^(([0-2]\d|3[0-1])\/(0\d|1[0-2])\/\d\d\d\d)$")
        is_date_valid = date_pattern.fullmatch(date_str)
        if not is_date_valid:
            raise EnterpriseManagementException("Invalid date format")

        try:
            datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError as ex:
            raise EnterpriseManagementException("Invalid date format") from ex

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
        ProjectValidator.validate_date_format(date_str)
        my_date = datetime.strptime(date_str, "%d/%m/%Y").date()

        if my_date < datetime.now(timezone.utc).date():
            raise EnterpriseManagementException("Project's date must be today or later.")

        if my_date.year < 2025 or my_date.year > 2050:
            raise EnterpriseManagementException("Invalid date format")
        return date_str