# ----------------------------------------------------------------------------------------------------------------------
# Script Name:      SpeciesSelectionTool.py
#
# Script Created:   2021-10-27
# Last Updated:     2021-11-30
# Script Author:    Meg Southee
#
# Purpose:          Create definition queries and group the output datasets (with valid data) under a species heading
#                   in the TOC in the active map.
# ----------------------------------------------------------------------------------------------------------------------

# Import libraries
import arcpy
# import os
# import sys




class Tool:
    """Select all points, lines and polygons for a specific species."""
    def __init__(self):
        pass

    def run_tool(self, parameters, messages):

        # Make variables for parameters
        param_sql = parameters[0].valueAsText

        # # Script Parameters
        # param_sql = arcpy.GetParameterAsText(0)

        arcpy.AddMessage(param_sql)

        # species_selection_expression = "national_scientific_name = '{}'".format(param_sql)
        #
        # arcpy.AddMessage(species_selection_expression)

        # Current ArcPro Project
        aprx = arcpy.mp.ArcGISProject("CURRENT")

        # Current Active Map in ArcPro Project
        m = aprx.activeMap

        # clear all selections in the map
        m.clearSelection()

        try:
            # Select record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute("BIOTICS_ELEMENT_NATIONAL",
                                                                     "NEW_SELECTION",
                                                                     param_sql,
                                                                     None)

            # # Select record in BIOTICS table based on the user-specified species name
            # biotics_record = arcpy.management.SelectLayerByAttribute("BIOTICS_ELEMENT_NATIONAL",
            #                                                          "NEW_SELECTION",
            #                                                          "{}".format(species_selection_expression),
            #                                                          None)

            count = arcpy.management.GetCount(biotics_record)
            if count == 1:
                arcpy.AddMessage("One record selected")
                pass

            elif count > 1:
                arcpy.AddError("More that one record selected.")

            else:
                arcpy.AddError("No records selected.")

            # check to see if a record was selected, if not provide error message

            # if record is selected, get the speciesid value

            # use the speciesid value to iterate through the datasets and create output layers in the TOC

        except:
            print("Error!")


# Controlling process
if __name__ == '__main__':
    sst = Tool()

    # Hard-coded parameters for debugging
    param_sql = arcpy.Parameter()
    # This would be if you make the entire sql query yourself.  Is there a way to just select species as dropdown
    param_sql.value = "national_scientific_name = 'Abronia latifolia'"
    parameters = [param_sql]

    # Run the tool using the parameters
    sst.run_tool(parameters, None)
