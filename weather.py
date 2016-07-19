months= {1: 'january', 2: 'february', 3:'march', 4: 'april', 5: 'may', 6:'june', 7:'july', 8:'august', 9:'september',10: 'october',11: 'november',12: 'december'}        


import pandas
from clock import *
dailyWeather = pandas.read_csv('C:\\Users\\Sjors\\Dropbox\\GIMAMasterThesis\\OOMscripts\\climateBoboDioulassov2.csv', sep=';', index_col='name')

myclock = Clock()


for i in xrange(34):
    myclock.tick()
    hourlyTemperature = dailyWeather.loc[myclock.month, 'h'+str(myclock.hours) ]

    monthlyPrecip = dailyWeather.loc[myclock.month, 'precipitation']
    hourlyPrecip = monthlyPrecip / myclock.daysPerMonth[myclock.month] / 24.0
    print hourlyPrecip
