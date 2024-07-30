# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:20:58 2023

@author: enf21
"""

# This code prompts the user to input a single line from a simulation set
# output. From this, it produces an output file containing model carbon isotope
# values in every timestep.

OutputTimeSeries = True

parameterInput = ""
while (parameterInput != "Y") and (parameterInput != "N"):
    parameterInput = input("Does this simulation include a burn-in period? (Y/N): ").capitalize()

if parameterInput == "Y":
    LongBurnIn = True
else:
    LongBurnIn = False

parameterInput = input("Please copy and paste an output line representing the conditions at the termination of a simulation set: ")

splitInput = parameterInput.split(",")
k1list = [float(splitInput[3]), float(splitInput[4]), float(splitInput[3])]  # Relative rate of carbonate sedimentation
k2list = [float(splitInput[5]), float(splitInput[6]), float(splitInput[5])]  # Relative rate of organic carbon sedimentation from DOC
k3list = [float(splitInput[7]), float(splitInput[8]), float(splitInput[7])]  # Relative rate of photosynthesis
k4list = [float(splitInput[9]), float(splitInput[10]), float(splitInput[9])]  # Relative rate of remineralisation
k5list = [float(splitInput[11]), float(splitInput[12]), float(splitInput[11])]  # Proportion of productivity dropped directly into sediments
e0list = [float(splitInput[13]), float(splitInput[14]), float(splitInput[13])]  # Fractionation coefficient of photosynthesis
Jlist = [float(splitInput[15]), float(splitInput[16]), float(splitInput[15])]  # Carbon flux in (x10^18 mol/kyr): Tahata et al. 2015
DIC0 = float(splitInput[18])
DOC0 = float(splitInput[17])

# Breakpoints are the timesteps in the model where the selected driver
# parameter value is permitted to change.
if LongBurnIn:
    Breakpoints = [350000, float(splitInput[20]), float(splitInput[21]), float(splitInput[22])]
else:
    Breakpoints = [219945, float(splitInput[20]), float(splitInput[21]), float(splitInput[22])]

di = -6  # Volcanic carbon isotope signature

# All x10^18 mol
DIC = [DIC0]
DOC = [DOC0]

# These lists will hold the time series that we output later.
DICd = [4]  # Carbon isotope signature of the DIC pool
DOCd = [-30]  # Carbon isotope signature of the DOC pool
Seddflux = [-30]  # Carbon isotope signature of sedimented organics: a mixture of productivity and DOC
Prodd = [-26]  # Carbon isotope signature of sedimented productivity
ky = [0]  # time

if LongBurnIn:
    timestepMax = 350000
else:
    timestepMax = 219945
timestep = timestepMax

# This loop re-runs the simulation, using the paramter values provided by the
# user, to produce required time series of box masses and isotopic
# compositions.
while timestep > 210785:
    if (timestep > Breakpoints[1]) or (timestep < Breakpoints[3]):
        k1 = k1list[0]
        k2 = k2list[0]
        k3 = k3list[0]
        k4 = k4list[0]
        k5 = k5list[0]
        e0 = e0list[0]
        J = Jlist[0]
    elif timestep > Breakpoints[2]:  # Interpolate between 1 and 2
        Weighting = (Breakpoints[1] - timestep)/(Breakpoints[1] - Breakpoints[2])
        k1 = k1list[1] * Weighting + k1list[0] * (1 - Weighting)
        k2 = k2list[1] * Weighting + k2list[0] * (1 - Weighting)
        k3 = k3list[1] * Weighting + k3list[0] * (1 - Weighting)
        k4 = k4list[1] * Weighting + k4list[0] * (1 - Weighting)
        k5 = k5list[1] * Weighting + k5list[0] * (1 - Weighting)
        e0 = e0list[1] * Weighting + e0list[0] * (1 - Weighting)
        J = Jlist[1] * Weighting + Jlist[0] * (1 - Weighting)
    else:  # Interpolate between 2 and 3
        Weighting = (Breakpoints[2] - timestep)/(Breakpoints[2] - Breakpoints[3])
        k1 = k1list[0] * Weighting + k1list[1] * (1 - Weighting)
        k2 = k2list[0] * Weighting + k2list[1] * (1 - Weighting)
        k3 = k3list[0] * Weighting + k3list[1] * (1 - Weighting)
        k4 = k4list[0] * Weighting + k4list[1] * (1 - Weighting)
        k5 = k5list[0] * Weighting + k5list[1] * (1 - Weighting)
        e0 = e0list[0] * Weighting + e0list[1] * (1 - Weighting)
        J = Jlist[0] * Weighting + Jlist[1] * (1 - Weighting)

    currentStep = timestepMax - timestep

    # In each timestep, we calculate the rates of each flux...
    carbonateSedimentation = k1 * DIC[currentStep]
    photosynthesis = k3 * DIC[currentStep]
    organicSedimentation = k2 * DOC[currentStep] + k5 * photosynthesis
    remineralisation = k4 * DOC[currentStep]

    # Then we calculate the resulting box masses.
    newDIC = DIC[currentStep] - carbonateSedimentation - photosynthesis + remineralisation + J
    DIC.append(newDIC)
    newDOC = DOC[currentStep] + photosynthesis - organicSedimentation - remineralisation
    DOC.append(newDOC)
    newDICd = DICd[currentStep] + ((J / DIC[currentStep]) * (di - DICd[currentStep])) + ((remineralisation / DIC[currentStep]) * (DOCd[currentStep] - DICd[currentStep])) + (k3 * e0)
    DICd.append(newDICd)
    newDOCd = DOCd[currentStep] + (((1-k5) * photosynthesis / DOC[currentStep]) * (DICd[currentStep] - e0 - DOCd[currentStep]))
    DOCd.append(newDOCd)
    Prodd.append(DICd[currentStep] - e0)
    Seddflux.append(((k2 * DOC[currentStep] * DOCd[currentStep]) + (k5 * photosynthesis * Prodd[currentStep])) / (k2 * DOC[currentStep] + k5 * photosynthesis))

    timestep = timestep - 1
    ky.append(currentStep)

# Here, we output the time series calculated above.
if OutputTimeSeries:
    OutputFilepath = input("Please input a filepath (including file name) to output the time series: ")
    with open(OutputFilepath, "a+") as outfile:
        modelT = 1  # The first value (index = 0) is not output because it is arbitrary.
        outfile.writelines("Model Time,Model [DOC],Model [DIC],Model dDOC,Model dDIC\n")
        while (modelT < len(DIC)):
            if ((modelT > 130000) or (LongBurnIn is False)):
                outputTime = ky[modelT]
                if LongBurnIn:
                    outputTime = outputTime - 130000
                outfile.writelines(str(outputTime) + "," + str(DOC[modelT]) + "," + str(DIC[modelT]) + "," + str(Seddflux[modelT]) + "," + str(DICd[modelT]) + "\n")
            modelT = modelT + 1
