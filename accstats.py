__author__ = 'Doman'

'''
'PARSUJ' ma za zadanie parsować JEDEN plik logfile_console_XXXX.log,
dane z niego wyciągnięte:
data, nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
dane te mają zostać zapisane w bazie danych SQLite3

'WYSWIETL' ma pozwolić na otworzenie bazy danych
i dowolne parsowanie danych po tych parametrach:
- gracz -> w jakich dniach grał, zawężenie wyników
- dzień/ilość graczy
- dzień/długość misji
- ...
oraz wyświetlanie wyników na wykresach

'BAZACLEANUP' - do oczyszczania bazy danych z takich samych wpisów,
możliwe też, że będzie sortować baze według daty rozegrania misji
'''

from pandas import *  # do gryzienia danych
from bdateutil import *  # dokładne przeliczenia na datach, lepsze od zwykłego dateutil
import os, glob, time  # , datetime, re
import sqlalchemy
# import numpy as np  # do gryzienia danych, panda tez to importuje
# import matplotlib.pyplot as plt  # do wykresów, jeszcze brak użycia


class Parsuj:
    def __init__(self):
        directory = 'C:/Users/Jarek/PycharmProjects/ACC Stats'
        self.changedir(directory)
        file = self.findfile()
        self.parserlogfile(file)

    # zmienia folder
    # może ścieżka jako argument? /kiedyś
    def changedir(self, directory):
        os.chdir(directory)
        print(os.getcwd())

    # szuka zgodnego pliku
    # zazwyczaj plik ma datę o jeden dzień w przód!!
    def findfile(self):
        log = glob.glob('logfile_console*.log')
        if len(log) == 0:
            raise FileNotFoundError('BRAK PLIKU!')
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

    def zapiszdosql(self, data):
        engine = sqlalchemy.create_engine('sqlite:///foo.db')
        data.to_sql('data', engine, if_exists='append')

    # parser danych z logfile
    def parserlogfile(self, file):
        # data, nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
        plik = open(file[1], "r")
        lista_graczy = []
        dlugosc_misji = 0
        mapa = ''
        data = file[0]
        nazwa_misji = ''

        for line in plik:

            if 'Mission read' in line:
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
                endtime = line.split(' ')[0]
                if endtime == '':
                    endtime = line.split(' ')[1]
                endtime = time.strptime(endtime, '%H:%M:%S')
                if dlugosc_misji > 0:
                    if (endtime.tm_hour + (dlugosc_misji / 3600) >= 24) or (endtime.tm_hour < 20):
                        data = data + relativedelta(days=-1)
                        data = time.strftime('%Y-%m-%d', data.timetuple())

        ilosc = len(lista_graczy)
        lista_graczy = ', '.join(lista_graczy)
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
        self.zapiszdosql(dane)


class BazaCleanup(object):
    pass


class Wyswietl(object):
    pass


# jednak wszystko w jednym pliku, ta klasa parsuje plik logfile
Parsuj()

# ta klasa bedzie zawierala wyswietlanie wynikow wedlug kryteriow
Wyswietl()

# cleanup bazy danych
BazaCleanup()