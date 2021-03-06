# Dark Matter same-sign top quark pair scrips
==================

Scripts for generic Dark Matter analysis in the context of same-sign tops.
Combination with monotop analysis is probed: [link](https://cds.cern.ch/record/2294626) to the internal note.
The repository has been moved to an [internal repository](https://:@gitlab.cern.ch:8443/atlas-clermont/DM_sstops.git) for later development.

## Guidelines

### Main scripts
* calculate_MG_xsection.py: this script creates a MadGraph configuration file, runs [MadGraph](https://launchpad.net/mg5amcnlo) and outputs the calculated quantities for a given process. Normally runs from the MadGraph directory.
* submit_MG_jobs.py: this script submits batch jobs (normally on lxplus) for a set of parameters, using the script above for each point
* make_results_table.py: this script creates a csv table with all the results (including cross-sections) from the MadGraph jobs' output
* reweight_sstop_files.py: this script uses the csv table from the previous step to reweight the signal histograms used by TRexFitter
* make_plots.py: a plotting script. Please specify the input folder with the limit files as an input parameter -i (or inside the script)

### Additional files
* ParameterSpace.py: a parameter space class used in the calculate_MG_xsection.py script
* parameter_tables/*.csv: pre-calculated tables made by make_results_table.py script. It can be used to directly reweight the histograms, skipping all the previous steps.
* MonotopDMF_UFO.tar.gz: the Dark Matter model used by MadGraph

### Quick recipe
If you only want to make the plots using the existing limits output:

```
# get the code from the repository
git clone https://github.com/senkin/DM_sstops_scripts
cd DM_sstops/scripts

# set up environment (using virtualenv for python):
source setup.sh

# make some plots (change input paths to the limit files accordingly)
python make_plots.py

# make some more plots
python make_plots.py -a

```

Recipe to create the MadGraph parameter tables output:
```
# download [MadGraph](https://launchpad.net/mg5amcnlo), for example
wget https://launchpad.net/mg5amcnlo/2.0/2.5.x/+download/MG5_aMC_v2.5.5.tar.gz
tar xvf MG5_aMC_v2.5.5.tar.gz

# get the code from the repository and copy to the MadGraph working directory
git clone https://github.com/senkin/DM_sstops_scripts
cp DM_sstops/scripts/* MG5_aMC_v2_5_5/
cd MG5_aMC_v2_5_5

# untar the DM model
tar xvf MonotopDMF_UFO.tar.gz
mv MonotopDMF_UFO models/

# try the calculate_MG_xsection.py script
python calculate_MG_xsection.py -g 0.5

# submit the MG jobs (on lxplus), change the working_path variable in it before running
python submit_MG_jobs.py

# resubmit failed jobs after some time
python submit_MG_jobs.py -r

# make the results table (change input path accordingly)
python make_results_table.py

```

### Reweighting the histogram files for limits
The reweight_sstop_files.py file is meant to be run from the LimitCalculation package as it requires the histograms that it creates on input.
More info on its usage in the Readme [here](https://svnweb.cern.ch/trac/atlasphys-exo/browser/Physics/Exotic/HQT/SameSignLeptonsPlusBJets/Run2/Code/LimitCalculation/trunk/README).


Dependencies
==================
[ROOT](http://root.cern.ch) >=5.30

[MadGraph](https://launchpad.net/mg5amcnlo) >=2.5.1

[freetype](http://www.freetype.org) and other matplotlib dependencies