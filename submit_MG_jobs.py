import os
import random
import time
import glob
from optparse import OptionParser

working_path = '/afs/cern.ch/user/s/ssenkin/workspace/private/MadGraph/MG5_aMC_v2_5_5'
output_path_for_results = working_path + '/output_JSON/'

mDM = 1
mediator_masses = [1000, 1500, 2000, 2500, 3000]
#a_r_couplings = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
a_r_couplings = [0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34]
#g_couplings = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]
g_couplings = [0.1, 0.5, 1.0]
processes = ['tt_exclusive', 'onshellV', 'offshellV', 'monotop']

def prepare_tarball():
    # Create output directory if it is not there
    os.system("mkdir -p " + output_path_for_results)
    
    # Create the tarball if it does not exist and move to working path
    if not os.path.isfile(working_path + '/tarball.tar.gz'):
        print 'Creating a tarball of ' + working_path
        os.system("tar -cvzf tarball.tar.gz " + working_path)
        os.system("mv tarball.tar.gz " + working_path + "/")
    else:
        print 'Tarball already exists: ' + working_path + '/tarball.tar.gz, will use this one.\n'
    return


def submit_job(signal, option):
    # Script name and working dir name
    foutname = "this_run" + "_" + signal + '_' + option.replace(" ","_").replace("-","").replace("=","").replace(",","").replace(":","_").replace('*','') + ".sh" # last replace to avoid having a * in file name
    workdir  = "tmp_dir_" + signal + '_' + str(time.time()) + `random.randint(0, 1000000)`

    # Outputdir
    outputdir = output_path_for_results + "/"
    os.system("mkdir -p " + outputdir)
    os.system("mkdir -p " + outputdir + '/logs')

    # Create the bash script to be submitted
    fout = open(foutname,"w")
    fout.write('#!/bin/bash\n')
    fout.write('source /etc/profile\n')
    fout.write('# Working area\n')
    fout.write('echo running on $HOSTNAME\n')
    fout.write('RandomDirectory='+workdir+'\n')
    fout.write('WorkingDirectory=work_${RandomDirectory}\n')
    fout.write('mkdir -p $WorkingDirectory\n')
    fout.write('cd $WorkingDirectory\n')
    fout.write('\n')
    fout.write('# Grab the code\n')
    fout.write('cp -f ' + working_path + '/tarball.tar.gz .\n')
    fout.write('tar -xzvf tarball.tar.gz\n')
    fout.write('echo "untaring done!"\n')
    fout.write('cd ' + working_path[1:] + '\n') # [1:] to remove the first character, which is '/'. That way, we stay in the temporary directory.
    fout.write('ls\n')
    fout.write('\n')
    fout.write('echo "setup done"\n')
    fout.write('\n')
    fout.write('# Create the config file for the studied signal, and run MG\n')
    fout.write('python calculate_MG_xsection.py -s ' + signal + ' ' + option+'\n')
    fout.write('\n')
    fout.write('# Copy outputs  \n')
    fout.write('cp -rf output_JSON/* ' + outputdir + '/.\n')
    fout.write('cp -rf workspace/*out ' + outputdir + '/logs/.\n')
    fout.write('cd ' + working_path + '\n')
    fout.write('rm -rf ${WorkingDirectory}\n')
    fout.close();

    #Launch the batch job command
    os.system("chmod +x " + foutname)
    os.system("bsub -q 8nm " + os.path.abspath(foutname) )
    return

def resubmit_job(process, mV, mDM, a_r, g):
    filename = output_path_for_results + process + '_mV%.0f_mDM%.0f_a_r%.2f_g%.2f.txt' % (mV, mDM, a_r, g)
    job_resubmitted = False
    if not os.path.isfile(filename):
        foutname = "this_run" + "_" + process + '_a_' + str(a_r) + '_M_' + str(mV) + '_g_' + str(g) + '.sh'
        print 'File ' + filename.replace(output_path_for_results,'') + ' does not exist, resubmitting job with command ' + "bsub -q 1nh " + os.path.abspath(foutname)
        os.system("bsub -q 1nh " + os.path.abspath(foutname) )
        job_resubmitted = True
    return job_resubmitted

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-r", "--resubmit", action = "store_true", dest = "resubmit",
                      help = "Resubmit jobs with no output/" )

    ( options, args ) = parser.parse_args()

    if not options.resubmit:
        prepare_tarball()

    all_jobs_done = True
    job_counter = 0

    for process in processes:
        for mV in mediator_masses:
            for a_r in a_r_couplings:
                for g in g_couplings:
                    if options.resubmit:
                        job_resubmitted = resubmit_job(process, mV, mDM, a_r, g)
                        if job_resubmitted:
                            job_counter += 1
                            all_jobs_done = False
                    else:
                        submit_job(process, '-a ' + str(a_r) + ' -M ' + str(mV) + ' -g ' + str(g))
                        job_counter += 1
    
    if options.resubmit and all_jobs_done:
        print 'All jobs seem to have correct output, no jobs resubmitted.'
    else:
        print 'Number of submitted jobs: ' + str(job_counter)
