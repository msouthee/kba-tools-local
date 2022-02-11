import arcpy


# Define a function to create the group layer for a selected record
def create_group_lyr_scoping(m, grp_lyr, sp_com_name, sp_sci_name, infra_exists, sp_level):
    arcpy.AddMessage("Run create_group_lyr function.")

    # Assign naming convention for output group layer in TOC based on infra & species level parameters:
    if infra_exists is True and sp_level == "Species":
        # Common Name (Scientific Name) data not identified to infraspecies
        grp_lyr_name = "{} ({}) data not identified to infraspecies".format(sp_com_name, sp_sci_name)

    else:
        # Common Name (Scientific Name)
        grp_lyr_name = "{} ({})".format(sp_com_name, sp_sci_name)

    # Add a copy of the SpeciesData group layer to the TOC (by referencing the .lyrx file written to scratch)
    m.addLayer(grp_lyr, "TOP")

    # Rename the newly added group layer, because layer was added at top index reference = [0]
    group_lyr = m.listLayers("SpeciesData")[0]
    group_lyr.name = grp_lyr_name  # rename the group layer in TOC
    group_lyr = m.listLayers(grp_lyr_name)[0]
    group_lyr.visible = False  # Turn off the visibility for the group layer

    return group_lyr
