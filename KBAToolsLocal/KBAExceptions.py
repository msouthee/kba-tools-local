# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAExceptions.py

class NoDataError(Exception):
    """Exception raised for NoDataError in the tool."""
    pass


class NoTableError(Exception):
    """Exception raised for NoDataError in the tool."""
    pass


class DefQueryError(Exception):
    """Exception raised for DefQueryError in the tool."""
    pass


class SpeciesDataError(Exception):
    """Exception raised for SpeciesDataError in the tool."""
    pass


class BioticsError(Exception):
    """Exception raised for BioticsError in the tool."""
    pass
