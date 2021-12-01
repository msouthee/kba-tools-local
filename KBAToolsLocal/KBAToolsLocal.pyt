# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAToolsLocal.pyt
#
# Script created:   2021-11-18
# Last Updated:     2021-11-18
# Script Author:    Meg Southee
#
# Purpose:          Python Toolbox to hold the KBAToolsLocal to be run by regional coordinators on local computers.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries and modules
import arcpy
import SpeciesSelectionTool

# Reload your module in the Python toolbox
import importlib
importlib.reload(SpeciesSelectionTool)


# Define Toolbox
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "KBA Tools Local"
        self.alias = "KBAToolsLocal"

        # List of tool classes associated with this toolbox
        self.tools = [ToolSpeciesSelection]


# Define Species Selection Tool
class ToolSpeciesSelection(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Species Selection Tool"
        self.description = "Use this tool to select all points, lines & polygons for a specific species."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # # Table and SQL parameter
        param_table = arcpy.Parameter(
            displayName='Biotics Table (already selected for you)',
            name='biotics',
            datatype='GPTableView',
            parameterType='Optional',
            direction='Input')

        # Default table to populate in the tool
        param_table.value = "BIOTICS_ELEMENT_NATIONAL"

        param_sql = arcpy.Parameter(
            displayName='Species SQL Query (select the species of interest from the dropdown on the right)',
            name='speciesname',
            datatype='GPSQLExpression',
            parameterType='Required',
            direction='Input')

        # Set the parameter dependency to create an sql expression based on the input table
        param_sql.parameterDependencies = [param_table.name]

        # Default sql query
        param_sql.value = "national_scientific_name = 'Abronia umbellata'"

        param_infraspecies = arcpy.Parameter(
            displayName='If you selected an infraspecies, do you want to select the full species as well? '
                        'This toggle will do nothing if you selected a full species.',
            name='infraspecies',
            datatype='GPString',
            parameterType='Required',
            direction='Input')

        # Filter list of available responses
        param_infraspecies.filter.list = ["Yes", "No"]

        # Default selection
        param_infraspecies.value = "Yes"

        params = [param_table, param_sql, param_infraspecies]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        sst = SpeciesSelectionTool.Tool()
        sst.run_tool(parameters, messages)
        return



# # # TEMPLATE
# # Sample Template for Toolbox
# class Toolbox(object):
#     def __init__(self):
#         """Define the toolbox (the name of the toolbox is the name of the
#         .pyt file)."""
#         self.label = "Toolbox"
#         self.alias = ""
#
#         # List of tool classes associated with this toolbox
#         self.tools = [Tool]

# # Sample Template for Tool
# class Tool(object):
#     def __init__(self):
#         """Define the tool (tool name is the name of the class)."""
#         self.label = "Tool"
#         self.description = ""
#         self.canRunInBackground = False
#
#     def getParameterInfo(self):
#         """Define parameter definitions"""
#         params = None
#         return params
#
#     def isLicensed(self):
#         """Set whether tool is licensed to execute."""
#         return True
#
#     def updateParameters(self, parameters):
#         """Modify the values and properties of parameters before internal
#         validation is performed.  This method is called whenever a parameter
#         has been changed."""
#         return
#
#     def updateMessages(self, parameters):
#         """Modify the messages created by internal validation for each tool
#         parameter.  This method is called after internal validation."""
#         return
#
#     def execute(self, parameters, messages):
#         """The source code of the tool."""
#         return
