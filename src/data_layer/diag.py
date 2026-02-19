# This file is meant to be temporary. Once the changes described below are implemented, this file should be deleted.
# List of tables to be used in the project, sorted by dataset. 
# The goal is to have a clear overview of the tables we are using that aren't using dbt processes, 
# so that we can easily identify which tables we need to update.
# For example, stg_ -> int_ - > mart_ (or similar) for tables that are currently in stg_ 
# but should be in int_ or mart_. 
"""
data_meteofrance.stg_mensq_pluviometrie
data_meteofrance.stg_mensq_temperatures
data_meteofrance.histo_simu_ann
data_meteofrance.histo_simu_geo

MENS_meteofrance.stations
MENS_meteofrance.stations_zones
MENS_meteofrance.Table_NBJTXS32_ANNEE
MENS_meteofrance.Table_sim_2100
"""