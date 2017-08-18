import numpy as np
import os, sys
from optparse import OptionParser
from cross_sections_DM import *
from copy import copy
import ROOT

gcd = ROOT.gROOT.cd

processes = ['tt_exclusive', 'ttu_onshellV', 'ttu_offshellV']

# Nominal model parameters
mediator_masses = [1000, 1500, 2000, 2500, 3000]
mDM = 1.

def make_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            print "Could not create a folder ", folder

def reweight_root_file(mV, process, data):
    global output_folder, systematics
    root_file_prefix = 'sstops_'
    if systematics:
        root_file_prefix = 'SystVar_sstops_'

    # slice in columns
    a_r = data[:,2]
    g = data[:,3]
    if 'tt_excl' in process:
        xsection = data[:,9]
        MC_cross_section = cross_sections_tt_excl[str(mV)]
    elif 'onshell' in process:
        xsection = data[:,8]
        MC_cross_section = cross_sections_onshellV[str(mV)]
    elif 'offshell' in process:
        xsection = data[:,7]
        MC_cross_section = cross_sections_offshellV[str(mV)]
    else:
        print 'Unknown process: ', process
        sys.exit(1)

    weights = xsection/MC_cross_section

    input_root_file = ROOT.TFile(input_folder + '/' + root_file_prefix + process + '_mV' + str(mV) + '.root', "read")

    for i in range(len(weights)):
        weight_suffix = '_a_r%.2f_g%.2f' % (a_r[i], g[i])
        # create the new root file with reweighted histograms
        reweighted_root_file = ROOT.TFile(output_folder + '/' + root_file_prefix + process + '_mV' + str(mV) + weight_suffix + '.root', "recreate")

        # get the histograms from the input root file
        for instance in input_root_file.GetListOfKeys():
            histogram = input_root_file.Get(instance.GetName())
            histogram_weighted = histogram.Clone()
            histogram_weighted.Scale(weights[i])
            histogram_weighted.Write(instance.GetName())

        reweighted_root_file.Close()

    input_root_file.Close()

def sum_files(mV, data):
    global output_folder, systematics
    root_file_prefix = 'sstops_'
    if systematics:
        root_file_prefix = 'SystVar_sstops_'
    
    # slice in columns
    a_r = data[:,2]
    g = data[:,3]

    first_file_name = output_folder + '/' + root_file_prefix + processes[0] + '_mV' + str(mV) + '_a_r{0:.2f}'.format(a_r[0]) + '_g{0:.2f}'.format(g[0]) + '.root'
    first_file = ROOT.TFile(first_file_name, "read")
    list_of_histograms = [histogram.GetName() for histogram in first_file.GetListOfKeys()]
    first_file.Close()

    for i in range(len(a_r)):
        weight_suffix = '_a_r%.2f_g%.2f' % (a_r[i], g[i])

        histograms_dict = {}

        for process in processes:
            reweighted_root_file = ROOT.TFile(output_folder + '/' + root_file_prefix + process + '_mV' + str(mV) + weight_suffix + '.root', "read")
            # print 'Reading from file ', output_folder + '/' + root_file_prefix + process + '_mV' + str(mV) + weight_suffix + '.root'
            gcd()
            
            # sum the histograms and place in dictionary
            for histogram_name in list_of_histograms:
                histogram = reweighted_root_file.Get(histogram_name)
                if histogram_name in histograms_dict:
                    histograms_dict[histogram_name] += copy(histogram.Clone())
                else:
                    histograms_dict[histogram_name] = copy(histogram.Clone())

            reweighted_root_file.Close()

        # write histograms
        summed_root_file = ROOT.TFile(output_folder + '/' + root_file_prefix + 'mV' + str(mV) + weight_suffix + '.root', "recreate")
        # print 'Creating file ', output_folder + '/' + root_file_prefix + 'mV' + str(mV) + weight_suffix + '.root'
        for histogram_name in list_of_histograms:        
            histograms_dict[histogram_name].Write(histogram_name)

        summed_root_file.Close()

def clean_up_files():
    global output_folder, systematics
    root_file_prefix = 'sstops_'
    if systematics:
        root_file_prefix = 'SystVar_sstops_'

    for process in processes:
         os.system("rm " + output_folder + '/' + root_file_prefix + process + '*.root')


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'reweighted_sstop_files/',
                  help = "set path to save weighted root files" )
    parser.add_option( "-i", "--input_folder", dest= "input_folder", default = '../',
                  help = "set path with input root files to reweight" )
    parser.add_option( "-s", "--syst", action = "store_true", dest = "systematics",
                      help = "Reweight systematic variations (SystVar_*.root)" )
    parser.add_option( "-k", "--keep_subprocesses", action = "store_true", dest = "keep_subprocesses",
                      help = "Keep reweighted root files for all subprocesses" )
    parser.add_option( "-c", "--clean_up_subprocesses", action = "store_true", dest = "clean_up_subprocesses",
                      help = "Only clean up reweighted root files for all subprocesses" )

    ( options, args ) = parser.parse_args()

    output_folder = options.output_folder
    make_folder_if_not_exists(output_folder)

    input_folder = options.input_folder
    systematics = options.systematics

    if options.clean_up_subprocesses:
        print 'Cleaning up reweighted subrpocess files...'
        clean_up_files()
        print 'Done.'
        sys.exit(0)

    whole_data = np.genfromtxt('big_table.csv', delimiter=',')
    #delete first row (variable names)
    whole_data = np.delete(whole_data, (0), axis=0)

    # work with a single mV:
    for mV in mediator_masses:
        single_mV_data = whole_data[whole_data[:,5]==mV]
        for process in processes:
            reweight_root_file(mV, process, single_mV_data)
        sum_files(mV, single_mV_data)

    if not options.keep_subprocesses:
        clean_up_files()



