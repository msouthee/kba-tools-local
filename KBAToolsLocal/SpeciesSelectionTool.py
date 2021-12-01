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


class Tool:
    """Select all points, lines and polygons for a specific species."""
    def __init__(self):
        pass

    def run_tool(self, parameters, messages):

        # Make variables from parameters
        param_table = parameters[0].valueAsText
        param_sql = parameters[1].valueAsText
        param_infraspecies = parameters[2].valueAsText

        arcpy.AddMessage("Parameters: {0}, {1}, {2}".format(param_table, param_sql, param_infraspecies))

        # # species level list based on the Canadian national name level [ca_nname_level] field
        # sp_level_list = ["species",
        #                  "subspecies",
        #                  "population",
        #                  "variety"]

        # List of biotics fields that you want to use in the search cursor
        biotics_fields = ["national_scientific_name",
                          "speciesid",
                          "ca_nname_level"]

        try:
            # Current ArcPro Project
            aprx = arcpy.mp.ArcGISProject("CURRENT")

            # Current Active Map in ArcPro Project
            m = aprx.activeMap

            # clear all selections in the map
            m.clearSelection()

            # Select the record in BIOTICS table based on the user-specified sql expression
            biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                     "NEW_SELECTION",
                                                                     param_sql)

            # Get record-level information about the selected record using a search cursor
            with arcpy.da.SearchCursor(param_table, biotics_fields, param_sql) as cursor:
                for row in cursor:

                    arcpy.AddMessage("Scientific Name: {}".format(row[0]))
                    arcpy.AddMessage("Species ID: {}".format(row[1]))
                    arcpy.AddMessage("Species Level: {}".format(row[2]))

                    # # Check to see if the selected record is a full species or a subspecies
                    # if row[2].lower() == "species":
                    #     arcpy.AddMessage("Species selected")
                    #     pass
                    #
                    # # this could also just be an else: statement if all 3 categories are being handled the same way
                    # elif row[2].lower() in ("subspecies", "population", "variety"):
                    #     arcpy.AddMessage("{} selected".format(row[2]))
                    #     pass

                    # Logic if user wants to select the full species & infraspecies [based on param_infraspecies]
                    if param_infraspecies == "Yes":

                        # Logic to select additional records in the biotics table

                        # Get the full species name
                        split = row[0].split(" ")
                        s = " "
                        species = s.join(split[:2])

                        # SQL statement to add full species and all infraspecies/subspecies/populations/varieties
                        sql = "national_scientific_name LIKE '{}%'".format(species)

                        # Add the full species and infraspecies to the selected record in biotics table
                        biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                                                                                 "ADD_TO_SELECTION",
                                                                                 sql)

                    # Logic if users only wants to select the single species
                    else:
                        pass

                """ This is where you end up if directly if param_infraspecies == "Yes", but you get here either way.
                    Use the speciesid value to iterate through the datasets and create output layers in the TOC."""

                # Get the count from the Result object based on the selected records in BIOTICS table
                count = int(arcpy.GetCount_management(biotics_record).getOutput(0))

                # Check to see how many records are selected in biotics
                if count == 1:  # Process single species
                    arcpy.AddMessage("{} record selected from Biotics table.".format(count))

                    # Variable to hold the species id
                    speciesid = row[1]

                    # Variable to hold the speciesid sql statement
                    speciesid_sql = "speciesid = {}".format(speciesid)
                    # arcpy.AddMessage(speciesid_sql)

                    # This logic doesn't actually help the workflow, it just checks that the logic is working properly
                    # Select single record in the species table
                    species_record = arcpy.management.SelectLayerByAttribute("Species",
                                                                             "NEW_SELECTION",
                                                                             speciesid_sql)

                    # Check that one record is selected
                    species_count = int(arcpy.GetCount_management(species_record).getOutput(0))
                    arcpy.AddMessage("{} record selected from Species table.".format(species_count))

                    # # Iterate through the other 4 feature classes and start making data layers
                    # points = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPoint",
                    #                                                  "NEW_SELECTION",
                    #                                                  speciesid_sql)
                    #
                    # lines = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputLine",
                    #                                                 "NEW_SELECTION",
                    #                                                 speciesid_sql)
                    #
                    # polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\InputPolygon",
                    #                                                    "NEW_SELECTION",
                    #                                                    speciesid_sql)
                    #
                    # eo_polygons = arcpy.management.SelectLayerByAttribute(r"SpeciesData\EO_Polygon",
                    #                                                       "NEW_SELECTION",
                    #                                                       speciesid_sql)
                    #
                    # eo_count = int(arcpy.GetCount_management(eo_polygons).getOutput(0))
                    # arcpy.AddMessage("{} record selected from EO_Polygon table.".format(eo_count))

                    # Steps to create a new group layer?? NO, but it works for the individual data layers
                    group_lyr = m.listLayers("SpeciesData")[0]
                    lyr_name = "{} - SpeciesID {}".format(group_lyr.name, speciesid)
                    arcpy.AddMessage(lyr_name)
                    new_group_lyr = arcpy.MakeFeatureLayer_management(group_lyr, lyr_name).getOutput(0)
                    m.addLayer(new_group_lyr, "TOP")
                    new_group_lyr.isVisible = False
                    aprx.save()

                    # # ..................................................................................................
                    # # List the existing layer that you want to duplicate
                    # copy_lyr = m.listLayers('EO_Polygon')[0]
                    #
                    # # Create the output layer name
                    # lyr_name = "{} - SpeciesID {}".format(copy_lyr.name, speciesid)
                    # arcpy.AddMessage(lyr_name)
                    #
                    # # Make a new feature layer with added .getOutput(0) function
                    # new_lyr = arcpy.MakeFeatureLayer_management(copy_lyr, lyr_name, speciesid_sql, None).getOutput(0)
                    #
                    # # Add the new layer to the new group layer in the map & turn off visibility
                    # m.addLayer(new_lyr)  # Works
                    # new_lyr.isVisible = False  # not clear if this does anything
                    #
                    # # Save the project
                    # aprx.save()
                    # # ..................................................................................................

                    # m.addLayerToGroup(new_group_lyr, new_lyr, "TOP") # Doesn't work yet
                    # aprx.save()

                    # # Add the layer to an existing group
                    # m.addLayerToGroup(group_lyr, lyr, "TOP")

                    # Move layer in the TOC?

                    # # Save the project
                    # aprx.save()

                    arcpy.AddMessage("End of script.")

                elif count > 1:  # Process species & infraspecies
                    arcpy.AddMessage("{} records selected.".format(count))

                    # process all of the species in the list

                    # create a new search cursor & start calling your function to do stuff


                else:
                    # Throw an error that there are no species selected
                    arcpy.AddError("{} records selected. Please select a species using the SQL statement"
                                   .format(count))




        except:
            print("Error!")


# Controlling process
if __name__ == '__main__':
    sst = Tool()

    # Hard-coded parameters for debugging
    param_table = arcpy.Parameter()
    param_sql = arcpy.Parameter()
    param_infraspecies = arcpy.Parameter()

    param_table.value = "BIOTICS_ELEMENT_NATIONAL"
    param_sql.value = "national_scientific_name = 'Abronia umbellata'"
    param_infraspecies = "Yes"

    parameters = [param_table, param_sql, param_infraspecies]

    # Run the tool using the parameters
    sst.run_tool(parameters, None)
