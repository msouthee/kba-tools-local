# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAToolsLocal_v1.pyt
#
# Script created:   2021-11-18
# Last Updated:     2022-01-18
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2021
#
# Purpose:          Python Toolbox to hold the KBAToolsLocal to be run by regional coordinators on local computers.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries and modules
import arcpy
import SingleSpeciesSelectionTool
import GroupedSpeciesSelectionTool

# Reload your module in the Python toolbox
import importlib
importlib.reload(SingleSpeciesSelectionTool)
importlib.reload(GroupedSpeciesSelectionTool)


# Define Toolbox
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "KBA Tools Local"
        self.alias = "KBAToolsLocal"

        # List of tool classes associated with this toolbox
        self.tools = [ToolSingleSpeciesSelection,
                      ToolGroupedSpeciesSelection]


# Define Single Species Selection Tool
class ToolSingleSpeciesSelection(object):
    def __init__(self):
        """Define the Single Species Selection Tool."""
        self.label = "Data Exploration Tool (Species and/or Infraspecies)"
        self.description = "Add data to the map separately for species and/or infraspecies."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""

        # Table parameter. Because parameterType = Derived, this parameter will NOT show up in the Tool dialog window.
        param_table = arcpy.Parameter(
            displayName='Biotics Table',
            name='biotics',
            datatype='GPTableView',
            parameterType='Derived',
            direction='Input')

        # Default table to populate in the tool.
        param_table.value = "BIOTICS_ELEMENT_NATIONAL"  # run local & server. User-friendly SQL statements available

        # SQL parameter
        param_sql = arcpy.Parameter(
            displayName='ADD DATA TO THE MAP SEPARATELY FOR SPECIES AND INFRASPECIES'
                        '\n\nIf you select a full species, all infraspecies will be processed by default'
                        '\n\nSelect a species: ',
            name='speciesname',
            datatype='GPSQLExpression',
            parameterType='Required',
            direction='Input')

        # Set the parameter dependency to create an sql expression based on the input table
        param_sql.parameterDependencies = [param_table.name]

        # Default sql query
        param_sql.value = "national_scientific_name = 'Abronia latifolia'"

        # Yes/No parameter
        param_infraspecies = arcpy.Parameter(
            displayName='If you selected an infraspecies, do you want to process the full species too?',
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
        sst = SingleSpeciesSelectionTool.Tool()
        sst.run_tool(parameters, messages)
        return


# Define Grouped Species Selection Tool
class ToolGroupedSpeciesSelection(object):
    def __init__(self):
        """Define the Grouped Species Selection Tool."""
        self.label = "Mapping Tool for Species"
        self.description = "Add data to the map grouped together for a species and all its infraspecies."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions."""

        # # Table parameter. Because parameterType = Derived, this parameter will NOT show up in the Tool dialog window.
        # param_table = arcpy.Parameter(
        #     displayName='Biotics Table',
        #     name='biotics',
        #     datatype='GPTableView',
        #     parameterType='Derived',
        #     direction='Input')
        #
        # # Default table to populate in the tool.
        # param_table.value = "BIOTICS_ELEMENT_NATIONAL"  # run local & server. User-friendly SQL statements available
        #
        # # SQL parameter
        # param_sql = arcpy.Parameter(
        #     displayName='ADD DATA TO THE MAP GROUPED TOGETHER FOR A SELECTED SPECIES AND ITS INFRASPECIES'
        #                 '\n\nSelect a species (this tool will only run on species):',
        #     name='speciesname',
        #     datatype='GPSQLExpression',
        #     parameterType='Required',
        #     direction='Input')
        #
        # # Set the parameter dependency to create an sql expression based on the input table
        # param_sql.parameterDependencies = [param_table.name]
        #
        # # Default sql query
        # param_sql.value = "national_scientific_name = 'Acaulon muticum'"
        #
        # # params = [param_table, param_sql]
        # # return params
        #
        # # NEW TEST PARAMETER
        # param_string = arcpy.Parameter(
        #     displayName="Species Name String",
        #     name="speciesnamestring",
        #     datatype="GPString",
        #     parameterType="Required",
        #     direction="Input")
        #
        # # Set the parameter dependency to create an sql expression based on the input table
        # param_string.parameterDependencies = [param_table.name]
        #
        # biotics_species = arcpy.da.SearchCursor('BIOTICS_ELEMENT_NATIONAL', 'national_scientific_name',
        #                                         "ca_nname_level = 'Species'")
        #
        # # Set a filter to use a ValueList and populate the values from the biotics_species SearchCursor
        # param_string.filter.type = "ValueList"
        # param_string.filter.list = sorted([row[0] for row in biotics_species])
        #
        # params = [param_table, param_sql, param_string]

        # NEW TEST PARAMETER AS THE ONLY PARAMETER
        param_string = arcpy.Parameter(
            displayName="Species Name:",
            name="speciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # # Set the parameter dependency to create an sql expression based on the input table
        # param_string.parameterDependencies = [param_table.name]

        biotics_species = arcpy.da.SearchCursor('BIOTICS_ELEMENT_NATIONAL', 'national_scientific_name',
                                                "ca_nname_level = 'Species'")

        # Set a filter to use a ValueList and populate the values from the biotics_species SearchCursor
        param_string.filter.type = "ValueList"
        param_string.filter.list = sorted([row[0] for row in biotics_species])

        params = [param_string]

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
        gst = GroupedSpeciesSelectionTool.Tool()
        gst.run_tool(parameters, messages)
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
#         sst = SpeciesSelectionTool.Tool()
#         sst.run_tool(parameters, messages)
#         return
