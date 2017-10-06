import sys
import json, csv
from optparse import OptionParser
from os import listdir
from os.path import isfile, join

def read_data_from_JSON(JSON_input_file):
    input_file = open(JSON_input_file, 'r')
    input_JSON = ''.join(input_file.readlines())
    data = json.loads(input_JSON)
    input_file.close()
    return data

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-i", "--input_path", dest = "input_path", default = 'output_JSON',
                  help = "Set the path where all the JSON files with results are stored (default: output_JSON)" )

    ( options, args ) = parser.parse_args()

    input_path = options.input_path + '/'

    list_of_files = [f for f in listdir(input_path) if isfile(join(input_path, f))]

    print 'Found', len(list_of_files), 'files in input directory', input_path

    initial_dict = {}
    common_dictionary = {}

    for file in sorted(list_of_files):
    	dictionary = read_data_from_JSON(input_path + file)
    	process = dictionary['process']
    	try:
    		initial_dict[process]
    	except:
    		initial_dict[process] = {}
    	for key in dictionary.keys():
    		if not "process" in key and not "m_top" in key:
    			try:
    				initial_dict[process][key].append(dictionary[key])
    			except:
    				initial_dict[process][key] = []
    				initial_dict[process][key].append(dictionary[key])

    # initialise the common dictionary
    for process in initial_dict.keys():
    	common_dictionary['xsection_' + process] = []

    first_dict_key = next(iter(initial_dict))
    available_sub_keys = initial_dict[first_dict_key].keys()
    for key in available_sub_keys:
        if not "xsection" in key and not "m_top" in key:
            common_dictionary[key] = []

    number_of_points = len(initial_dict[first_dict_key]['xsection'])
    for i in range(number_of_points):
        for key in available_sub_keys:
            value = initial_dict[first_dict_key][key][i]
            value = round(value, 6)
            if not "xsection" in key and not "m_top" in key:
                common_dictionary[key].append(value)
        for process in initial_dict.keys():
            common_dictionary['xsection_' + process].append(initial_dict[process]['xsection'][i])

    keys_to_write = sorted(common_dictionary.keys())
    with open('big_table.csv', 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(keys_to_write)
		writer.writerows(zip(*[common_dictionary[key] for key in keys_to_write]))
