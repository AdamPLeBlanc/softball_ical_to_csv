#!/usr/bin/env python

import csv
import sys
import os
import datetime
import pytz

class IcalGame(object):
    def __init__(self,teamName,summary,startTime,endTime,location):
        #figure out the date & time
        dateFmt = "%Y%m%dT%H%M%S"
        utcTz = pytz.utc
        localTz = pytz.timezone("US/Pacific-New")
        self._startTime = datetime.datetime.strptime(startTime[:-1],dateFmt).replace(tzinfo=utcTz).astimezone(localTz)
        self._endTime = datetime.datetime.strptime(endTime[:-1],dateFmt).replace(tzinfo=utcTz).astimezone(localTz)
        #figure out the team names and who is home & away
        teamNames = [name.strip() for name in summary.split("vs.")]
        self._teamName = teamName
        self._opponentName = teamNames[1]
        self._dugout = "Away"
        if teamNames[1] == self._teamName:
            self._opponentName = teamNames[0]
            self._dugout = "Home"

        #set the location
        self._location = location

    @property
    def startDate(self):
        return self._startTime.strftime("%m/%d/%Y")

    @property
    def startTime(self):
        return self._startTime.strftime("%I:%M %p")

    @property
    def gameDuration(self):
        delta = self._endTime - self._startTime
        hours,seconds = divmod(delta.seconds,3600)
        minutes = seconds/60
        return "{0}:{1}".format(hours,minutes)

    @property
    def teamName(self):
        return self._teamName

    @property
    def opponentName(self):
        return self._opponentName

    @property
    def locationName(self):
        return self._location

    @property
    def dugout(self):
        return self._dugout

    def __str__(self):
        fields = ["Team","Opponent","Start Date","Start Time","Duration[HH:MM]","Dugout"]
        values = [self.teamName,self.opponentName,self.startDate,self.startTime,self.gameDuration,self.dugout]
        return os.linesep.join(["{0}: {1}".format(field,value) for field,value in zip(fields,values)])


def parseIcal(filePath):
    gameEvents = []
    for line in open(filePath,"rb"):
        line = line.strip()
        key,val = [x.strip() for x in line.split(':')]
        if key == "SUMMARY":
            summary = val
        elif key == "LOCATION":
            location = val
        elif key == "DTSTART":
            startTime = val
        elif key == "DTEND":
            endTime = val
        elif key == "END":
            gameEvents.append(IcalGame("Chosen Few",summary,startTime,endTime,location))

    return gameEvents

def createCsv(games,outPath):
    outStream = open(outPath,"wb")
    csvWriter = csv.writer(outStream,delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL)
    headerRow = ["Date","Time","Name","Opponent Name","Opponent Contact Name","Opponent Contact Phone Number","Opponent Contact E-mail Address",
                 "Location Name","Location Address","Location URL","Location Details","Home or Away","Uniform","Duration (HH:MM)","Arrival Time (Minutes)","Extra Label","Notes"]
    csvWriter.writerow(headerRow)
    for game in games:
        row = [game.startDate,game.startTime,game.teamName,game.opponentName,'','','',game.locationName,'','','',game.dugout,'',game.gameDuration,15,'','']
        csvWriter.writerow(row)

    outStream.close()



#main method
if "__main__" in __name__:
        if len(sys.argv) > 1:
            csvPath = "schedule.csv"
            path = sys.argv[1]
            gameEvents = parseIcal(path)
            #print "\n\n".join(map(str,gameEvents))
            createCsv(gameEvents,csvPath)

