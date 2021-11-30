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
import SpeciesSeletionTool

# Reload your module in the Python toolbox
import importlib
importlib.reload(SpeciesSeletionTool)

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "KBA Tools Local"
        self.alias = "KBAToolsLocal"

        # List of tool classes associated with this toolbox
        self.tools = [SpeciesSelectionTool]

# UPDATE TOOLS AS DEVELOPMENT CONTINUES
# Sample Template for Tool
class SpeciesSelectionTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Species Selection Tool"
        self.description = "Use this tool to select all points, lines & polygons for a specific species."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
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
