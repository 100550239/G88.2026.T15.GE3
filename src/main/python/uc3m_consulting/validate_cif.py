"""Module for validating the CIF of a project document"""
import re
from uc3m_consulting.enterprise_management_exception import EnterpriseManagementException



class ValidateCIF:
    """Class for validating the CIF of a project document"""

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

        control_digit = ValidateCIF.calculate_control_digit(numbers)

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
