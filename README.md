# Dark Matter same-sign top quark pair scrips
==================

Scripts for generic Dark Matter analysis in the context of same-sign tops.

## Guidelines

### Main scripts
* calculate_MG_xsection.py: this script creates a MadGraph configuration file, runs [MadGraph](https://launchpad.net/mg5amcnlo) and outputs the calculated quantities for a given process
* submit_MG_jobs.py: this script submits batch jobs (normally on lxplus) for a set of parameters, using the script above for each point
* make_results_table.py: this script creates a csv table with all the results (including cross-sections) from the MadGraph jobs' output
* reweight_sstop_files.py: this script uses the csv table from the previous step to reweight the signal histograms used by TRexFitter
* make_plots.py: a plotting script. Please specify the input folder with the limit files (../LimitsOutput/FullMC_BlindExp/) as an input parameter -i (or inside the script)

### Additional files
* ParameterSpace.py: a parameter space class used in the calculate_MG_xsection.py script
* big_table.csv: pre-calculated table made by make_results_table.py script. It can be used to directly reweight the histograms, skipping all the previous steps.
* MonotopDMF_UFO.tar.gz: the Dark Matter model used by MadGraph

Dependencies
==================
[ROOT](http://root.cern.ch) >=5.30

[MadGraph](https://launchpad.net/mg5amcnlo) >=2.5.1

[freetype](http://www.freetype.org) and other matplotlib dependencies