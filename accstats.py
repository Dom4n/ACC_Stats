__author__ = 'Doman'

'''
TEN SKRYPT ma za zadanie parsować plik logfile_console_XXXX.log,
dane z niego wyciągnięte:
nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
dane te mają zostać zapisane w bazie danych lub json

INNY SKRYPT(?) ma pozwolić na otworzenie bazy danych lub json
i dowolne parsowanie danych po tych parametrach:
- gracz -> w jakich dniach grał, zawężenie wyników
- dzień/ilość graczy
- dzień/długość misji
oraz wyświetlanie wyników na wykresach
'''

from pandas import *
from datetime import *
from dateutil.relativedelta import *
import numpy as np
import matplotlib.pyplot as plt
import os, glob, time, datetime, fileinput, re, csv

directory = 'F:/LOGS/test'

# zmienia folder
#TODO: może argumentem to przesyłać? /kiedyś
def changeDir(self, directory):
    os.chdir(directory)
    print(os.getcwd())

# szuka zgodnego pliku
# misja musi się zacząć (do wybrania slotów) pomiędzy 20 a 21!
#TODO: zmieinć z czasu rozpoczęcia gry na czas załadowania misji!
def findFile(self):
    log = glob.glob('logfile_console*.log')
    names = []
    mtimes = []
    for i in log:
        #t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(i)))
        t = time.gmtime(os.path.getmtime(i))
        #if t.tm_hour >= 20:
        if 1:
            t = time.strftime('%Y-%m-%d %H:%M:%S', t)
        #t = os.path.getmtime(i)
        #print(os.path.getmtime(i))
            names.append(i)
            mtimes.append(t)

    d = {'mtimes' : mtimes,
         'names' : names}
    dfilelist = DataFrame(d)
    dfilelist = dfilelist.sort('mtimes')
    return dfilelist

# kasuje powtarzające się nazwy
def uniq(self, input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output

# parser danych z logfile
#TODO: do generalnej przebudowy!!
def parserLogfile(self):
    alldata = DataFrame(columns=['time','duration','misja','ilosc','gracze'])
    onedata = DataFrame(columns=['time','duration','misja','ilosc','gracze'])
    for file in dfilelist.values:

        file = file[1]
        logg = open(file, "r")
        gracze = []
        ilosc = 0

        for line in logg:

            if re.match("(.*)(Game started|Game restarted)(.*)", line):
                t1 = re.search("((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)", line).group(1)
                t2 = re.search("^2[0-3]", t1)
                try:
                    t2 = t2.group(0)
                except:
                    break

            if re.match("(.*)mission=(.*)", line):
                misja = re.search(".*?(\".*?\")", line).group(1).replace('\"', '')

            if re.match("(.*)duration=(.*)", line):
                duration = re.search("\d+", line).group(0)
                duration = round((int(duration)/60), 1)

            if re.match("(.*)name=(.*)", line):
                gracz = re.search(".*?(\".*?\")", line).group(1)
                gracz = gracz.replace('\"', '')
                gracze.append(gracz)

            ######
                czasepoch = os.path.getmtime(file)
                czasepoch = datetime.datetime.fromtimestamp(czasepoch)
                t3 = time.strptime(t1, '%H:%M:%S')
                if (t3.tm_hour+(duration/60) >= 24) or (t3.tm_hour < 20):
                    #print(czasepoch)
                    czasepoch = czasepoch+relativedelta(days=-1)
                czas = time.strftime('%Y %m %d', czasepoch.timetuple())
            #####
            try:
                ilosc = len(gracze)
                d0 = {'time':czas,
                      'duration':duration,
                      'misja':misja,
                      'ilosc':ilosc,
                      'gracze':[gracze]}
                onedata = onedata.append(DataFrame(d0, columns=['time','duration','misja','ilosc','gracze'], index=[misja]))
                #print(onedata)
            except:
                pass

            if re.match("(.*)Waiting for next game(.*)", line):
                gracze = []
                #print(onedata)
                #break

        if (ilosc > 4 ) and (duration > 1):
            #czas = time.gmtime(os.path.getmtime(file))
            #if (czasepoch.tm_hour+duration >= 24):
            #    czasepoch.tm_mday = czasepoch.tm_mday - 1


            #gracze = uniq(gracze)
            #ilosc = len(gracze)

            #d1 = {'time':czas,
             #     'duration':duration,
              #   'misja':misja,
               #  'ilosc':ilosc,
                # 'gracze':[gracze]}

            #alldata = alldata.append(DataFrame(d1, columns=['time','duration','misja','ilosc','gracze']))
            maks = onedata['duration'].idxmax()
            print(maks)
            #onedata.loc[maks]
            alldata = alldata.append(onedata.loc[maks])


    maks = onedata['duration'].idxmax()
    print(maks)
    onedata.loc[maks]

## Jakieś gówno
def gowno(self):
    czasepoch = os.path.getmtime(file)
    czase2 = datetime.datetime.fromtimestamp(czasepoch)
    print(czase2)
    czase2 = czase2+relativedelta(minutes=-duration)
    print(czase2)
    czase2

    print(t1)
    t3 = time.strptime(t1, '%H:%M:%S')
    t3

    czase2-relativedelta(days=1)




