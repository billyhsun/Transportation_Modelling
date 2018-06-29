import inro.modeller as _m
import traceback as _traceback
from contextlib import contextmanager
from contextlib import nested
from datetime import datetime as _dt
from multiprocessing import cpu_count
from json import loads as _parsedict
from os.path import dirname
import os


_MODELLER = _m.Modeller() #Instantiate Modeller once.
_util = _MODELLER.module('tmg.common.utilities')
_tmgTPB = _MODELLER.module('tmg.common.TMG_tool_page_builder')
PathDetails = _MODELLER.tool('inro.emme.transit_assignment.extended.path_details')
EMME_VERSION = _util.getEmmeVersion(tuple) 

class ExtractPathsEMME(_m.Tool()):
    version = '0.0.1'
    tool_run_msg = ""
    number_of_tasks = 1

    xtmf_ScenarioNumber = _m.Attribute(int)
    #xtmf_ClassName = _m.Attribute(str)
    #xtmf_IterationNumber = _m.Attribute(str)
    #xtmf_PathDetails = _m.Attribute(str)
    xtmf_OutputPathFile = _m.Attribute(str)

    def __init__(self):
        #---Init internal variables
        self.TRACKER = _util.ProgressTracker(self.number_of_tasks) #init the ProgressTracker

    def page(self):
        pb = _m.ToolPageBuilder(self, title="Path Analysis",
                     description="Cannot be called from Modeller.",
                     runnable=False,
                     branding_text="XTMF") 
        
        return pb.render()

    def __call__(self, xtmf_ScenarioNumber, xtmf_OutputPathFile, xtmf_ODdist):
        self.ScenarioNumber = int(xtmf_ScenarioNumber)
        self.scenario = _m.Modeller().emmebank.scenario(self.ScenarioNumber)
        if (self.scenario == None):
            raise Exception("Scenario %s was not found!" %xtmf_ScenarioNumber)
        if not self.scenario.has_transit_results:
            raise Exception("Scenario %s does not have transit assignment results" %xtmf_ScenarioNumber)             
        self.OutputPathFile = xtmf_OutputPathFile
        self.ODdist = xtmf_ODdist
        self.NumberOfProcessors = cpu_count()
        '''self.ClassName = xtmf_ClassName
        self.IterationNumber = xtmf_IterationNumber'''

        self.demandMatrices = _util.DetermineAnalyzedTransitDemandId(EMME_VERSION, self.scenario)
        configPath = dirname(_MODELLER.desktop.project_file_name()) \
                    + "/Database/STRATS_s%s/config" %self.ScenarioNumber 
        with open(configPath) as reader:
            config = _parsedict(reader.readline())
            data = config['data']
            if 'multi_class' in data:
                if data['multi_class'] == True:
                    self.Multiclass = True
                else:
                    self.Multiclass = False
            else:
                if data['type'] == "MULTICLASS_TRANSIT_ASSIGNMENT":

                    self.Multiclass = True
                else:
                    self.Multiclass = False
        '''if self.Multiclass == True:
            self.AnalyzedDemandMatrixID = demandMatrices[self.ClassName]
        else:
            self.AnalyzedDemandMatrixID = demandMatrices
        self.SelectedPaths = xtmf_SelectedPaths
        self.SelectPathsBy = xtmf_SelectPathsBy
        self.SelectedPathsCriteria = xtmf_SelectedPathsCriteria
        self.SelectedPathsThresholdLower = xtmf_SelectedPathsThresholdLower
        self.SelectedPathsThresholdUpper = xtmf_SelectedPathsThresholdUpper
        self.PathDetail = xtmf_PathsDetails.split(',')
        #self.PathsToOutput = self._VerifyNonNullWithError(self.PathDetail[0],"Paths to Output must be specfied")
        self.TotalImpedenceDetails = self._ConvertToBool(self.PathDetail[0])
        self.AverageBoardingDetails = self._ConvertToBool(self.PathDetail[1])
        self.DistanceDetails = self._ConvertToBool(self.PathDetail[2])
        self.TimesAndCostsType = self._VerifyNonNullWithError(self.PathDetail[3],"Times and cost type must be defined")
        self.FirstWaitingTime = self._ConvertToBool(self.PathDetail[4])
        self.TotalWaitingTime = self._ConvertToBool(self.PathDetail[5])
        self.FirstBoardingTime = self._ConvertToBool(self.PathDetail[6])
        self.TotalBoardingTime = self._ConvertToBool(self.PathDetail[7])
        self.InVehicleTime = self._ConvertToBool(self.PathDetail[8])
        self.AuxTransitTime = self._ConvertToBool(self.PathDetail[9])
        self.FirstBoardingCost = self._ConvertToBool(self.PathDetail[10])
        self.TotalBoardingCost = self._ConvertToBool(self.PathDetail[11])
        self.InVehicleCost = self._ConvertToBool(self.PathDetail[12])
        self.AuxTransitCost = self._ConvertToBool(self.PathDetail[13])
        self.ZonesDetails = self._ConvertToBool(self.PathDetail[14])
        self.PathNumberDetails =self._ConvertToBool(self.PathDetail[15])
        self.ProportionDetails = self._ConvertToBool(self.PathDetail[16])
        self.SelectedVolumeDetails = self._ConvertToBool(self.PathDetail[17])
        self.VolumeDetails = self._ConvertToBool(self.PathDetail[18])
        self.PathValueDetails = self._ConvertToBool(self.PathDetail[19])
        self.PathItemDetails = self._ConvertToBool(self.PathDetail[20])
        self.NodesDetails = self._ConvertToBool(self.PathDetail[21])
        self.ModeDetails = self._ConvertToBool(self.PathDetail[22])
        self.TransitLineDetails = self._ConvertToBool(self.PathDetail[23])
        self.AuxTransitSubPathDetails = self._ConvertToBool(self.PathDetail[24])
        self.SubPathDetails = self._ConvertToBool(self.PathDetail[25])
        self.ODZoneDetails = self._ConvertToBool(self.PathDetail[26])
        self.ODPathStatDetails = self._ConvertToBool(self.PathDetail[27])
        self.ODPathNumberDetails = self._ConvertToBool(self.PathDetail[28])
        self.ODSelectedDemandDetails = self._ConvertToBool(self.PathDetail[29])
        self.ODDemandDetails = self._ConvertToBool(self.PathDetail[30])
        self.ODAggPathValue = self._ConvertToBool(self.PathDetail[31])
        self.ODDetails = self._ConvertToBool(self.PathDetail[32])'''

        try:
            self._Execute()
        except Exception, e:
            msg = str(e) + "\n" + _traceback.format_exc(e)
            raise Exception(msg)

    def _Execute(self):
        print "Extracting Paths"        
        spec = {
        "type": "EXTENDED_TRANSIT_PATH_DETAILS",
        "selected_paths": {
            "by": "FLOW_PROPORTION",
            "criteria": {
                "threshold": {
                    "lower": 0.001,
                    "upper": 9999
                }
            }
        },
        "details_to_output": {
            "total_impedance": False,
            "times_and_costs": None,
            "avg_boardings": False,
            "distance": False
        },
        "items_for_paths": {
            "zones": True,
            "path_number": True,
            "proportion": True,
            "volume": True,
            "details": True
        },
        "items_for_sub_paths": {
            "nodes": True,
            "mode": True,
            "transit_line": True,
            "aux_transit_sub_paths": True,
            "details": True
        },
        "items_for_od_pairs": {
            "zones": False,
            "number_of_paths": False,
            "demand": False,
            "details": False
        },
        "analyzed_demand": None,
        "constraint": {
            "by_value": {
                "interval_min": 0,
                "interval_max": 0,
                "condition": "EXCLUDE",
                "od_values": "mf1"
            },
            "by_zone": None
        }
        }
        path_file = self.OutputPathFile
        if os.path.exists(path_file) == True:
            os.remove(path_file)
        for key in self.demandMatrices:
            className = key   
        PathDetails(specification=spec, output_file=path_file, scenario = self.scenario, class_name = "Iteration 5 " + className)
        

    def _ConvertToBool(self, param):
        if param == 'True':
            return True
        else:
            return False

    def _VerifyNonNullWithError(self, param, errorString):
        if param != '':
            return param
        else:
            raise Exception(errorString)

    def _VerifyNonNull(self, param):
        if param != '':
            return param
        else:
            return None
