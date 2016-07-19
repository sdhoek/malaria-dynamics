#### CLASS DEFINITON CLOCK

class Clock(object): 
    def __init__(self): 
        self.hours = 0
        self.isNight = True
        self.month = 'january'
        #Foo added so months number matches index number logically
        self.months = ('foo', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')
        self.daysPerMonth = {'january': 31, 'february': 28, 'march': 31, 'april':30, 'may':31, 'june':30, 'july':31, 'august':31, 'september':30, 'october': 31, 'november':30, 'december':31}
        self.dayCounter = 1
        
    def tick(self):
        self.hours +=1
        #if 24:00, reset clock to 0:00
        if self.hours >= 24: 
            self.hours = 0
            self.monthlyTick()
        self.setNightTime()
    
    def setNightTime(self): 
        if (self.hours >=  0) and (self.hours <= 6):
            self.isNight = True
            
        elif (self.hours >= 18): 
            self.isNight = True
        else: 
            self.isNight = False
            
    def monthlyTick(self): 
        #switch to new day
        self.dayCounter +=1
         
        if self.dayCounter > self.daysPerMonth[self.month]:   
            #Reset daycounter back to 1 if daycount exceeds days per month
            self.dayCounter = 1
            newMonthIdx = self.months.index(self.month)+1
            if newMonthIdx > 12:
                #Reset back to first month if end of year
                self.month = self.months[1]
            else: 
                #Switch to next month if not end of year
                self.month = self.months[newMonthIdx]
        
        
    def tock(self): 
        print "the time is ", self.hours,  ":00 ", 'and the date is ', self.month, 'the ', str(self.dayCounter), 'th'
        if self.isNight:
            print "it is nighttime"
            
        else:
            print "it is daytime"

