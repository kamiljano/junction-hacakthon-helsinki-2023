#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 10:34:39 2023

@author: jorge
"""
from dataclasses import dataclass
import numpy as np
import json
import pandas as pd
from plotnine import ggplot, aes, geom_line, geom_vline


@dataclass
class GlassDataPoint:
    @dataclass
    class Status:
        ticktime : int
        timestamp : int 
        status : bool 
        counter : int
        
    @dataclass
    class EyeData:
        rightEyeSensors : tuple[int, int, int, int, int, int]
        leftEyeSensors : tuple[int, int, int, int, int, int]
        
        sumRSensors = lambda self : np.sum(self.rightEyeSensors)
        sumLSensors = lambda self : np.sum(self.leftEyeSensors)
        meanRSensors = lambda self : np.mean(self.rightEyeSensors)
        meanLSensors = lambda self : np.mean(self.leftEyeSensors)
        sdRSensors = lambda self : np.std(self.rightEyeSensors)
        sdLSensors = lambda self : np.std(self.leftEyeSensors)

        rightEyeXY = lambda self : (np.sum(self.rightEyeSensors[0:3])/
                                    np.sum(self.rightEyeSensors[3:6]),
                                    self.rightEyeSensors[0] + self.rightEyeSensors[5] /
                                    np.sum(self.rightEyeSensors[2:4]))    
        leftEyeXY = lambda self : (np.sum(self.leftEyeSensors[0:3])/
                                   np.sum(self.leftEyeSensors[3:6]),
                                   self.leftEyeSensors[0] + self.leftEyeSensors[5] /
                                   np.sum(self.leftEyeSensors[2:4])) 
        
    @dataclass
    class Temperature:
        rightEyeSensors : tuple[int, int, int, int]
        leftEyeSensors : tuple[int, int, int, int]
        faceT = lambda self : (self.rightEyeSensors[0] +  self.rightEyeSensors[1] + self.leftEyeSensors[0] +  self.leftEyeSensors[1]) / 4.
        airT = lambda self : (self.rightEyeSensors[2] +  self.rightEyeSensors[3] + self.leftEyeSensors[2] +  self.leftEyeSensors[3]) / 4.
        rate = lambda self : self.faceT() / self.airT()
    
    status : Status
    
    eyeData : EyeData
        
    heartRate : int
    
    gps : tuple[int, int]
    
    temp : Temperature
    
class GlassData:
    dataPoints = dict()
    
    blink_mean_threshold = 1
    blink_sd_threshold = 1.5
    
    def __init__(self, files):
        # Opening JSON file
        for file in files:
            f = open(file)
             
            # returns JSON object as 
            # a dictionary
            data = json.load(f)
             
            # Iterating through the json
            # list
            for row in data:
                afe = row['afe']
                for eye in afe:
                    if 't' in eye:
                        if eye['t'] == 'R':
                            rightEyeSensors = eye['m'][0][0:6]
                            i = eye['i']
                            status = GlassDataPoint.Status(i[0], i[1], i[2], i[3])
                        if eye['t'] == 'L':
                            leftEyeSensors = eye['m'][0][0:6]
                eyes = GlassDataPoint.EyeData(rightEyeSensors, leftEyeSensors)
                if 'heart' in row:
                    hr = row['heart']['hr']
                else:
                    hr = 0
                if 'gps' in row:
                    gps = (row['gps']['latitude'], row['gps']['longitude'])
                else:
                    gps = (0,0)
                t = row['auxSensors']['tempEt']['v']
                temp = GlassDataPoint.Temperature(t[0:4], t[4:8])
                glassData = GlassDataPoint(status, eyes, hr, gps, temp)
                self.dataPoints[status.ticktime] = glassData
             
            # Closing file
            f.close()
            
    def tempRates(self):
        times = np.array([])
        tRates = np.array([])
        for key in self.dataPoints:
            tRate = self.dataPoints[key].temp.rate()
            times = np.append(times, key)
            tRates = np.append(tRates, tRate)
        return times, tRates
        
    def eyePositions(self):
        times = np.array([])
        rbrightness = np.array([])
        lbrightness = np.array([])
        reyesX = np.array([])
        reyesY = np.array([])
        leyesX = np.array([])
        leyesY = np.array([])
        for key in self.dataPoints:
            eyeR = self.dataPoints[key].eyeData.rightEyeXY()
            eyeL = self.dataPoints[key].eyeData.leftEyeXY()
            meanrBr = self.dataPoints[key].eyeData.sumRSensors()
            meanlBr = self.dataPoints[key].eyeData.sumLSensors()
            times = np.append(times, key)
            reyesX = np.append(reyesX, eyeR[0])
            reyesY = np.append(reyesY, eyeR[1])
            leyesX = np.append(leyesX, eyeL[0])
            leyesY = np.append(leyesY, eyeL[1])
            rbrightness = np.append(rbrightness, meanrBr)
            lbrightness = np.append(lbrightness, meanlBr)
        reyesX = (reyesX - np.mean(reyesX)) / np.std(reyesX)
        reyesY = (reyesY - np.mean(reyesY)) / np.std(reyesY)
        leyesX = (leyesX - np.mean(leyesX)) / np.std(leyesX)
        leyesY = (leyesY - np.mean(leyesY)) / np.std(leyesY)
        rbrightness = (rbrightness - np.mean(rbrightness)) / np.std(rbrightness)
        lbrightness = (lbrightness - np.mean(lbrightness)) / np.std(lbrightness)
        return times, reyesX, reyesY, leyesX, leyesY, rbrightness, lbrightness
        
    def blinks(self):
        times = np.array([])
        rmeans = np.array([])
        rsds = np.array([])
        lmeans = np.array([])
        lsds = np.array([])
        rbl = np.array([])
        lbl = np.array([])
        for key in self.dataPoints:
            rmean = self.dataPoints[key].eyeData.meanRSensors()
            lmean = self.dataPoints[key].eyeData.meanLSensors()
            rsd = self.dataPoints[key].eyeData.sdRSensors()
            lsd = self.dataPoints[key].eyeData.sdLSensors()
            times = np.append(times, key)
            rmeans = np.append(rmeans, rmean)
            rsds = np.append(rsds, rsd)
            lmeans = np.append(lmeans, lmean)
            lsds = np.append(lsds, lsd)
            
        for i in range(len(times)):
            rmin = np.max([i-10, 0])
            rmax = np.min([i+10, len(times)])
            rmean = rmeans[i]
            rsd = rsds[i]
            lmean = lmeans[i]
            lsd = lsds[i]
            local_rmeans = rmeans[rmin:rmax]
            local_rsds = rsds[rmin:rmax]
            local_lmeans = lmeans[rmin:rmax]
            local_lsds = lsds[rmin:rmax]
            
            mean_local_rmeans = np.mean(local_rmeans)
            sd_local_rmeans = np.std(local_rmeans)
            mean_local_rsds = np.mean(local_rsds)
            sd_local_rsds = np.std(local_rsds)
            
            mean_local_lmeans = np.mean(local_lmeans)
            sd_local_lmeans = np.std(local_lmeans)
            mean_local_lsds = np.mean(local_lsds)
            sd_local_lsds = np.std(local_lsds)
            
            outl_rmean = (rmean - mean_local_rmeans) / sd_local_rmeans > self.blink_mean_threshold
            outl_rsd = (rsd - mean_local_rsds) / sd_local_rsds > self.blink_sd_threshold
            outl_r = outl_rmean and outl_rsd
            
            outl_lmean = (lmean - mean_local_lmeans) / sd_local_lmeans > self.blink_mean_threshold
            outl_lsd = (lsd - mean_local_lsds) / sd_local_lsds > self.blink_sd_threshold
            outl_l = outl_lmean and outl_lsd
            
            if outl_r:
                rbl = np.append(rbl, times[i])
            if outl_l:
                lbl = np.append(lbl, times[i])
            
        return rbl, lbl, rmeans, lmeans, rsds, lsds 
            
    def heartRates(self):
        times = np.array([])
        hrs = np.array([])
        for key in self.dataPoints:
            hr = self.dataPoints[key].heartRate
            times = np.append(times, key)
            hrs = np.append(hrs, hr)
        return times, hrs
    
    def gps(self):
        times = np.array([])
        gps = np.array([])
        gps = dict()
        for key in self.dataPoints:
            gp = self.dataPoints[key].gps
            times = np.append(times, key)
            gps = np.append(gps, gp)
        return times, gps

dataset = "indoor"

if dataset == "indoor":
    indoor12 = GlassData(['Indoor/Participant_1/AFE_000_CONFIDENTIAL.json',
                           'Indoor/Participant_1/AFE_001_CONFIDENTIAL.json',
                           'Indoor/Participant_1/AFE_002_CONFIDENTIAL.json',
                           'Indoor/Participant_1/AFE_003_CONFIDENTIAL.json'])
else:
    indoor1 = GlassData(["labeled.json"])

timesTI1, tempRates_indoor1 = indoor1.tempRates()
timesTI2, reyeX_indoor1, reyeY_indoor1, leyeX_indoor1, leyeY_indoor1, rbrightness, lbrightness = indoor1.eyePositions()
rblinks_indoor1, lblinks_indoor1, rmeans, lmeans, rsds, lsds = indoor1.blinks()

tempDF = pd.DataFrame({"times": timesTI1, "t": tempRates_indoor1})
eyePDF = pd.DataFrame({"times": timesTI2, "reyeX": reyeX_indoor1, "reyeY": reyeY_indoor1,
                       "leyeX" : leyeX_indoor1, "leyeY" : leyeY_indoor1})
rblinkDF = pd.DataFrame({"rblink": rblinks_indoor1})
lblinkDF = pd.DataFrame({"lblink": lblinks_indoor1})

brightnessDF = pd.DataFrame({"times": timesTI2, "rbrightness": rbrightness, "lbrightness": lbrightness})

(
ggplot(tempDF)
    + aes(x="times", y="t")
    + geom_line()
)
(
    ggplot(eyePDF)
    + aes(x="times")
    + geom_line(aes(y="reyeX"), color="red")
    + geom_line(aes(y="reyeY"), color="blue")
    + geom_line(aes(y="leyeX"), color="green", linetype="-")
    + geom_line(aes(y="leyeY"), color="orange", linetype="--")
    + geom_vline(data=rblinkDF, mapping=aes(xintercept="rblink"), color="red")
    + geom_vline(data=lblinkDF, mapping=aes(xintercept="lblink"),
                 color="green", linetype="--")
)
(
    ggplot(eyePDF)
    + aes(x="times")
    + geom_line(aes(y="reyeX"), color="red")
    + geom_line(aes(y="reyeY"), color="blue")
    + geom_vline(data=rblinkDF, mapping=aes(xintercept="rblink"),
                 color="green", linetype="--")
)
(
    ggplot(eyePDF)
    + aes(x="times")
    + geom_line(aes(y="leyeX"), color="green", linetype="-.")
    + geom_line(aes(y="leyeY"), color="orange", linetype="-.")
    + geom_vline(data=lblinkDF, mapping=aes(xintercept="lblink"),
                 color="brown", linetype="--")
)
(
    ggplot(brightnessDF)
    + aes(x="times")
    + geom_line(aes(y="rbrightness"), color="red", linetype="-")
    + geom_line(aes(y="lbrightness"), color="green", linetype="-")
    + geom_vline(data=lblinkDF, mapping=aes(xintercept="lblink"),
                 color="brown", linetype="--")
    + geom_vline(data=lblinkDF, mapping=aes(xintercept="lblink"),
                 color="brown", linetype="-")
)
