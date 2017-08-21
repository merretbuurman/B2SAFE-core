'''
Helper functions to find the irods_environment.json 
file that is needed to run some tests.

Author: Merret Buurman (DKRZ), 2017
'''

import os
import json

HOME = os.path.expanduser("~")
IRODS_INSTALL_DIR = '/var/lib/irods' # TODO - any better way of getting this?
TEST_RESOURCES_PATH = '../tests/resources'
ENV_FILENAME = 'irods_environment.json'
HIDDEN_DIR = '.irods'


# Three locations where to find irods_environment.json files:
'''
irods_environment.json file from the current user.
If the current user is not the irods admin user, this
file may lack some information.
'''
USER_FILE_PATH = os.path.join(HOME, HIDDEN_DIR, ENV_FILENAME)

'''
irods_environment.json file of the iRODS admin user.
This is probably not accessible by the user running this
script.
'''
GLOBAL_FILE_PATH = os.path.join(IRODS_INSTALL_DIR, HIDDEN_DIR, ENV_FILENAME)

'''
irods_environment.json file of the iRODS admin user, copied into 
the test-resources directory and with modified permissions.
'''
GLOBAL_FILE_PATH_RESOURCES = os.path.join(TEST_RESOURCES_PATH, ENV_FILENAME)


'''
Return a dictionary with relevant iRODS environment variables.
May be combined of the current user's environment file and
the global environment file.
'''
def get_environment(required_entries):
    jsonfile1 = get_user_environment_file()
    print("\nINFO: environment from current user: "+str(jsonfile1))
    try:
        check_json_content(jsonfile1, required_entries)
        jsonfilecontent = jsonfile1
    except ValueError:
        # if any are missing, take them from global environment file:
        jsonfile2 = get_main_environment_file()
        jsonfilecontent = enrich_environment_with_additional_info_ONLYREQUIRED(jsonfile1, jsonfile2, required_entries)
        modify_irods_home(jsonfilecontent, jsonfile1)
        check_json_content(jsonfilecontent, required_entries)
    print("INFO: environment used for tests:    "+str(jsonfilecontent))
    return jsonfilecontent

def read_json_file(path_with_filename):
    return json.loads(open(path_with_filename, 'r').read())

def get_user_environment_file():
    return read_json_file(USER_FILE_PATH)

'''
Iterate over various directories, look for the irods_environment.json 
file. Return the irods_environment file or an empty dictionary,
if no file is found.
'''
def get_main_environment_file():
    filepaths = [GLOBAL_FILE_PATH, GLOBAL_FILE_PATH_RESOURCES]

    jsonfile = None
    for filepath in filepaths:
        if jsonfile is None:
            try:
                jsonfile = read_json_file(filepath)
            except IOError as e:
                pass
    
    if jsonfile is None:
        jsonfile = {}
    return jsonfile

'''
Check if all necessary entries are in the current
environment dictionary.
'''
def check_json_content(jsonfilecontent, required_entries):
    for req in required_entries:
        if req not in jsonfilecontent:
            raise ValueError("Missing value '"+req+"' in irods_environment.json")

'''
This completes the irods_environment dictionary by adding
from the additional_dict those key-value-pairs that did were
missing in the irods_environment dictionary AND that are
required.
It returns a new dictionary.
'''
def enrich_environment_with_additional_info_ONLYREQUIRED(environment_dict, additional_dict, required_entries):
    finaldict = environment_dict.copy()
    for key in required_entries:
        if not key in finaldict:
            finaldict[key] = additional_dict[key]
    return finaldict

'''
This completes the irods_environment dictionary by adding
from the additional_dict those key-value-pairs that did were
missing in the irods_environment dictionary.
It returns a new dictionary.
'''
def enrich_environment_with_additional_info_FULL(environment_dict, additional_dict):
    finaldict = additional_dict.copy()
    finaldict.update(environment_dict)
    return finaldict

'''
The user environment file does not contain the zone name, but
the global environment file contains the wrong one, so it 
has to be adapted. 
TODO: This is somehow a dirty hack.
'''
def modify_irods_home(finaldict, original_environment_dict):
    zone = original_environment_dict['irods_zone_name']
    user = original_environment_dict['irods_user_name']
    irods_home = '/'+zone+'/home/'+user
    if not irods_home == finaldict['irods_home']:
        print("INFO: Replacing '"+finaldict['irods_home']+"' with '"+irods_home+"'.")
        finaldict['irods_home'] = irods_home