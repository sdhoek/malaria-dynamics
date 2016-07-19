from agents import *

class Habitat(Point):
    def __init__(self, x=0, y=0, size = 20):
	self.id = 0
	self.x=x
	self.y=y
	self.currentBiomass = None
	self.maxCarryingCapacity = None
	self.size = size # In m3 
	self.evaporationRate = (3.5/39.5)/24.0 #### Cubic Meter/hour
	self.mosquitoPerM3 = 6.25	

    def getBiomass(self, nearbyMosquitos):
        self.nearbyMosquitos = self.near(25, nearbyMosquitos)
        self.nonAdults = [element for element in self.nearbyMosquitos if element.state != 'adult']
        return len(self.nonAdults)
        #### nearby non-adult mosquitos
	    
    	    
    def getCarryingCapacity(self):
        self.carryingCapacity = self.mosquitoPerM3 * self.size
	return self.carryingCapacity
	   
    
    def kill(self):
        pass
        
        #### Remove too many mosquitos
    def evaporate(self):
        ## Reduces habitatsize by a set evaporationRate
	self.size -= self.evaporationRate
	    
    def fill(self, rainfall):
         ## Takes rainfall in mm as input
        ## fill up pool size and converts rainfall in mm to cubic meters
	self.size += (rainfall/39.5) ### in cubic meters
    def waterBalance(self, rainfall):
        ## Takes rainfall in mm as input
    
	self.evaporate()
	self.fill(rainfall)
	
	##Sets size in m3 to 0 if value goes below zero -> pools cannot have a negative size
	if self.size < 0:
	    self.size  =0
	   