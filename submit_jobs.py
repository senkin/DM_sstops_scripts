import os
import random
import time
import glob

working_path = '/afs/cern.ch/user/s/ssenkin/workspace/private/MadGraph/MG5_aMC_v2_5_5'
output_path_for_results = working_path + '/output_JSON/'

branching_ratios = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.99]
mediator_masses = [1000, 1500, 2000, 2500, 3000]
a_r_couplings = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
processes = ['tt_exclusive', 'onshellV', 'offshellV', 'monotop']

#====================================
def prepare_tarball():
#====================================
    # Create output directory and clean up if exists
    os.system("mkdir -p " + output_path_for_results)
    #os.system("rm -f " + output_path_for_results + "/*")
    
    # Create the tarball and move to working path
    os.system("tar -cvzf tarball.tar.gz " + working_path)
    os.system("mv tarball.tar.gz " + working_path + "/")
    return


#===============================
def submit_job(signal, option):
#===============================

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

if __name__ == '__main__':
    prepare_tarball()
    
    for process in processes:
        for mV in mediator_masses:
            for a_r in a_r_couplings:
                for BR in branching_ratios:
                    submit_job(process, '-a ' + str(a_r) + ' -M ' + str(mV) + ' -B ' + str(BR))
