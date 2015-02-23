__author__ = 'Doman'

'''
'PARSUJ' ma za zadanie parsować JEDEN plik logfile_console_XXXX.log,
dane z niego wyciągnięte:
data, nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
dane te mają zostać zapisane w bazie danych (lub json?)

'WYSWIETL' ma pozwolić na otworzenie bazy danych (lub json)
i dowolne parsowanie danych po tych parametrach:
- gracz -> w jakich dniach grał, zawężenie wyników
- dzień/ilość graczy
- dzień/długość misji
- ...
oraz wyświetlanie wyników na wykresach
'''

from pandas import *  # do gryzienia danych
from dateutil.relativedelta import *  # dokładne przeliczenia na datach
# import numpy as np
# import matplotlib.pyplot as plt
import os, glob, time, datetime, re


class Parsuj:
    def __init__(self):
        directory = 'C:/Users/Jarek/PycharmProjects/ACC Stats'
        self.changedir(directory)
        file = self.findfile()
        self.parserlogfile(file)

    # zmienia folder
    # TODO: może ścieżka jako argument? /kiedyś
    def changedir(self, directory):
        os.chdir(directory)
        print(os.getcwd())

    # szuka zgodnego pliku
    # zazwyczaj plik ma datę o jeden dzień w przód!!
    def findfile(self):
        log = glob.glob('logfile_console*.log')
        t = time.gmtime(os.path.getmtime(log[0]))
        t2 = time.strftime('%Y-%m-%d', t)
        plik = list([t2, log[0]])
        return plik

    # kasuje powtarzające się nazwy
    def uniq(self, wejscie):
        unikalne = []
        for x in wejscie:
            if x not in wejscie:
                unikalne.append(x)
        unikalne.sort()
        return unikalne

    # parser danych z logfile
    # TODO: do generalnej przebudowy!!
    def parserlogfile(self, file):
        # data, nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
        dane = DataFrame(columns=['data', 'nazwa_misji', 'mapa', 'dlugosc_misji',
                                  'ilosc_graczy', 'lista_graczy'])
        plik = open(file[1], "r")
        lista_graczy = []
        ilosc = 0
        dlugosc_misji = 0
        mapa = ''
        data = file[0]
        nazwa_misji = ''

        for line in plik:

            if 'Mission read' in line:
                endtime = line[:8]
                if not line.startswith('20'):
                    break

            if 'mission=' in line:
                nazwa_misji = line.split('"')[1]

            if 'island=' in line:
                mapa = line.split('"')[1]

            if 'duration=' in line:
                dlugosc_misji = float(line.split('=')[1][:5])

            if 'name=' in line:
                gracz = line.split('"')[1]
                lista_graczy.append(gracz)

            if ('Game restarted' in line) or ('Game finished' in line):
                endtime = line.split(' ')[0][:8]
                if endtime == '':
                    endtime = line.split(' ')[1][:8]
                endtime = time.strptime(endtime, '%H:%M:%S')
                if dlugosc_misji > 0:
                    if (endtime.tm_hour + (dlugosc_misji / 3600) >= 24) or (endtime.tm_hour < 20):
                        data = data + relativedelta(days=-1)
                        data = time.strftime('%Y %m %d', data.timetuple())

        ilosc = len(lista_graczy)
        global d0
        d0 = {'data': data,
              'nazwa_misji': nazwa_misji,
              'mapa': mapa,
              'dlugosc_misji': dlugosc_misji,
              'ilosc_graczy': ilosc,
              'lista_graczy': [lista_graczy]}
        # dane = dane.
        # onedata = onedata.append(
        #     DataFrame(d0, columns=['time', 'duration', 'misja', 'ilosc', 'gracze'], index=[misja]))
        # print(onedata)
        dane = DataFrame(d0, columns=['data',
                                      'nazwa_misji',
                                      'mapa',
                                      'dlugosc_misji',
                                      'ilosc_graczy',
                                      'lista_graczy'])

        print(d0)
        print(dane)

        # if (ilosc > 4 ) and (duration > 1):
            # czas = time.gmtime(os.path.getmtime(file))
            # if (czasepoch.tm_hour+duration >= 24):
            #    czasepoch.tm_mday = czasepoch.tm_mday - 1

            # gracze = uniq(gracze)
            # ilosc = len(gracze)

            # d1 = {'time':czas,
            #     'duration':duration,
            #   'misja':misja,
            #  'ilosc':ilosc,
            # 'gracze':[gracze]}

            # alldata = alldata.append(DataFrame(d1, columns=['time','duration','misja','ilosc','gracze']))
            # maks = onedata['duration'].idxmax()
            # print(maks)
            # onedata.loc[maks]
            # alldata = alldata.append(onedata.loc[maks])

        # maks = onedata['duration'].idxmax()
        # print(maks)
        # onedata.loc[maks]

    # # Jakieś gówno
    # def gowno(self):
    #     czasepoch = os.path.getmtime(file)
    #     czase2 = datetime.datetime.fromtimestamp(czasepoch)
    #     print(czase2)
    #     czase2 = czase2 + relativedelta(minutes=-duration)
    #     print(czase2)
    #     czase2
    #
    #     print(t1)
    #     t3 = time.strptime(t1, '%H:%M:%S')
    #     t3
    #
    #     czase2 - relativedelta(days=1)


#class Wyswietl(object):
#    pass

# TODO: jednak wszystko w jednym pliku, ta klasa parsuje plik logfile
# Parsuj()

# TODO: ta klasa bedzie zawierala wyswietlanie wynikow wedlug kryteriow
# Wyswietl()
