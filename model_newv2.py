#from pcraster import *
from numpy import random
import matplotlib.pyplot as plt
import numpy as np
import inspect
import shapely
import os
import fiona
from pandas import DataFrame, read_csv
import pandas as pd
import math

#custom classes (must be in same directory)
from clock import *
from SEIprototype import *
from agents import *
from mosquito import Mosquito
from habitat import Habitat
from map import Map




class Human(Point):
    def __init__(self, x=0, y=0, age= None):
        self.id = 0
	self.x = x
	self.y = y
	self.SEI = SEI() 
	self.age = age
	self.timesStung = None
	
    def removeHabitat(self):
        pass
        
    def near(self):
        pass

class Tracker(object):
    def __init__(self):
        
        self.tick = []
        self.totalMosquitos = []
        self.totalHumans = []
        self.totalHabitats = []

		
class Model(object):
    def __init__(self):
        self.tick = 0
        
        self.clock = Clock()
        
        self.agentContainer = {'humanContainer': [], 'mosquitoContainer': [], 'habitatContainer': []}
        self.fieldContainer = {'climate': None,'precipitation': None, 'temperature': None}
        self.environment = Map(0,0,1250,1250)
        
        self.options = {'graph': True, 'animation': True, 'saveOutput':True}
        self.tracker = Tracker()
        
        self.saveRaster = None
        
        
    def createInstance(self, container, agentType, amount):
        for i in xrange(amount):
            container.append(agentType)
        
    def run(self, ticks):
        self.ticks = ticks
        for tick in xrange(self.ticks): 
            # Enable time in model
            self.clock.tick()
            self.tick = tick
            
            if self.tick % 100 == 0:
                print self.agentContainer['habitatContainer'][0].getCarryingCapacity()
                print self.tick
                
            ######## Environment part
            self.fieldContainer['temperature'] = self.fieldContainer['climate'].loc[self.clock.month, 'h'+str(self.clock.hours) ]
            self.fieldContainer['monthPrecipitation'] = self.fieldContainer['climate'].loc[self.clock.month, 'precipitation']
            self.fieldContainer['rainyDays'] =self.fieldContainer['climate'].loc[self.clock.month, 'rainydays']
            
            self.environment.rainToday = 0
            
            if self.clock.hours == 6:
               self.environment.rainToday = self.environment.rain( float(self.clock.daysPerMonth[self.clock.month]) , float(self.fieldContainer['rainyDays']) )
               
            
            self.fieldContainer['hourlyPrecipitation'] =self.fieldContainer['monthPrecipitation']  / self.clock.daysPerMonth[self.clock.month] / 24.0
            
            
            ######## Habitat part
            for habitat in self.agentContainer['habitatContainer']:
                habitat.waterBalance(self.environment.rainToday)
                #Calculate carrying capacity( m3 * 6.25) and biomass (non adult = 1) in a range of 25 meters for each habitat
                carryingCapacity = int(habitat.getCarryingCapacity())
                biomass = habitat.getBiomass(self.agentContainer['mosquitoContainer'])
               
                
                if biomass > carryingCapacity:
                    # pick newest slice of non adult mosquios from the pool to simulate cannibalism
                   toBeRemoved =  habitat.nonAdults[(carryingCapacity-(biomass-carryingCapacity)):carryingCapacity]
                   # Remove these eggs from the total container
                   for agent in toBeRemoved:
                       self.agentContainer['mosquitoContainer'].remove(agent)
            
            ######## Human immigration
            
            rand = np.random.uniform(0,1)
            if rand < 0.001:
                ### make this dependent on village contours?
                human = Human(np.random.randint(500,800), np.random.randint(500,800), np.random.randint(20,50))
                if rand <0.0005:
                    human.SEI.currentState = I()
                self.agentContainer['humanContainer'].append(human)
 
     
            ####### Human emigration 
            
             
            rand3 = np.random.uniform(0,1)
            if rand3 < 0.001:
                rand2 = np.random.randint(0, len(self.agentContainer['humanContainer']))
                self.agentContainer['humanContainer'].pop(rand2-1)
                
     
             
            ######## Human part
            for human in self.agentContainer['humanContainer']:
                #run SEI model
                human.SEI.run_all()
                
            ####### Mosquito part
            for mosquito in self.agentContainer['mosquitoContainer']:
            #Calculate once per day if mosquito should die
                if self.clock.hours == 6: 
                    if mosquito.calcDeathchance(): 
                        self.agentContainer['mosquitoContainer'].remove(mosquito)
                        continue
                
                #TO DO: Fix conversion formula
                # Out of bounds check: 
                
                if self.environment.outOfBounds(mosquito):
                      #remove out of bounds mosquitos
                      self.agentContainer['mosquitoContainer'].remove(mosquito)
                      continue
                # GENERAL MOZZIE FUNCTIONS
                
                #Get older (runs age of mosquitos)
                mosquito.development(self.fieldContainer['temperature'])
                #run SEI model. 
                mosquito.SEI.run_all()
                #run mosquito movement
                mosquito.newMove(self.clock, self.agentContainer['humanContainer'], self.agentContainer['habitatContainer'], self.agentContainer['mosquitoContainer'])  
                
            
            #### DATA SAVE###
            ## save module
            #Save data every month
            if self.tick % (30*24) == 0:
                
                self.save()
            
           
            ########Visualisation engine########
            if self.options['graph']:
                self.graphPlotter()
            if self.options['animation']:
                self.animationPlotter()
                
            
           
           
    def animationPlotter(self):
        if self.tick == 0:
            plt.ion()
        ## plotting module 
        if self.clock.isNight: 
            #Plot all mosquitos, humans and mosquitos
            mozziex, mozziey = [mosquito.x for mosquito in self.agentContainer['mosquitoContainer']], [mosquito.y for mosquito in self.agentContainer['mosquitoContainer']]
         
            humanx, humany = [human.x for human in self.agentContainer['humanContainer']], [human.y for human in self.agentContainer['humanContainer']]
            
            habitatx, habitaty = [habitat.x for habitat in self.agentContainer['habitatContainer']], [habitat.y for habitat in self.agentContainer['habitatContainer']]
             
            plt.plot(mozziex, mozziey, 'o', color = 'blue')
            plt.plot(humanx, humany, 'x', color = 'red')
            plt.plot(habitatx, habitaty, 'x', color = 'green')
            plt.ylim([self.environment.lowerY, self.environment.upperY])
            plt.xlim([self.environment.lowerX, self.environment.upperX])
            plt.draw()
            plt.pause(0.0001)
            plt.clf()
            
    def graphPlotter(self):
        #put initial settings here
        if self.tick == 0:
            #Create lists to keep track of total values
            self.tracker.totalMosquitosInfected = []
            self.tracker.totalHumansInfected =[]
            self.tracker.adultMosquitos = []
            self.tracker.totalHumans = []

       
        # Calc totals
        infHumans =  [human for human in myModel.agentContainer['humanContainer'] if isinstance(human.SEI.currentState, I)]   
        infMosquitos = [mosquito for mosquito in self.agentContainer['mosquitoContainer'] if isinstance(mosquito.SEI.currentState, I)]
        adultMosquitos = [mosquito for mosquito in self.agentContainer['mosquitoContainer'] if mosquito.state == 'adult']
        # Append totals to list 
        self.tracker.tick.append(self.tick)
        self.tracker.totalMosquitos.append(len(self.agentContainer['mosquitoContainer']))
        self.tracker.totalMosquitosInfected.append(len(infMosquitos))
        self.tracker.totalHumansInfected.append(len(infHumans))
        self.tracker.adultMosquitos.append(len(adultMosquitos))
        self.tracker.totalHumans.append(len(self.agentContainer['humanContainer']))
        # Show list at final tick
        if self.tick == (self.ticks-1):
            plt.plot(self.tracker.totalHumans, 'r--', self.tracker.adultMosquitos, 'b--', self.tracker.totalMosquitosInfected, 'g', self.tracker.totalHumansInfected, 'y')
            plt.show()
            plt.savefig(outputFolder+'graph.png')
            
    def save(self): 
        # Open raster file that serves as blueprint for saving data. 
        with fiona.open('C:/Users/Sjors/Dropbox/GIMAMasterThesis/OOMscripts/mold.shp', 'r') as blueprint:
            blueprintRaster = list(blueprint)
            schema = blueprint.schema
            
        
        # Create copy of container
        mosquitos = self.agentContainer['mosquitoContainer']
        humans= self.agentContainer['humanContainer']
               
        for square in blueprintRaster: 
            
            #Replace geometry dictionary with shapely polygon object
            square['geometry'] = shape(square['geometry'])
            
            #Get list of mosquitos inside geometry of square
            mosquitoInSquare = [mosquito for mosquito in mosquitos if square['geometry'].contains(shapely.geometry.Point(mosquito.x, mosquito.y))]
            #Get list of humans inside geometry of square
            humanInSquare = [human for human in humans if square['geometry'].contains(shapely.geometry.Point(human.x, human.y))]
            
            #Mosquito total
            square['properties']['mtotal'] = len(mosquitoInSquare)
            #Mosquito adult total
            square['properties']['madult'] = len([mosquito for mosquito in mosquitoInSquare if mosquito.state == 'adult'])
            #Mosquito infected total
            square['properties']['minfect'] = len([mosquito for mosquito in mosquitoInSquare if isinstance(mosquito.SEI.currentState, (I,E))])
            #Human total
            square['properties']['htotal'] = len(humanInSquare)
            #Human infected total
            square['properties']['hinfect'] = len([human for human in humanInSquare if isinstance(human.SEI.currentState, (I, E))])
            
            
            # Remove mosquitos and humans that are already found from the list to be searched
            mosquitos = [mosquito for mosquito in mosquitos if mosquito not in mosquitoInSquare]
            humans = [human for human in humans if human not in humanInSquare]
        
        ## Write data to file
        with fiona.open(outputFolder+str(self.tick)+'.shp', 'w', 'ESRI Shapefile', schema) as output: 
            for square in blueprintRaster:
                ## Write output in file, filename has tick as name
                output.write({
                                'geometry': mapping(square['geometry']),
                                'properties': square['properties']
                                })
            
          
for i in xrange(23,100):
    myModel = Model()
    ######## SETTINGS###########
    #Select folder for model output
    outputFolder = 'C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\OOMscripts\\stability\\stability'+str(i)+'\\'
    tickCount = 25000
    
    
    
    # Create folder if it does not yet exist
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
        
    #### LOAD human locations
    
    humans = fiona.open("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\human_v2.shp")
    for feat in humans:  
        human = Human(feat['geometry']['coordinates'][0],feat['geometry']['coordinates'][1], feat['properties']['age'])
        human.SEI.totalInfections = feat['properties']['prev_infec']
        human.SEI.totalInfections = 0
        if random.randint(1,2) == 2: 
            human.SEI.currentState = I()
        myModel.agentContainer['humanContainer'].append(human)
    
    #### LOAD HABITATS
    habitats = fiona.open("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\habitat.shp")
   
    for feat in habitats:   
        habitat = Habitat(feat['geometry']['coordinates'][0],feat['geometry']['coordinates'][1])
        habitat.size = 50
        myModel.agentContainer['habitatContainer'].append(habitat)
        
    # Create mosquitos 
    for i in xrange(500):   #500 initial mozzies
        myModel.agentContainer['mosquitoContainer'].append(Mosquito())
        myModel.agentContainer['mosquitoContainer'][i].age = np.random.randint(0,40) #initial age between 0 and 40 days
        myModel.agentContainer['mosquitoContainer'][i].x = np.random.randint(0,1250)
        myModel.agentContainer['mosquitoContainer'][i].y = np.random.randint(0,1250)
        if (i % 2) == 0:
            myModel.agentContainer['mosquitoContainer'][i].SEI.currentState = I()
            
    ## Load in temperature data
    myModel.fieldContainer['climate'] = read_csv('C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\OOMscripts\\climateBoboDioulassov2.csv', sep=';', index_col='name')
    
    
    #### SAVE INITIAL SETTINGS
    initial = {}
    initial['humanCount'] = len(myModel.agentContainer['humanContainer'])
    initial['habitatCount'] = len(myModel.agentContainer['habitatContainer'])
    initial['mosquitoCount'] = len(myModel.agentContainer['mosquitoContainer'])
    initial['habitatSize'] = myModel.agentContainer['habitatContainer'][0].size
    initial['habitatMosquitoPerm3'] = myModel.agentContainer['habitatContainer'][0].mosquitoPerM3
    initial['habitatEvaporationRate'] = myModel.agentContainer['habitatContainer'][0].evaporationRate
    initial['mosquitoEggsAmount'] = myModel.agentContainer['mosquitoContainer'][0].eggsAmount
    initial['mosquitoInteractRange'] = myModel.agentContainer['mosquitoContainer'][0].interactRange
    initial['mosquitoPerceptionRange'] = myModel.agentContainer['mosquitoContainer'][0].perceptionRange
    initial['mosquitoMoveSpeed'] = myModel.agentContainer['mosquitoContainer'][0].movSpeed
    initial['tickCount'] = tickCount
    df = pd.DataFrame()
    df = df.from_dict(initial, orient='index')
    df.to_csv(outputFolder+'initialSettings.csv')
    
    
    
    
    myModel.run(tickCount) 



































#### PCRASTER SETUP ######
""""
setclone("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\clonemap2.map")

habitat = readmap("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\habitat2.map")
human = readmap("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\human_v2.map")
#create "near" maps
fakehabitatdem= spreadmax(habitat, 1, 1, 100)
dirhabitat= lddcreate(fakehabitatdem, 9999999,999999,9999999,9999999)
fakehumandem =spreadmax(human,1,1,100)
dirhuman = lddcreate(fakehumandem, 9999999,999999,9999999,9999999)

#### MODEL SETUP ######

## To do: Access map clone attributes and use these in class definition
cellsize = 5



  

"""
#df.to_excel("C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\test5.xls")
# Save map 
#report(fakehumandem, "C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\Data\\humandem.map")


