# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      KBAToolsLocal.pyt
#
# Script created:   2021-11-18
# Last Updated:     2022-04-26
# Script Author:    Meg Southee
# Credits:          © WCS Canada / Meg Southee 2021
#
# Purpose:          Python Toolbox to hold the LocalKBATools to be run by regional coordinators on local computers.
#
# Updates:          Add parameters to handle french species names.
#
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries and modules
import arcpy
import FullSpeciesMappingTool
import FullSpeciesScopingTool
import InfraspeciesTool

# Reload your module in the Python toolbox
import importlib

importlib.reload(FullSpeciesMappingTool)
importlib.reload(FullSpeciesScopingTool)
importlib.reload(InfraspeciesTool)


# Define Toolbox
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Local KBA Tools"
        self.alias = "LocalKBATools"

        # List of tool classes associated with this toolbox
        self.tools = [ToolFullSpeciesMapping,
                      ToolFullSpeciesScoping,
                      ToolInfraspecies]


# Define Full Species Mapping Tool
class ToolFullSpeciesMapping(object):
    def __init__(self):
        """Define the Full Species Mapping Tool."""
        self.label = "Mapping Tool - Species"
        self.description = "Add data to the map in a single group for species and infraspecies."
        self.canRunInBackground = False

    def getParameterInfo(self):
        # """Define parameter definitions."""
        # param_species = arcpy.Parameter(
        #     displayName="Species Name:",
        #     name="speciesnamestring",
        #     datatype="GPString",
        #     parameterType="Required",
        #     direction="Input")
        #
        # # Create a search cursor to filter the values to show only full species names
        # biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
        #                                                "national_scientific_name",
        #                                                "ca_nname_level = 'Species'")
        #
        # # Set parameter filter to use a ValueList and populate the values from SearchCursor
        # param_species.filter.type = "ValueList"
        # param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])
        #
        # params = [param_species]
        # return params

        """Define parameter definitions."""
        param_species = arcpy.Parameter(
            displayName="Species Name:",
            name="speciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values to show only full species names
        biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                       "national_scientific_name",
                                                       "ca_nname_level = 'Species'")

        # Set parameter filter to use a ValueList and populate the values from SearchCursor
        param_species.filter.type = "ValueList"
        param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])

        param_french_names = arcpy.Parameter(
            displayName="Use French species name?",
            name="french_name",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        params = [param_species,
                  param_french_names]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        param_species = arcpy.Parameter(
            displayName="Species Name:",
            name="speciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values to show only full species names
        biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                       "national_scientific_name",
                                                       "ca_nname_level = 'Species'")

        param_species.filter.type = "ValueList"
        param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fsmt = FullSpeciesMappingTool.Tool()
        fsmt.run_tool(parameters, messages)
        return


# Define Full Species Scoping Tool
class ToolFullSpeciesScoping(object):
    def __init__(self):
        """Define the Full Species Scoping Tool."""
        self.label = "Exploratory Tool - Species & Infraspecies"
        self.description = "Add data to the map in separate group for species and infraspecies."
        self.canRunInBackground = False
        self.category = "Exploratory Data Analysis"

    def getParameterInfo(self):
        # """Define parameter definitions."""
        # param_species = arcpy.Parameter(
        #     displayName="Species Name:",
        #     name="speciesnamestring",
        #     datatype="GPString",
        #     parameterType="Required",
        #     direction="Input")
        #
        # # Create a search cursor to filter the values based on the full species names
        # biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
        #                                               "national_scientific_name",
        #                                               "ca_nname_level = 'Species'")
        #
        # # Set parameter filter to use a ValueList and populate the values from SearchCursor
        # param_species.filter.type = "ValueList"
        # param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])
        #
        # params = [param_species]
        # return params

        """Define parameter definitions."""
        param_species = arcpy.Parameter(
            displayName="Species Name:",
            name="speciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values based on the full species names
        biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                      "national_scientific_name",
                                                      "ca_nname_level = 'Species'")

        # Set parameter filter to use a ValueList and populate the values from SearchCursor
        param_species.filter.type = "ValueList"
        param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])

        param_french_names = arcpy.Parameter(
            displayName="Use French species name?",
            name="french_name",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        params = [param_species,
                  param_french_names]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        param_species = arcpy.Parameter(
            displayName="Species Name:",
            name="speciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values based on the full species names
        biotics_species_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                       "national_scientific_name",
                                                       "ca_nname_level = 'Species'")

        param_species.filter.type = "ValueList"
        param_species.filter.list = sorted([row[0] for row in biotics_species_cursor])

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        fsst = FullSpeciesScopingTool.Tool()
        fsst.run_tool(parameters, messages)
        return


# Define Infraspecies Tool
class ToolInfraspecies(object):
    def __init__(self):
        """Define the Infraspecies Tool."""
        self.label = "Mapping Tool - Infraspecies"
        self.description = "Add data to the map in separate groups for infraspecies and its full species, " \
                           "if the user wants to display the full species data too."
        self.canRunInBackground = False

    def getParameterInfo(self):
        # """Define parameter definitions."""
        # param_infraspecies = arcpy.Parameter(
        #     displayName="Infraspecies Name:",
        #     name="infraspeciesnamestring",
        #     datatype="GPString",
        #     parameterType="Required",
        #     direction="Input")
        #
        # # Create a search cursor to filter the values to show only full species names
        # biotics_infraspecies_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
        #                                                     "national_scientific_name",
        #                                                     "ca_nname_level <> 'Species'")
        #
        # # Set parameter filter to use a ValueList and populate the values from SearchCursor
        # param_infraspecies.filter.type = "ValueList"
        # param_infraspecies.filter.list = sorted([row[0] for row in biotics_infraspecies_cursor])
        #
        # ## CHANGE THIS PARAMETER TO A BOOLEAN
        # # Yes/No parameter
        # param_includefullspecies = arcpy.Parameter(
        #     displayName='Do you want to process the full species too?',
        #     name='includefullspecies',
        #     datatype='GPString',
        #     parameterType='Required',
        #     direction='Input')
        #
        # # Filter list of available responses
        # param_includefullspecies.filter.list = ["Yes", "No"]
        #
        # # Default selection
        # param_includefullspecies.value = "No"
        #
        # params = [param_infraspecies, param_includefullspecies]
        # return params

        """Define parameter definitions."""
        param_infraspecies = arcpy.Parameter(
            displayName="Infraspecies Name:",
            name="infraspeciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values to show only full species names
        biotics_infraspecies_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                            "national_scientific_name",
                                                            "ca_nname_level <> 'Species'")

        # Set parameter filter to use a ValueList and populate the values from SearchCursor
        param_infraspecies.filter.type = "ValueList"
        param_infraspecies.filter.list = sorted([row[0] for row in biotics_infraspecies_cursor])

        # Yes/No parameter - changed to a boolean
        param_includefullspecies = arcpy.Parameter(
            displayName='Do you want to process the full species too?',
            name='includefullspecies',
            datatype='GPBoolean',
            parameterType='Optional',
            direction='Input')

        param_french_names = arcpy.Parameter(
            displayName="Use French species name?",
            name="french_name",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        params = [param_infraspecies,
                  param_includefullspecies,
                  param_french_names]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        param_infraspecies = arcpy.Parameter(
            displayName="Infraspecies Name:",
            name="infraspeciesnamestring",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Create a search cursor to filter the values to show only full species names
        biotics_infraspecies_cursor = arcpy.da.SearchCursor("BIOTICS_ELEMENT_NATIONAL",
                                                            "national_scientific_name",
                                                            "ca_nname_level <> 'Species'")

        # Set parameter filter to use a ValueList and populate the values from SearchCursor
        param_infraspecies.filter.type = "ValueList"
        param_infraspecies.filter.list = sorted([row[0] for row in biotics_infraspecies_cursor])

        # # Yes/No parameter
        # param_includefullspecies = arcpy.Parameter(
        #     displayName='Do you want to process the full species too?',
        #     name='includefullspecies',
        #     datatype='GPString',
        #     parameterType='Required',
        #     direction='Input')
        #
        # # Filter list of available responses
        # param_includefullspecies.filter.list = ["Yes", "No"]

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        it = InfraspeciesTool.Tool()
        it.run_tool(parameters, messages)
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
