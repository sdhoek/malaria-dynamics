import numpy as np
class Map(object): 
    def __init__(self, lowerX = 0, lowerY=0, upperX=0, upperY=0):
        self.lowerX = lowerX
        self.lowerY = lowerY
        self.upperX = upperX
        self.upperY = upperY
        
    def outOfBounds(self, agent):
        #  Check if agent is within or outside of map bounds. Returns true if agent is out of bounds
        if (agent.x >= self.upperX) or (agent.x <= self.lowerX ) or (agent.y >= self.upperY) or (agent.y <= self.lowerY):
            return True
        else:
            return False
            
            
    def rainfallAmount(self):
        ##Calculate amount of rain falling on rainy day
        probability = np.random.uniform(0,1)
        if probability < 0.01:
            amount = np.random.randint(100,150)
        elif probability <0.03:
            amount = np.random.randint(50, 100)
        elif probability <0.23:
            amount = np.random.randint(20,50)
        elif probability <0.44:
            amount = np.random.randint(10,20)
        elif probability < 0.61:
            amount = np.random.randint(5,10)
        elif probability <= 1:
            amount = np.random.uniform(0.5, 5)
        return amount
        
            
    def rain(self, daysPerMonth, rainyDays):
        ## Calculate daily possibility of rainfall, returns 0 if no rain occurs
         rainyDayChance = rainyDays/daysPerMonth
         if (np.random.uniform(0,1) < rainyDayChance ) :
            return self.rainfallAmount()
         else:
            return 0
                
    
       