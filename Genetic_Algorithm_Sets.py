# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 15:20:58 2023

@author: enf21
"""

# This code continuously runs sets of simulations of carbon isotope values over
# the Shuram excursion, with a burn-in period in excess of 100 million years
# in simulation time to allow for box values to approach equilibrium.

import random
import math
import time

BurnIn = ""
while ((BurnIn != "Y") and (BurnIn != "N")):
    BurnIn = input("Would you like these simulation sets to include a burn-in period? (Y/N) ").capitalize()
if BurnIn == "Y":
    BurnIn = True
else:
    BurnIn = False

output = input("Please input a filepath and name for the file to contain outputs from this script: ")
with open(output, "a+") as outfile:  # Write headers to the output.
    outfile.write("Replicte Number")
    outfile.write(",")
    outfile.write("Varied Variable")
    outfile.write(",")
    outfile.write("RSS")
    outfile.write(",")
    outfile.write("Background k1")
    outfile.write(",")
    outfile.write("Shuram k1")
    outfile.write(",")
    outfile.write("Background k2")
    outfile.write(",")
    outfile.write("Shuram k2")
    outfile.write(",")
    outfile.write("Background k3")
    outfile.write(",")
    outfile.write("Shuram k3")
    outfile.write(",")
    outfile.write("Background k4")
    outfile.write(",")
    outfile.write("Shuram k4")
    outfile.write(",")
    outfile.write("Background k5")
    outfile.write(",")
    outfile.write("Shuram k5")
    outfile.write(",")
    outfile.write("Background e0")
    outfile.write(",")
    outfile.write("Shuram e0")
    outfile.write(",")
    outfile.write("Background J")
    outfile.write(",")
    outfile.write("Shuram J")
    outfile.write(",")
    outfile.write("DOC0")
    outfile.write(",")
    outfile.write("DIC0")
    outfile.write(",")
    outfile.write("Breakpoints 1")
    outfile.write(",")
    outfile.write("Breakpoints 2")
    outfile.write(",")
    outfile.write("Breakpoints 3")
    outfile.write(",")
    outfile.write("Breakpoints 4")
    outfile.write("\n")

OrgCin = input("Please input the name and filepath for a .csv file containing empirical organic carbon isotope measurements: ")
# This .csv file should contain, in its second column, organic carbon isotope
# measurements and, in its fourth column, the ages of those measurements in
# ky, calibrated such that the Shuram excursion begins around 218607ky and
# termination of the excursion begins around 211607ky.

EmpiricalOrgC = []
EmpiricalOrgT = []
with open(OrgCin) as infile:
    header = True
    for line in infile:
        if header is True:
            header = False
        else:
            splitline = line.split(",")
            if (int(float(splitline[3])) < 219945) and (int(float(splitline[3])) > 210785):
                EmpiricalOrgC.append(float(splitline[1]))
                EmpiricalOrgT.append(int(float(splitline[3])))

CarbCin = input("Please input the name and filepath for a .csv file containing empirical carbonate carbon isotope measurements (e.g. C:/Users/ID/Downloads/output.txt): ")
# This .csv file should contain, in its second column, carbonate carbon isotope
# measurements and, in its fourth column, the ages of those measurements in
# ky, calibrated such that the Shuram excursion begins around 218607ky and
# termination of the excursion begins around 211607ky.

EmpiricalCarbC = []
EmpiricalCarbT = []
with open(CarbCin) as infile:
    header = True
    for line in infile:
        if header is True:
            header = False
        else:
            splitline = line.split(",")
            if (int(float(splitline[3])) < 219945) and (int(float(splitline[3])) > 210785):
                EmpiricalCarbC.append(float(splitline[1]))
                EmpiricalCarbT.append(int(float(splitline[3])))

# Breakpoints at which values can be set. Random variation is added to these
# breakpoint ages in each simulation set. Values will be interpolated between
# these breakpoints.
if BurnIn:
    Breakpoints = [350000, 218607, 217253, 211607]
else:
    Breakpoints = [219945, 218607, 217253, 211607]
Breakpoints[1] = Breakpoints[1] + random.randint(1, 500) - random.randint(1, 500)
Breakpoints[2] = Breakpoints[2] + random.randint(1, 500) - random.randint(1, 500)
Breakpoints[3] = Breakpoints[3] + random.randint(1, 500) - random.randint(1, 500)

# k2 = 0 requires that all organic carbon sedimentation come from productivity,
# rather than from the pool of detrital organic carbon.
k2ZeroQ = ""
while (k2ZeroQ != "Y") and (k2ZeroQ != "N"):
    k2ZeroQ = input("Would you like all k2 values to be zero? (Y/N)").capitalize()
if k2ZeroQ == "Y":
    k2list0 = [0, 0, 0]  # Relative rate of organic carbon sedimentation from DOC
else:
    k2list0 = [0.00002, 0.00002, 0.00002]  # Relative rate of organic carbon sedimentation from DOC

k1list0 = [0.0005, 0.0005, 0.0005]  # Relative rate of carbonate sedimentation
k3list0 = [0.0003, 0.0003, 0.0003]  # Relative rate of photosynthesis
k4list0 = [0.000001, 0.000001, 0.000001]  # Relative rate of remineralisation
k5list0 = [0.1, 0.1, 0.1]  # Proportion of productivity dropped directly into sediments
e0list0 = [30, 30, 30]  # Fractionation coefficient of photosynthesis
Jlist0 = [0.003, 0.003, 0.003]  # Carbon flux in (x10^18 mol/kyr): Tahata et al. 2015
di = -6  # Input carbon isotope signature
DIC00 = 20
DOC00 = 10000

randomMultiplierOptions = [0.4, 0.5, 2.5, 2, 0.8, 1.4, 0.8, 1.4, 1.05, 0.95, 1.1, 0.9, 1.04, 0.96, 1.01, 0.99, 1.01, 0.99]

k1list = list(k1list0)
k2list = list(k2list0)
k3list = list(k3list0)
k4list = list(k4list0)
k5list = list(k5list0)
e0list = list(e0list0)
Jlist = list(Jlist0)
bestTotalRSS = -1  # This variable guides the genetic algorithm.
driver = 1

DOC0 = DOC00
DIC0 = DIC00

attempts = 0  # A counter variable.
attemptsSinceLastUpdate = 0  # Tracks how close we are to converging on a final set of parameter values for this simulation set
replicateNumber = 0
while True:
    if attemptsSinceLastUpdate == 500:  # After 500 attempted improvements, we conclude that we have as good a set of parameter values as we are going to get.
        replicateNumber = replicateNumber + 1
        if bestTotalRSS != -1:  # Only write an output if we've found a functioning set of variables
            with open(output, "a+") as outfile:  # Write output
                outfile.write(str(replicateNumber))
                outfile.write(",")
                if driver == 1:
                    outfile.write("k1")
                elif driver == 2:
                    outfile.write("k2")
                elif driver == 3:
                    outfile.write("k3")
                elif driver == 4:
                    outfile.write("k4")
                elif driver == 5:
                    outfile.write("k5")
                elif driver == 6:
                    outfile.write("e0")
                else:
                    outfile.write("J")
                outfile.write(",")
                outfile.write(str(bestTotalRSS))
                outfile.write(",")
                outfile.write(str(k1list[0]))
                outfile.write(",")
                outfile.write(str(k1list[1]))
                outfile.write(",")
                outfile.write(str(k2list[0]))
                outfile.write(",")
                outfile.write(str(k2list[1]))
                outfile.write(",")
                outfile.write(str(k3list[0]))
                outfile.write(",")
                outfile.write(str(k3list[1]))
                outfile.write(",")
                outfile.write(str(k4list[0]))
                outfile.write(",")
                outfile.write(str(k4list[1]))
                outfile.write(",")
                outfile.write(str(k5list[0]))
                outfile.write(",")
                outfile.write(str(k5list[1]))
                outfile.write(",")
                outfile.write(str(e0list[0]))
                outfile.write(",")
                outfile.write(str(e0list[1]))
                outfile.write(",")
                outfile.write(str(Jlist[0]))
                outfile.write(",")
                outfile.write(str(Jlist[1]))
                outfile.write(",")
                outfile.write(str(DOC0))
                outfile.write(",")
                outfile.write(str(DIC0))
                outfile.write(",")
                outfile.write(str(Breakpoints[0]))
                outfile.write(",")
                outfile.write(str(Breakpoints[1]))
                outfile.write(",")
                outfile.write(str(Breakpoints[2]))
                outfile.write(",")
                outfile.write(str(Breakpoints[3]))
                outfile.write("\n")

        # Reset parameters to their starting values.
        k1list = list(k1list0)
        k2list = list(k2list0)
        k3list = list(k3list0)
        k4list = list(k4list0)
        k5list = list(k5list0)
        e0list = list(e0list0)
        Jlist = list(Jlist0)
        DOC0 = DOC00
        DIC0 = DIC00

        # Reset breakpoints, and add new randomness.
        if BurnIn:
            Breakpoints = [350000, 218607, 217253, 211607]
        else:
            Breakpoints = [219945, 218607, 217253, 211607]
        Breakpoints[1] = Breakpoints[1] + random.randint(1, 500) - random.randint(1, 500)
        Breakpoints[2] = Breakpoints[2] + random.randint(1, 500) - random.randint(1, 500)
        Breakpoints[3] = Breakpoints[3] + random.randint(1, 500) - random.randint(1, 500)

        bestTotalRSS = -1  # Reset genetic algorithm control
        driver = (replicateNumber % 7) + 1  # New driver
        attemptsSinceLastUpdate = 0

    attempts = attempts + 1
    attemptsSinceLastUpdate = attemptsSinceLastUpdate + 1
    try:  # Try in case a numerical issue causes a crash.
        # This is the genetic algorithm. Here, we attempt to tweak parameter
        # values to improve the fit of the model to the data.
        if BurnIn:
            tryChanging = random.randint(0, 7)
        else:
            tryChanging = random.randint(0, 9)
        multiplier = random.choice(randomMultiplierOptions)
        if tryChanging == 0:
            k1list = [k1val * multiplier for k1val in k1list]
        elif tryChanging == 1:
            k2list = [k2val * multiplier for k2val in k2list]
        elif tryChanging == 2:
            k3list = [k3val * multiplier for k3val in k3list]
        elif tryChanging == 3:
            k4list = [k4val * multiplier for k4val in k4list]
        elif tryChanging == 4:
            k5list = [k5val * multiplier for k5val in k5list]
        elif tryChanging == 5:
            e0list = [e0val * multiplier for e0val in e0list]
        elif tryChanging == 6:
            Jlist = [Jval * multiplier for Jval in Jlist]
        elif (tryChanging == 7 and BurnIn is False):
            DOC0 = DOC0 * multiplier
        elif (tryChanging == 8 and BurnIn is False):
            DIC0 = DIC0 * multiplier
        else:
            if driver == 1:
                k1list[1] = k1list[1] * multiplier
            elif driver == 2:
                k2list[1] = k2list[1] * multiplier
            elif driver == 3:
                k3list[1] = k3list[1] * multiplier
            elif driver == 4:
                k4list[1] = k4list[1] * multiplier
            elif driver == 5:
                k5list[1] = k5list[1] * multiplier
            elif driver == 6:
                e0list[1] = e0list[1] * multiplier
            else:
                Jlist[1] = Jlist[1] * multiplier
        # All x10^18 mol
        DIC = []
        DIC.append(DIC0)
        DOC = []
        DOC.append(DOC0)
        oxygenFlux = [0]  # (/kyr)

        DOCd = []  # Carbon isotope signature of the DOC pool
        DOCd.append(-30)
        DICd = []  # Carbon isotope signature of the DIC pool
        DICd.append(4)
        Seddflux = [-28]  # Carbon isotope signature of sedimented organics: a mixture of productivity and DOC
        Prodd = [-26]  # Carbon isotope signature of sedimented productivity
        ky = [0]  # time

        timestepMax = Breakpoints[0]
        timestep = timestepMax
        while timestep > 210785:  # Here, we test our new values.
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

            carbonateSedimentation = k1 * DIC[currentStep]
            photosynthesis = k3 * DIC[currentStep]
            organicSedimentation = k2 * DOC[currentStep] + k5 * photosynthesis
            remineralisation = k4 * DOC[currentStep]

            newDIC = DIC[currentStep] - carbonateSedimentation - photosynthesis + remineralisation + J
            DIC.append(newDIC)

            newDOC = DOC[currentStep] + photosynthesis - organicSedimentation - remineralisation
            DOC.append(newDOC)

            newDICd = DICd[currentStep] + ((J / DIC[currentStep]) * (di - DICd[currentStep])) + ((remineralisation / DIC[currentStep]) * (DOCd[currentStep] - DICd[currentStep])) + (k3 * e0)
            DICd.append(newDICd)

            newDOCd = DOCd[currentStep] + (((1-k5) * photosynthesis / DOC[currentStep]) * (DICd[currentStep] - e0 - DOCd[currentStep]))
            DOCd.append(newDOCd)

            Prodd.append(DICd[currentStep] - e0)

            oxygenFlux.append(photosynthesis - remineralisation)
            Seddflux.append(((k2 * DOC[currentStep] * DOCd[currentStep]) + (k5 * photosynthesis * Prodd[currentStep])) / (k2 * DOC[currentStep] + k5 * photosynthesis))

            timestep = timestep - 1
            ky.append(currentStep)

        index = 0
        OrgRSS = 0
        for empiricalValue in EmpiricalOrgC:
            empiricalTime = EmpiricalOrgT[index]
            simulatedIndex = timestepMax - empiricalTime
            simulatedValue = Seddflux[simulatedIndex]
            OrgRSS = OrgRSS + ((empiricalValue - simulatedValue) * (empiricalValue - simulatedValue))
            index = index + 1

        index = 0
        CarbRSS = 0
        for empiricalValue in EmpiricalCarbC:
            empiricalTime = EmpiricalCarbT[index]
            simulatedIndex = timestepMax - empiricalTime
            simulatedValue = DICd[simulatedIndex]
            CarbRSS = CarbRSS + ((empiricalValue - simulatedValue) * (empiricalValue - simulatedValue))
            index = index + 1

        # Total RSS is the measure of our goodness of fit.
        totalRSS = (OrgRSS * len(EmpiricalCarbC) / len(EmpiricalOrgC)) + CarbRSS

        # We must ensure that this paramter tweak did not require that we
        # exceed the bounds placed on parameter values. If it didn't, and the
        # RSS has been improved, then we will keep it.
        if ((totalRSS < bestTotalRSS) or (bestTotalRSS == -1)) and (math.isnan(totalRSS) is False) and (k1list[0] < 0.01) and (k1list[0] > 0.0001) and (k1list[1] < 0.1) and (k1list[1] > 0.00001) and (k2list[0] < 0.01) and (k2list[1] < 0.1) and (k3list[0] > 0.0001) and (k3list[0] < 0.1) and (k3list[1] > 0.00001) and (k3list[1] < 1) and (k4list[0] > 0.000001) and (k4list[0] < 10) and (k4list[1] > 0.0000001) and (k4list[1] < 100) and (k5list[0] < 1) and (k5list[1] < 1) and (e0list[0] < 50) and (e0list[1] < 50) and (Jlist[0] < 0.006) and (Jlist[1] < 0.06) and (Breakpoints[2] < Breakpoints[1]) and (Breakpoints[1] < Breakpoints[0]):
            attemptsSinceLastUpdate = 0
            bestTotalRSS = totalRSS  # We are keeping our change
            print("New best model:")
            print(f"Combined RSS: {totalRSS}")
            print("Found at:")
            print(time.localtime(time.time()))
            print(f"On attempt {attempts}")
            print("k1list:")
            print(k1list)
            print("k2list:")
            print(k2list)
            print("k3list:")
            print(k3list)
            print("k4list:")
            print(k4list)
            print("k5list:")
            print(k5list)
            print("e0list:")
            print(e0list)
            print("Jlist:")
            print(Jlist)
            print("DOC0:")
            print(DOC0)
            print("DIC0:")
            print(DIC0)
            print("Breakpoints:")
            print(Breakpoints)
            print("")
        else:  # Otherwise, we reset our values to what they were before we implemented a tweak.
            if tryChanging == 0:
                k1list = [k1val / multiplier for k1val in k1list]
            elif tryChanging == 1:
                k2list = [k2val / multiplier for k2val in k2list]
            elif tryChanging == 2:
                k3list = [k3val / multiplier for k3val in k3list]
            elif tryChanging == 3:
                k4list = [k4val / multiplier for k4val in k4list]
            elif tryChanging == 4:
                k5list = [k5val / multiplier for k5val in k5list]
            elif tryChanging == 5:
                e0list = [e0val / multiplier for e0val in e0list]
            elif tryChanging == 6:
                Jlist = [Jval / multiplier for Jval in Jlist]
            elif (tryChanging == 7 and BurnIn is False):
                DOC0 = DOC0 / multiplier
            elif (tryChanging == 8 and BurnIn is False):
                DIC0 = DIC0 / multiplier
            else:
                if driver == 1:
                    k1list[1] = k1list[1] / multiplier
                elif driver == 2:
                    k2list[1] = k2list[1] / multiplier
                elif driver == 3:
                    k3list[1] = k3list[1] / multiplier
                elif driver == 4:
                    k4list[1] = k4list[1] / multiplier
                elif driver == 5:
                    k5list[1] = k5list[1] / multiplier
                elif driver == 6:
                    e0list[1] = e0list[1] / multiplier
                else:
                    Jlist[1] = Jlist[1] / multiplier
    except ZeroDivisionError:  # If a crash occurs, reset values and continue.
        if tryChanging == 0:
            k1list = [k1val / multiplier for k1val in k1list]
        elif tryChanging == 1:
            k2list = [k2val / multiplier for k2val in k2list]
        elif tryChanging == 2:
            k3list = [k3val / multiplier for k3val in k3list]
        elif tryChanging == 3:
            k4list = [k4val / multiplier for k4val in k4list]
        elif tryChanging == 4:
            k5list = [k5val / multiplier for k5val in k5list]
        elif tryChanging == 5:
            e0list = [e0val / multiplier for e0val in e0list]
        elif tryChanging == 6:
            Jlist = [Jval / multiplier for Jval in Jlist]
        elif (tryChanging == 7 and BurnIn is False):
            DOC0 = DOC0 / multiplier
        elif (tryChanging == 8 and BurnIn is False):
            DIC0 = DIC0 / multiplier
        else:
            if driver == 1:
                k1list[1] = k1list[1] / multiplier
            elif driver == 2:
                k2list[1] = k2list[1] / multiplier
            elif driver == 3:
                k3list[1] = k3list[1] / multiplier
            elif driver == 4:
                k4list[1] = k4list[1] / multiplier
            elif driver == 5:
                k5list[1] = k5list[1] / multiplier
            elif driver == 6:
                e0list[1] = e0list[1] / multiplier
            else:
                Jlist[1] = Jlist[1] / multiplier
        continue
