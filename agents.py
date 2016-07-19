#### CLASS DEFINITION BOUNDING BOX 
import math
from shapely.geometry import Polygon, mapping, shape

class Raster(object): 
    def __init__(self): 
        self.data= []
        self.polygons = []
    def build(self, mapSize, rasterSize):
        ### Check correctness of division
        assert (mapSize % rasterSize) == 0, 'Cannot divide map because rasterSize does not fit in map'
        
        xAmount = mapSize / rasterSize
        yAmount = mapSize / rasterSize
        
        xmin = 0
        ymin = 0
        ymax = ymin + rasterSize
        ### Vertical loop
        for j in xrange(yAmount):
            ### Horizontal loop
            for i in xrange(xAmount):
                
                square = {'geometry':{}, 'id': None, 'properties': {}, 'type':'Feature'}
                square['id'] = id(square)
                xmax = xmin + rasterSize
                self.data.append(BoundingBox(xmin,xmax, ymin,ymax))
                square['geometry']  = Polygon([(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)])
                self.polygons.append(square)
                xmin = xmax
            # Reset variables for new vertical loop
            ymin = ymax
            ymax = ymin+rasterSize
            xmin = 0 
            
            



class BoundingBox(object):
    def __init__(self, xmin = 0, xmax = 0, ymin = 0, ymax =0):
	self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax

    def printSelf(self):
        print "xmin is:", self.xmin, "xmax is:", self.xmax, "ymin is:", self.ymin, "ymax is:", self.ymax

        # Check if there are any points within self
    def contains(self, points):
        #Check geometry correctness
        #if correct: continue
        if self.checkGeometry():
            contains = [point for point in points if ((point.x > self.xmin) and (point.x < self.xmax) and (point.y > self.ymin) and (point.y < self.ymax))]
            
            return contains
        #Raise error if false
        else:
            raise ValueError("Bounding Box Geometry NOT VALID")

    def checkGeometry(self):
        #implement more thorough check?
        if self.xmin > self.xmax:
            return False
        elif self.ymin > self.ymax:
            return False
        else:
            return True
    def __str__(self): 
        return "BBOX Object "+ ' xmin: '+ str(self.xmin)+ ' xmax: '+ str(self.xmax)+ ' ymin: '+ str(self.ymin)+ ' ymax: '+ str(self.ymax)


class Point(object):
    import math
    def __init__(self, x = 0.0, y= 0.0, orientation = 0):
        self.x = x
        self.y = y
        self.orientation = orientation

    def move(self, velocity):
        # Move forward based on orientation and velocity
        dx = math.sin(math.radians(self.orientation)) * float(velocity)
        dy = math.cos(math.radians(self.orientation)) * float(velocity)
        self.x += dx
        self.y += dy

    def setOrientation(self, newOrientation):
        #sets new orientation in degrees
        self.orientation = newOrientation

    def printSelf(self):
        print self.x, self.y

    def buffer(self, size):
        # creates a set of 360 points for each degree around a circle
        bufferGeom =[]
        for i in range(360):
            bufferGeom.append(( math.sin(math.radians(i))*size , math.cos(math.radians(i))*size ))

        return bufferGeom

    def distanceToPoint(self, point):
        #Use pythagoras to calculate distance between self and other point

        dx = point.x - self.x
        dy = point.y - self.y
        distance = math.sqrt( (dx**2.0) + (dy**2.0) )

        return distance

    def bearing(self, point):
        #Calculate bearing in degrees from self to other point
        dx = float(point.x - self.x)
        dy = float(point.y - self.y)

        if dx > 0.0:
            bearing = 90.0 - math.degrees(math.atan(dy/dx))
        if dx < 0.0:
            bearing = 270.0 - math.degrees(math.atan(dy/dx))
        if dx == 0.0:
            if dy > 0.0:
                bearing = 0.0
            if dy < 0.0:
                bearing = 180.0
            if dy == 0.0:
                bearing = 0.0

        return bearing # in degrees


    def getBoundingBox(self, length):
        #length = distance between x and xmin
        xmin = float(self.x-(length))
        xmax = float(self.x+(length))
        ymin = float(self.y-(length))
        ymax = float(self.y+(length))

        return BoundingBox(xmin, xmax, ymin, ymax)


    def near(self, boundingBox, agentSet):
            #Returns list of agents that fall within bounding box
            #If input is not a BoundingBox() instance, create a BoundingBox() instance with the int/float element
        try:
            if type(boundingBox) != type(BoundingBox()):
                boundingBox = self.getBoundingBox(boundingBox)


            nearAgents = boundingBox.contains(agentSet)

            return nearAgents
        except:
            raise ValueError("something is wrong in near function")

    def closest(self, agentList):
        """return min(agentList, key=agentList.distanceTo)    IMPLEMENT EXISTING PYTHON MIN FUNCTION????"""
        
        
        #add distance attribute to agentList
        for agent in agentList:
            agent.distanceTo = self.distanceToPoint(agent)
        # If there is only 1 agent, this agent is automatically the closest    
        if len(agentList) == 1: 
            return agentList[0]            
        
        #First item in list as default
        theclosest = agentList[0]

        for agent in agentList:
            #if item in list is closer than current one
            if theclosest.distanceTo > agent.distanceTo:
                #replace theclosest with new agent with lowest value
                theclosest = agent
        #returns closest agent
        return theclosest
