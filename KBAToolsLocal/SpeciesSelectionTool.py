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
        biotics_fields = ["speciesid",
                          "element_code",
                          "ca_nname_level",
                          "national_scientific_name",
                          "national_engl_name"]  # new list of fields

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

                    # Assign variables for row items
                    speciesid = row[0]
                    element_code = row[1]
                    s_level = row[2]
                    sci_name = row[3]
                    common_name = row[4]

                    # Print statements
                    arcpy.AddMessage("Species ID: {}".format(speciesid))
                    arcpy.AddMessage("Scientific Name: {}".format(sci_name))
                    arcpy.AddMessage("Common Name: {}".format(common_name))
                    arcpy.AddMessage("Species Level: {}".format(s_level))
                    arcpy.AddMessage("Element Code: {}".format(element_code))

            # Exit the search cursor, keep the variables from the search cursor.

            # Check to see if the selected record is a full species or a subspecies
            if s_level.lower() == "species":
                arcpy.AddMessage("Full species selected. Process all infraspecies.")
                # arcpy.AddMessage("Species ID = {}".format(speciesid))
                # arcpy.AddMessage("speciesid = {}".format(speciesid))

                # Select record from species table for the full species
                species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                          "NEW_SELECTION",
                                                                          "speciesid = {}".format(
                                                                              speciesid))

                # Add logic to select all infraspecies records for this full species
                # Compare and match element_code to records in Species table
                # Select records from Species table where fullspecies_elementcode matches the element_code
                species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                          "ADD_TO_SELECTION",
                                                                          "fullspecies_elementcode = '{}'".format(element_code))

                count = int(arcpy.GetCount_management(species_records).getOutput(0))
                arcpy.AddMessage("{} species records selected (full species & infraspecies)".format(count))

            # If the user selects a subspecies/population/variety, check to see if they want the full species
            elif s_level.lower() in ("subspecies", "population", "variety"):

                # Check if user wants to select the infraspecies & full species [based on param_infraspecies]
                if param_infraspecies == "Yes":

                    # Logic to select additional records based on element_code
                    # Select initial record from Species table based on the speciesid
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "NEW_SELECTION",
                                                                              "speciesid = {}".format(
                                                                                  speciesid))

                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (infraspecies)".format(count))

                    # Create a search cursor to get the fullspecies_elementcode from the species_record
                    with arcpy.da.SearchCursor("Species",
                                               ["fullspecies_elementcode"],
                                               "speciesid = {}".format(speciesid)) as species_cursor:

                        for species_row in species_cursor:
                            fs_elementcode = species_row[0]  # get the fullspecies_element code

                    # Add the full species record to the selected infraspecies record
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "ADD_TO_SELECTION",
                                                                              "fullspecies_elementcode = '{}'".format(fs_elementcode))

                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (after adding full species).".format(count))

                    # # Get the full species name
                    # split = sci_name.split(" ")
                    # s = " "
                    # species_name = s.join(split[:2])
                    #
                    # # This logic needs to be replaced based on the element_code field in Biotics
                    # # and the fullspecies_elementcode in the Species table
                    #
                    # # SQL statement to add full species and all infraspecies/subspecies/populations/varieties
                    # sql = "national_scientific_name LIKE '{}%'".format(species_name)
                    #
                    # # Add the full species and infraspecies to the selected record in biotics table
                    # biotics_record = arcpy.management.SelectLayerByAttribute(param_table,
                    #                                                          "ADD_TO_SELECTION",
                    #                                                          sql)

                # Logic if users only wants to select the single infraspecies by itself
                else:
                    species_records = arcpy.management.SelectLayerByAttribute("Species",
                                                                              "NEW_SELECTION",
                                                                              "speciesid = {}".format(
                                                                                  speciesid))

                    count = int(arcpy.GetCount_management(species_records).getOutput(0))
                    arcpy.AddMessage("{} species records selected (infraspecies only)".format(count))

            """ This is where you end up  if you select a full species; if you select an infraspecies and
                param_infraspecies == "Yes"; or if you select an infraspecies and param_infraspecies == "No".
                Iterate through the selected species records and create output layers in the map TOC."""

            # # Get the count from the Result object based on the selected record(s) in the Species table
            # count = int(arcpy.GetCount_management(species_records).getOutput(0))

            # Check to see how many records are selected in biotics
            if count == 1:  # Process single species WRITE A FUNCTION TO DO THIS PROCESSING
                arcpy.AddMessage("{} records selected.".format(count))

                # # Iterate through the 4 feature classes and start making data layers
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

                # # Steps to create a new group layer?? NO, but it works for the individual data layers
                # group_lyr = m.listLayers("SpeciesData")[0]
                # lyr_name = "{} - SpeciesID {}".format(group_lyr.name, speciesid)
                # arcpy.AddMessage(lyr_name)
                # new_group_lyr = arcpy.MakeFeatureLayer_management(group_lyr, lyr_name).getOutput(0)
                # m.addLayer(new_group_lyr, "TOP")
                # new_group_lyr.isVisible = False
                # aprx.save()

                # ................................................................................................
                # List the existing layer that you want to duplicate
                copy_lyr = m.listLayers('EO_Polygon')[0]

                # Create the output layer name
                lyr_name = "{} - SpeciesID {}".format(copy_lyr.name, speciesid)
                arcpy.AddMessage(lyr_name)

                # Make a new feature layer with added .getOutput(0) function
                new_lyr = arcpy.MakeFeatureLayer_management(copy_lyr, lyr_name, speciesid_sql, None).getOutput(0)

                # Add the new layer to the new group layer in the map & turn off visibility
                m.addLayer(new_lyr)  # Works
                new_lyr.isVisible = False  # not clear if this does anything

                # Save the project
                aprx.save()
                # ................................................................................................

                # m.addLayerToGroup(new_group_lyr, new_lyr, "TOP") # Doesn't work yet
                # aprx.save()

                # # Add the layer to an existing group
                # m.addLayerToGroup(group_lyr, lyr, "TOP")

                # Move layer in the TOC?

                # # Save the project
                # aprx.save()

            elif count > 1:  # Process species & infraspecies
                arcpy.AddMessage("{} records selected.".format(count))

                # process all of the species in the list

                # create a new search cursor & start calling your function to do stuff

            else:
                # Throw an error that there are no species selected
                arcpy.AddError("{} records selected. Please select a record from Biotics using the SQL statement."
                               .format(count))

            arcpy.AddMessage("End of script.")

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
