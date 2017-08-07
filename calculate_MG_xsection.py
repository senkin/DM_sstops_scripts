# this script creates a MadGraph configuration file, runs Madgraph and outputs the calculated quantities for a given process

import sys, os
import json
import copy
import subprocess as sp
import string
import numpy as np
import math
from optparse import OptionParser
from ParameterSpace import ParameterSpace

from time import time

class Timer():
    def __init__(self):
        self.start_time =  time()
    def elapsed_time(self):
        return time() - self.start_time
    def restart(self):
        self.start_time =  time()

madgraph_executable = './bin/mg5_aMC'

def make_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            print "Could not create a folder ", folder

def write_data_to_JSON(data, JSON_output_file, indent = True):
    output_file = open(JSON_output_file, 'w')
    if indent:
        output_file.write(json.dumps(data, indent=4, sort_keys = True))
    else:
        output_file.write(json.dumps(data, sort_keys = True))
    output_file.close()


def create_MG_config(subprocess, parameters, auto_width = True):
	global workspace_path
	name = workspace_path + subprocess + '_' + parameters.parameter_space_name()
	filename = name + '.dat'
	file = open(filename,'w')
	file.write('#************************************************************\n')
	file.write('#*                        MadGraph 5                        *\n')
	file.write('#*                                                          *\n')
	file.write('#*                *                       *                 *\n')
	file.write('#*                  *        * *        *                   *\n')
	file.write('#*                    * * * * 5 * * * *                     *\n')
	file.write('#*                  *        * *        *                   *\n')
	file.write('#*                *                       *                 *\n')
	file.write('#*                                                          *\n')
	file.write('#*                                                          *\n')
	file.write('#*    The MadGraph Development Team - Please visit us at    *\n')
	file.write('#*    https://server06.fynu.ucl.ac.be/projects/madgraph     *\n')
	file.write('#*                                                          *\n')
	file.write('#************************************************************\n')
	file.write('#*                                                          *\n')
	file.write('#*        This is an auto-generated file for MadGraph 5     *\n')
	file.write('#*                                                          *\n')
	file.write('#*     run as ./bin/mg5  filename                           *\n')
	file.write('#*                                                          *\n')
	file.write('#************************************************************\n')
	file.write('set automatic_html_opening False\n')
	file.write('import model models/MonotopDMF_UFO -modelname\n')
	file.write('define j = g u c d s b u~ c~ d~ s~ b~\n')
	file.write('define l+ = e+ mu+ ta+\n')
	file.write('define l- = e- mu- ta-\n')
	file.write('define vl = ve vm vt\n')
	file.write('define vl~ = ve~ vm~ vt~\n')
	file.write('\n')
	if 'tt_excl' in subprocess:
		file.write('# tt exclusive decay\n')
		file.write('generate p p > t t, (t > b W+, W+ > l+ vl)\n')
		file.write('add process p p > t~ t~, (t~ > b~ W-, W- > l- vl~)\n')
		file.write('\n')
	elif 'onshell' in subprocess:
		file.write('# Visible on-shell V decay\n')
		file.write('generate p p > V > t t u~, (t > b W+, W+ > l+ vl)\n')
		file.write('add process p p > V > t~ t~ u, (t~ > b~ W-, W- > l- vl~)\n')
		file.write('\n')
	elif 'offshell' in subprocess:
		file.write('# Off-shell V decay\n')
		file.write('generate p p > t t u~ $$ V, (t > b W+, W+ > l+ vl)\n')
		file.write('add process p p > t~ t~ u $$ V, (t~ > b~ W-, W- > l- vl~)\n')
		file.write('\n')
	elif 'Monotop' in subprocess or 'monotop' in subprocess:
		file.write('# Monotop\n')
		file.write('generate p p > t psi psibar, (t > b W+, W+ > l+ vl)\n')
		file.write('add process p p > t~ psi psibar, (t~ > b~ W-, W- > l- vl~)\n')
		file.write('\n')

	file.write('# Output processes to MadEvent directory\n')
	file.write('output %s\n' % name)
	file.write('\n')
	file.write('launch %s\n' % name)
	file.write('set Mpsi %e # changing the psi mass\n' % parameters.mDM)
	file.write('set ar %e # changing the a_r coupling constant\n' % parameters.a_r)
	file.write('set gg %e # changing the gg coupling constant\n' % parameters.g)
	file.write('set MV %e # changing the V mass\n' % parameters.mV)
	if auto_width:
		file.write('set WV Auto # changing the V width\n')
	else:
		file.write('set WV %e # changing the V width\n' % parameters.G_tot)
	file.write('launch %s -i\n' % name)
	file.write('print_results --path=%s.txt --format=short\n' % name)

	file.close

def run_MG_config(subprocess, parameters, auto_width = True):
	global workspace_path
	name = workspace_path + subprocess + '_' + parameters.parameter_space_name()
	config_filename = name + '.dat'
	output_filename = name + '.out'
	output_file = open(output_filename,'w')
	print 'Executing command: ', madgraph_executable + ' ./' + config_filename
	print 'Output file: ', output_filename
	run = sp.Popen([madgraph_executable, config_filename], cwd='./', stdout=output_file)
	run.communicate()
	output_file.close

def read_MG_output(subprocess, parameters, auto_width = True):
	global workspace_path, output_path
	name = workspace_path + subprocess + '_' + parameters.parameter_space_name()
	output_banner_filename = name + '/Events/run_01/run_01_tag_1_banner.txt'
	output_banner = open(output_banner_filename,'r')

	# new parameters instance for MG-calculated quantities
	parameters = ParameterSpace()

	# parse the output for numbers
	for line in output_banner.readlines():
		columns = string.split(line)
		if '# ar' in line:
			parameters.set_a_r(columns[1])
		if '# gg' in line:
			parameters.set_g(columns[1])
		if '# mv' in line:
			parameters.set_mV(columns[1])
		if '# mpsi' in line:
			parameters.set_mDM(columns[1])
		if 'DECAY  32' in line:
			parameters.set_G_tot(columns[2])
		if '1000023  -1000023' in line:
			parameters.set_BR(columns[0])
		if 'Integrated weight (pb)' in line:
			cross_section = float(columns[-1])

	output_banner.close

	print '*'*100
	print 'MadGraph calculated quantities:'
	parameters.print_initial_parameters()
	print '='*100
	print 'Calculated cross-section [pb] = ', cross_section

	data_to_write = copy.copy(parameters.__dict__)
	data_to_write['xsection'] = cross_section
	data_to_write['process'] = subprocess
	JSON_file_name = output_path + subprocess + '_' + parameters.parameter_space_name() + '.txt'
	write_data_to_JSON(data_to_write, JSON_file_name)
	print 'Data written into JSON file ', JSON_file_name

	return parameters


if __name__ == '__main__':
    timer = Timer()
    timer_value = timer.elapsed_time()

    parser = OptionParser()
    parser.add_option( "-o", "--output_path", dest = "output_path", default = 'output_JSON',
                  help = "Set the output path where all the JSON files with results are stored (default: output_JSON)" )
    parser.add_option( "-w", "--workspace_path", dest = "workspace_path", default = 'workspace',
                  help = "Set the workspace path where all the MG files are stored (default: workspace)" )
    parser.add_option( "-M", "--mV", dest = "mV", default = 2000,
                  help = "Set the mediator mass (mV), default: 2000 GeV" )
    parser.add_option( "-m", "--mDM", dest = "mDM", default = 1,
                  help = "Set the DM candidate mass (mDM), default: 1 GeV" )
    parser.add_option( "-a", "--a_r", dest = "a_r", default = 0.5,
                      help = "Set the a_r coupling constant (V_tu vertex)" )
    parser.add_option( "-g", "--g", dest = "g", default = '',
                      help = "Set the g coupling constant (V_chi_chi vertex)" )
    parser.add_option( "-G", "--total_width", dest = "total_width", default = '',
                      help = "Set the total width in GeV (default - automatic)" )
    parser.add_option( "-B", "--BR", dest = "BR", default = '',
                      help = "Set the invisible BR (default - automatic)" )
    parser.add_option( "-s", "--signal", dest = "signal", default = 'tt_exclusive',
                  help = "Choose the signal of interest. Default: tt_exclusive (prompt tt production), alternatively ttu_offshellV, ttu_onshellV, monotop" )

    ( options, args ) = parser.parse_args()

    workspace_path = options.workspace_path + '/'
    make_folder_if_not_exists(workspace_path)

    output_path = options.output_path + '/'
    make_folder_if_not_exists(output_path)

    current_process = options.signal

    if not options.g and not options.total_width and not options.BR:
        print 'Insufficient input parameters, please enter the total width (G), branching ratio (BR) or the g coupling constant (g).'
        sys.exit(1)

    parameters = ParameterSpace()

    parameters.set_mV(options.mV)
    parameters.set_mDM(options.mDM)
    parameters.set_a_r(options.a_r)

    auto_width = True
    if options.total_width:
    	auto_width = False

    if options.g:
    	parameters.set_g(options.g)

    if options.BR:
    	parameters.set_BR(options.BR)

    if options.total_width:
        parameters.set_G_tot(options.total_width)

    print 'Input parameters:'
    parameters.print_initial_parameters()
    parameters.calculate_all()
    print '*'*100
    print 'Analytically calculated parameters:'
    parameters.print_calculated_parameters()

    print '.'*100

    print 'Creating the new MadGraph config for %s process.' % current_process
    create_MG_config(current_process, parameters, auto_width)
    
    run_MG_config(current_process, parameters, auto_width)
    print 'Runtime for process %s, parameter set %s : %.1f min' % (current_process, parameters.parameter_space_name(), (timer.elapsed_time()-timer_value)/60)
    
    timer_value = timer.elapsed_time()
    
    MG_calculated_parameters = read_MG_output(current_process, parameters, auto_width)

    if parameters!=MG_calculated_parameters:
    	print 'ERROR: analytically calculated parameters do not match with MadGraph calculated ones.'
    	print 'Analytical parameters: ', parameters.__dict__
    	print 'MG-calculated parameters: ', MG_calculated_parameters.__dict__
    	sys.exit(1)
