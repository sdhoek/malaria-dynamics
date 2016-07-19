#from pcraster import *
from numpy import random
import matplotlib.pyplot as plt
import numpy
import inspect

import fiona
from pandas import DataFrame, read_csv
import math

#custom classes (must be in same directory)
from clock import *
from SEIprototype import *
from agents import *

       
#### CLASS DEFINITION MOSQUITO ######
class Mosquito(Point):
	
    def __init__(self, x=650, y=600):
        self.id = id(self)
	self.x = x
	self.y = y
	self.orientation = numpy.random.uniform(0,360)
	self.digestTime = 0
	
	self.age = 0.0  #in days, resets when turning adult
       
    # SEI Model            
	self.SEI = SEI() 
	self.state = "adult"
	self.hungry = True
		## Hungry is placeholder for states
	self.eggsAmount = 35		
	self.interactRange = 20 #meter		
	self.perceptionRange = 100 #meter	
	self.movSpeed = 25 #M/hour
	self.developLarva = 0
	self.developLarvaMax = 1
	self.skeletonHarden = 0
	self.skeletonHardenMax = 1
	
		
		
		#states = [egg, larva, pupa, immature adult, bloodmealseek, digest, gravid]


    def development(self, temperature): 
        self.age += 0.04166666667    #day/ticksperday
        if (self.state == "egg") and (self.age >= 2): 
            #TODO: Make probabilistic?
            self.state = "larva"
            self.age = 0 
        elif (self.state == "larva"):
            self.developLarva += (temperature * 0.000305) - 0.003285
            #Transition if threshold is reached
            if self.developLarva >= self.developLarvaMax:
                del self.developLarva
                del self.developLarvaMax
                self.state = "pupa"
                self.age = 0
        elif (self.state == "pupa") and (self.age >= 1): 
            #TODO: Make probabilistic?
            self.state = "IA"
            self.age = 0
        elif (self.state == "IA"):
            self.skeletonHarden+= 1.0/((temperature *-2.18) +117.0)
            if self.skeletonHarden >= self.skeletonHardenMax:
                self.state = "adult"
                del self.skeletonHarden
                del self.skeletonHardenMax
                
            
    def newMove(self, clock, humancontainer, habitatcontainer, mosquitocontainer):
        
        if (self.state == 'adult') and (clock.isNight): 
            if self.hungry:
                near = self.near(self.perceptionRange, humancontainer)
                if len(near) != 0:
                    closest = self.closest(near)
                    if (closest.distanceTo <self.interactRange):
                        self.sting(closest)
                    elif (closest.distanceTo <self.perceptionRange):
                        self.setOrientation(self.bearing(closest))
                        self.move(5) 
                    else: 
                        self.moveRandom(self.movSpeed)
                else:
                    self.moveRandom(self.movSpeed)
                    
                    
                    
            elif self.hungry == False:
                self.digest()
                
                near = self.near(self.perceptionRange,habitatcontainer)
                if len(near) != 0:
                    closest = self.closest(near)
                    if closest.distanceTo < self.interactRange:
                        if self.digestTime <= 0:
                            eggs = self.layEggs()
                            mosquitocontainer.extend(eggs)
                    elif (closest.distanceTo < self.perceptionRange):
                        self.setOrientation(self.bearing(closest))
                        self.move(5)
                    else:
                        self.moveRandom(self.movSpeed)
                else:
                    self.moveRandom(self.movSpeed)
                
         
                
    def digest(self):
        if self.hungry == False:
            self.digestTime -= 1
        
            
    def move(self, velocity):
        # Move forward based on orientation and velocity
        dx = math.sin(math.radians(self.orientation)) * float(velocity)
        dy = math.cos(math.radians(self.orientation)) * float(velocity)
        self.x += dx
        self.y += dy
    
    def moveRandom(self, velocity): 
        self.setOrientation(numpy.random.randint(0, 360))
        self.move(velocity)
            
    def setOrientation(self, newOrientation):
        #sets new orientation in degrees
        self.orientation = newOrientation
		
    def sting(self, human): 

        self.hungry = False
        self.digestTime = 72 # hours
        # If mosquito is infected and human is susceptible -> infected human
        if isinstance(self.SEI.currentState, I) and isinstance(human.SEI.currentState, S): 
            human.SEI.getInfected()
        #If human is infected and self is susceptible --> infected self
        elif isinstance(human.SEI.currentState, I) and isinstance(self.SEI.currentState, S):
            self.SEI.getInfected()
        
            
    # Birth rule
    def layEggs(self):
        self.hungry = True
        #Return new mosquitos in function
        newmozzies =[]
        for i in range(self.eggsAmount):
            newmozzies.append(Mosquito(self.x, self.y))
            newmozzies[i].state = "egg"
        return newmozzies
    def die(self): 
        pass
        
        #### KILL SELF HERE
        # Death rule
        # calcDeathchance returns true if agent has to die
    def calcDeathchance(self):
        rand = numpy.random.uniform(0,1)

        #No adult -> static, hourly deathrate
        if (self.state != "adult"):
            self.mortalityRate = 0.1
            if rand <= self.mortalityRate: 
                return True

        # adult -> age dependent
        elif (self.state == "adult"): 
            self.mortalityRate = self.ageMortalityRate() 
            if rand <= self.mortalityRate: 
                return True
                
    def ageMortalityRate(self): 
        a = 0.005
        b = 7.0
        s = 0.7
    
        self.MRdaily = (a*math.exp(self.age/b))/(1.0+a*s*b*(math.expm1(self.age/b)-1.0))
        self.SRdaily = 1.0 - self.MRdaily
        self.SRhourly = self.SRdaily**(1.0/24.0)
        self.MRhourly = 1.0 - self.SRhourly
        return self.MRdaily
        #return self.MRhourly
        
        
        #Check rasters
    def checkRaster(self, raster):
        self.rasterval = cellvalue(raster, self.getPCRx(), self.getPCRy())[0]
        return self.rasterval
	    
    def getPCRy(self): 
        return int(self.x/cellsize)
	    
    def getPCRx(self): 
        return int((self.y/cellsize)*-1+250) #250 is rowindexlengh
        
