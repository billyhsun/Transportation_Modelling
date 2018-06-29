from __future__ import division
import time, math, csv
import inro.modeller as _m
import traceback as _traceback
from inro.emme.matrix import MatrixData as _MatrixData

_MODELLER = _m.Modeller() #Instantiate Modeller once.
_util = _MODELLER.module('tmg.common.utilities')
_tmgTPB = _MODELLER.module('tmg.common.TMG_tool_page_builder')
_bank = _MODELLER.emmebank


## Current Version: 1.2

'''
# Version 1.1
## Class structures for trie implementation
class Node:
    def __init__(self, label=None, data=None):
        self.label = label
        self.data = data
        self.children = dict()
    
    def addChild(self, key, data=None):
        if not isinstance(key, Node):
            self.children[key] = Node(key, data)
        else:
            self.children[key.label] = key

    def count_total_paths(self):
        count = 0
        current_node = self
        if current_node == {} or current_node == None:
            return count
        
        elif current_node.children.has_key("count") == True and len(current_node.children) == 1:
            count += current_node.children["count"].data
            return count
        
        elif current_node.children.has_key("count") == True and len(current_node.children) > 1:
            count += current_node.children["count"].data
            for key, val in current_node.children.items():
                if key != "count":
                    count += val.count_total_paths()
            return count
        
        else:
            for key, val in current_node.children.items():
                count += val.count_total_paths()
            return count

    def __getitem__(self, key):
        return self.children[key]


class Trie:
    def __init__(self):
        self.head = Node()
    
    def __getitem__(self, key):
        return self.head.children[key]
    
    def add(self, path):
        current_node = self.head
        finished = True

        if self.has_path(path) == False: # Add the path, as well as a count of 1 at the end
            for i in range(len(path)):
                if path[i] in current_node.children:
                    current_node = current_node.children[path[i]]
                else:
                    finished = False
                    break 
            
            if not finished:
                while i < len(path):
                    current_node.addChild(path[i])
                    current_node = current_node.children[path[i]]
                    i += 1
            
            current_node.data = path
            current_node.addChild("count", 1)    

        else: # Trace the path to its end and add 1 to the count
            for i in range(len(path)):
                if path[i] in current_node.children:
                    current_node = current_node.children[path[i]]
                else:
                    finished = False
                    break 
            
            if not finished:
                while i < len(path):
                    current_node = current_node.children[path[i]]
                    i += 1

            current_node.children["count"].data += 1 # Add 1 to the count

            
    def has_path(self, path):
        if path == [] or path == '':
            return False
        if path == None:
            raise ValueError('Trie.has_word requires a not-Null list')
        
        current_node = self.head
        exists = True
        for segment in path:
            if segment in current_node.children:
                current_node = current_node.children[segment]
            else:
                exists = False
                break
        if exists:
            if current_node.children.has_key("count") == False:
                exists = False
            if current_node.data == None:
                exists = False
        return exists


    def count_path(self, path):
        if self.has_path(path) == False:
            return 0
        else:
            current_node = self.head
            i = 0
            j = len(path)
            for segment in path:
                if i < j:
                    if current_node.children.has_key("count") == True and len(current_node.children) == 1:
                        break
                    else:
                        current_node = current_node.children[segment]
                        i += 1
                else:
                    break
        return current_node.children["count"].data
'''

## Helper functions

# Versions 1.0-1.2
def convert_id (filename):
    # EMME ID to TTS ID
    EMME2TTS = {}
    with open(filename, 'r') as file:
        data = file.readlines()

    for line in data:
        line = line.split(',')
        line[-1] = line[-1].rstrip()
        EMME2TTS[line[0]] = line[1]

    return EMME2TTS


def read_obs_paths (filename): # Creates a dictionary of lists for each O-D pair
    with open(filename, 'r') as file:
        data = file.readlines()

    obs_paths = {}

    for line in data:
        line = line.split(',')
        line[-1] = line[-1].rstrip()

        if line[0] == "OriginZone" or line[2] != 'W' or line[3] != 'W':
            continue

        key = (int(line[0]), int(line[1])) # Orig, Dest

        path = []
        for i in range (len(line)):
            if i < 8 or line[i] == '0':
                continue
            if line[i] == 'T593' or line[i] == 'T594':
                line[i] = 'T595' 
            path.append(line[i])

        if obs_paths.has_key(key) == False:
            obs_paths[key] = [path]
        else:
            obs_paths[key].append(path)
        
    return obs_paths


'''
# Version 1.0
def read_EMME_paths(filename):
    # Open and read file
    with open(filename, "r") as file:
        content = file.readlines()

    # Transportation modes
    aux_transit_modes = ['a', 'k', 't', 'u', 'v', 'w', 'y']
    transit_modes = ['b', 'g', 'l', 'm', 'p', 'q', 'r', 's']

    # Organize the data
    path_details = {}

    for line in content:
        line = line.split(" ")
        for item in line:
            if item == "":
                line.remove(item)
        line[-1] = line[-1].rstrip()

        if line[0] == "c" or len(line) < 2:
            continue

        key = (int(line[0]), int(line[1]))
        
        i = 0
        transit_routes = []
        while i < (len(line)-1):
            if line[i] in transit_modes:
                line[i+1] = line[i+1][1:-1]
                transit_routes.append(line[i+1])
                i += 3
                continue
            elif line[i] in aux_transit_modes:
                i += 3
                continue
            else:
                i += 1
                continue
            
        for i in range (len(transit_routes)):
            if EMME2TTS.has_key(transit_routes[i]): # Convert from EMME ID to TTS ID
                transit_routes[i] = EMME2TTS[transit_routes[i]]

        if path_details.has_key(key) == False:
            path_details[key] = [transit_routes]
        else:
            path_details[key].append(transit_routes)

    return path_details


def compare_paths(EMMEpathDetails, ObservedPaths, EMME2TTS): # Includes hard-coded elements
    count = 0
    no_of_observed_paths = 0
    for key, obs_paths in ObservedPaths.items():
        #if 0 < key[0] <= 1000 and 0 < key[1] <= 1000: # Within Toronto
        #if 1000 < key[0] <= 2000 and 1000 < key[1] <= 2000: # Within Durham
        #if 2000 < key[0] <= 3000 and 2000 < key[1] <= 3000: # Within York
        #if 3000 < key[0] <= 4000 and 3000 < key[1] <= 4000: # Within Peel
        #if 4000 < key[0] <= 5000 and 4000 < key[1] <= 5000: # Within Halton
        #if 5000 < key[0] <= 6000 and 5000 < key[1] <= 6000: # Within Hailton    
            if EMMEpathDetails.has_key(key):
                no_of_observed_paths += len(obs_paths)
                for obs_path in obs_paths:
                    obs_path_in_EMME = False
                    for EMME_path in EMMEpathDetails[key]:
                        if obs_path == EMME_path:
                            obs_path_in_EMME = True
                            break
                        elif (obs_path == ['T595', 'T595'] and EMME_path == ['T595']) or (EMME_path == ['T595', 'T595'] and obs_path == ['T595']):
                            obs_path_in_EMME = True
                            break
                        
                    if obs_path_in_EMME == True:
                        count += 1

    percentage = count / no_of_observed_paths # Closer to 1, the better
    print (percentage)
    return percentage


def compare_path_similarity(EMMEpathDetails, ObservedPaths, EMME2TTS):
    total_percentage = 0.0
    no_of_observed_paths = 0
    for key, obs_paths in ObservedPaths.items():
        #if 0 < key[0] <= 1000 and 0 < key[1] <= 1000: # Within Toronto
        #if 1000 < key[0] <= 2000 and 1000 < key[1] <= 2000: # Within Durham
        #if 2000 < key[0] <= 3000 and 2000 < key[1] <= 3000: # Within York
        #if 3000 < key[0] <= 4000 and 3000 < key[1] <= 4000: # Within Peel
        #if 4000 < key[0] <= 5000 and 4000 < key[1] <= 5000: # Within Halton
        #if 5000 < key[0] <= 6000 and 5000 < key[1] <= 6000: # Within Hailton    
            if EMMEpathDetails.has_key(key):
                no_of_observed_paths += len(obs_paths)
                for obs_path in obs_paths:
                    A = False
                    for EMME_path in EMMEpathDetails[key]:
                        percentages = []
                        # Compare subpaths
                        if obs_path == EMME_path:       
                            A = True
                            break
                        else:
                            n = 0
                            for item in obs_path:
                                if item in EMME_path:
                                    n += 1
                            percent = n/len(obs_path)
                            percentages.append(percent)
                            
                    if A == True:
                        total_percentage += 1.0
                    else:
                        total_percentage += max(percentages)
                            
    percentage = total_percentage / no_of_observed_paths # Closer to 1, the better
    print (percentage)
    return percentage


def calculate_fitness(EMMEpathDetails, ObservedPaths, EMME2TTS, beta):
    fitness = 0.0
    for key, obs_paths in ObservedPaths.items(): 
        if EMMEpathDetails.has_key(key):
            for obs_path in obs_paths:
                A = False
                B = False
                for EMME_path in EMMEpathDetails[key]:       
                    percentages = []

                    # Compare subpaths
                    if obs_path == EMME_path:
                        A = True
                        break
                    if (obs_path == ['T595', 'T595'] and EMME_path == ['T595']) or (EMME_path == ['T595', 'T595'] and obs_path == ['T595']):
                        B = True
                        break

                count = 0        
                if A == True:
                    count = EMMEpathDetails[key].count(obs_path)
                    path_chosen = count / len(EMMEpathDetails[key])
                elif B == True:
                    count = EMMEpathDetails[key].count(['T595'])
                    count += EMMEpathDetails[key].count(['T595', 'T595'])
                    path_chosen = count / len(EMMEpathDetails[key])
                else:
                    path_chosen = 0

                fitness += math.log((path_chosen + beta)/(beta + 1))
                
    print (fitness)
    return fitness
'''

'''
# Version 1.1
def read_EMME_paths(filename, EMME2TTS): # Creates a dictionary of tries for each O-D pair
    # Open and read file
    with open(filename, "r") as file:
        content = file.readlines()

    # Transportation modes
    aux_transit_modes = ['a', 'k', 't', 'u', 'v', 'w', 'y']
    transit_modes = ['b', 'g', 'l', 'm', 'p', 'q', 'r', 's']

    # Organize the data
    path_details = {}
    prev_key = (0, 0)
    path_tree = Trie()

    for line in content:    
        line = line.split(" ")
        for item in line:
            if item == "":
                line.remove(item)
        line[-1] = line[-1].rstrip()

        if line[0] == "c" or len(line) < 2:
            continue

        key = (int(line[0]), int(line[1]))

        if key != prev_key:
            path_details[prev_key] = path_tree
            path_tree = Trie() # If (orig, dest) changes, reinitialize trie

        i = 0
        subpath = []
        while i < (len(line)-1):
            if line[i] in transit_modes:
                line[i+1] = line[i+1][1:-1]
                subpath.append(line[i+1])
                i += 3
                continue
            elif line[i] in aux_transit_modes:
                i += 3
                continue
            else:
                i += 1
                continue

        for i in range (len(subpath)):
            if EMME2TTS.has_key(subpath[i]): # Convert from EMME ID to TTS ID
                subpath[i] = EMME2TTS[subpath[i]]

        path_tree.add(subpath)
        prev_key = key

    path_details[prev_key] = path_tree
    return path_details


def calculate_fitness(EMMEpathDetails, ObservedPaths, fitness_csv_file, beta):
    fitness = 0.0
    for key, obs_paths in ObservedPaths.items(): 
        if EMMEpathDetails.has_key(key):
            for obs_path in obs_paths:
                
                if EMMEpathDetails[key].has_path(obs_path) == True:
                    path_chosen = EMMEpathDetails[key].count_path(obs_path) / EMMEpathDetails[key].head.count_total_paths()
                    
                elif obs_path == ['T595', 'T595'] and EMMEpathDetails[key].has_path(['T595']) == True:
                    count = EMMEpathDetails[key].count_path(['T595'])
                    count += EMMEpathDetails[key].count_path(['T595', 'T595'])
                    path_chosen = count / EMMEpathDetails[key].head.count_total_paths()
                    
                elif obs_path == ['T595'] and EMMEpathDetails[key].has_path(['T595', 'T595']) == True:
                    count = EMMEpathDetails[key].count_path(['T595'])
                    count += EMMEpathDetails[key].count_path(['T595', 'T595'])
                    path_chosen = count / EMMEpathDetails[key].head.count_total_paths()

                else:
                    path_chosen = 0

                fitness += math.log((path_chosen + beta)/(beta + 1))

    print ("Fitness: " + str(fitness))
    with open (fitness_csv_file, 'wb') as file:
        writer = csv.writer(file)
        writer.writerow([fitness])
    return


def compare_paths(EMMEpathDetails, ObservedPaths): 
    count = 0
    no_of_observed_paths = 0
    for key, obs_paths in ObservedPaths.items():  
        if EMMEpathDetails.has_key(key):
            no_of_observed_paths += len(obs_paths)
            for obs_path in obs_paths:
                if EMMEpathDetails[key].has_path(obs_path) == True:
                    count += 1
                if obs_path == ['T595', 'T595'] and EMMEpathDetails[key].has_path(['T595']) == True:
                    count += 1
                if obs_path == ['T595'] and EMMEpathDetails[key].has_path(['T595', 'T595']) == True:
                    count += 1

    percentage = count / no_of_observed_paths # Closer to 1, the better
    print (percentage)
    return percentage
'''

# Version 1.2
def read_EMME_paths(filename, EMME2TTS):
    # Open and read file
    with open(filename, "r") as file:
        content = file.readlines()

    # Transportation modes
    aux_transit_modes = ['a', 'k', 't', 'u', 'v', 'w', 'y']
    transit_modes = ['b', 'g', 'l', 'm', 'p', 'q', 'r', 's']

    # Organize the data
    path_details = {}

    for line in content:
        line = line.split(" ")
        for item in line:
            if item == "":
                line.remove(item)
        line[-1] = line[-1].rstrip()

        if line[0] == "c" or len(line) < 2:
            continue

        key = (int(line[0]), int(line[1]))
        prop = float(line[3])
        
        i = 0
        transit_routes = []
        transit_routes.append(prop)
        while i < (len(line)-1):
            if line[i] in transit_modes:
                line[i+1] = line[i+1][1:-1]
                transit_routes.append(line[i+1])
                i += 3
                continue
            elif line[i] in aux_transit_modes:
                i += 3
                continue
            else:
                i += 1
                continue
            
        for i in range (len(transit_routes)):
            if EMME2TTS.has_key(transit_routes[i]): # Convert from EMME ID to TTS ID
                transit_routes[i] = EMME2TTS[transit_routes[i]]

        if path_details.has_key(key) == False:
            path_details[key] = [transit_routes]
        else:
            path_details[key].append(transit_routes)

    return path_details


def calculate_fitness(EMMEpathDetails, ObservedPaths, fitness_csv_file, beta):
    fitness = 0.0
    for key, obs_paths in ObservedPaths.items(): 
        if EMMEpathDetails.has_key(key):
            for obs_path in obs_paths:
                A = False
                B = False

                for EMME_path in EMMEpathDetails[key]:
                    temp = EMME_path[1:]
                    
                    # Compare subpaths
                    if obs_path == temp:
                        A = True
                        break
                    if (obs_path == ['T595', 'T595'] and temp == ['T595']) or (temp == ['T595', 'T595'] and obs_path == ['T595']):
                        B = True
                        break

                count = 0        
                if A == True:
                    path_chosen = 0.0
                    for path in EMMEpathDetails[key]:
                        if path[1:] == obs_path:
                            path_chosen += path[0]
                    
                elif B == True:
                    path_chosen = 0.0
                    for path in EMMEpathDetails[key]:
                        if path[1:] == ['T595', 'T595'] or path[1:] == ['T595']:
                            path_chosen += path[0]
                            
                else:
                    path_chosen = 0.0

                fitness += math.log((path_chosen + beta)/(beta + 1))
                
    print ("Fitness: " + str(fitness))
    with open (fitness_csv_file, 'wb') as file:
        writer = csv.writer(file)
        writer.writerow([fitness])
    return



## Main class for the tool
class Calculate_fitness(_m.Tool()):
    version = '1.0.0'
    tool_run_msg = ""
    number_of_tasks = 1

    EMME2TTS_file = _m.Attribute(str)
    Obs_paths_file = _m.Attribute(str)
    EMME_paths_file = _m.Attribute(str)
    fitness_csv_file = _m.Attribute(str)
    beta = _m.Attribute(float)

    def __init__(self):
        #---Init internal variables
        self.TRACKER = _util.ProgressTracker(self.number_of_tasks) #init the ProgressTracker

        #---Set the defaults of parameters used by Modeller
        self.Scenario = _MODELLER.scenario #Default is primary scenario

    def page(self):
        pb = _m.ToolPageBuilder(self, title="Calculate Fitness",
                     description="Cannot be called from Modeller.",
                     runnable=False,
                     branding_text="XTMF") 
        
        return pb.render()

    def __call__(self, EMME2TTS_file, Obs_paths_file, EMME_paths_file, fitness_csv_file, beta):
        print "Calculating Fitness"
        #EMME2TTS = convert_id("2011_Emme2TTS_Line.csv")
        #ObservedPaths = read_obs_paths("TripDataObsAM.csv")
        #EMMEpath_details = read_EMME_paths("pathDetails", EMME2TTS)

        EMME2TTS = convert_id(EMME2TTS_file)
        ObservedPaths = read_obs_paths(Obs_paths_file)
        EMMEpath_details = read_EMME_paths(EMME_paths_file, EMME2TTS)
        calculate_fitness(EMMEpath_details, ObservedPaths, fitness_csv_file, beta)

    def _Execute(EMME_paths_file, Obs_paths_file, EMME2TTSfile, beta):
        self.TRACKER.completeTask()
