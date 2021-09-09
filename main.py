from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import shutil

# define the model name and simulation parameters
fmuPath = 'G:/FMUs/SampleModel.fmu'
start_time = 0.0
stop_time = 120.0
threshold = 2.0
step_size = 1.0
# step_size = 1e-3

model_description = read_model_description(fmuPath)

# Open a file: file
file = open('C:/Users/gorog/Desktop/rows.json', mode='r', encoding='UTF8')

# read all lines at once
all_of_it = file.read()

# close the file
file.close()

vrs = {}

for variable in model_description.modelVariables:
    vrs[variable.name] = variable.valueReference

fmu_input = vrs['strInput']
fmu_output = vrs['strOutput']

# extract the FMU
unzipdir = extract(fmuPath)

fmu = FMU2Slave(guid=model_description.guid,
                unzipDirectory=unzipdir,
                modelIdentifier=model_description.coSimulation.modelIdentifier,
                instanceName='instance1')

# initialize
fmu.instantiate()
fmu.setupExperiment(startTime=start_time)
fmu.enterInitializationMode()
fmu.exitInitializationMode()

current_time = start_time

rows = []  # list to record the results

# simulation loop
while current_time < stop_time:
    # set the input
    fmu.setString([input], [all_of_it])

    # perform one step
    fmu.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)

    # set the output
    [outputs4] = fmu.getString([fmu_output])
    strOut = outputs4.decode('utf8')

    # advance the time
    current_time += step_size

fmu.terminate()
fmu.freeInstance()

# clean up
shutil.rmtree(unzipdir, ignore_errors=True)