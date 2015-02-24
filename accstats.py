__author__ = 'Doman'

'''
'PARSUJ' parsuje jeden albo wiele plików logfile_console_XXXX.log,
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

'BAZACLEANUP' - tworzy główną bazę danych, wyczyszczoną z powtarzających się wpisów
na podstawie czasu trwania misji, sortuje po datach rozegrania misji.
'''

from pandas import *  # do gryzienia danych
from bdateutil import *  # dokładne przeliczenia na datach, lepsze od zwykłego dateutil
import os, glob, time  # , datetime, re
import sqlalchemy
# import numpy as np  # do gryzienia danych, panda tez to importuje
# import matplotlib.pyplot as plt  # do wykresów, jeszcze brak użycia


class Parsuj:
    def __init__(self):
        directory = 'C:/Users/Jarek/PycharmProjects/ACC Stats/LOGS'
        self.changedir(directory)
        file = self.findfile()
        for x in file:
            self.parserlogfile(x)

    # zmienia folder
    # może ścieżka jako argument? /kiedyś
    def changedir(self, directory):
        os.chdir(directory)

    # szuka zgodnego pliku
    # zazwyczaj plik ma datę o jeden dzień w przód!!
    def findfile(self):
        log = glob.glob('logfile_console*.log')
        if len(log) == 0:
            raise FileNotFoundError('BRAK PLIKU!')
        return log

    # kasuje powtarzające się nazwy
    def uniq(self, wejscie):
        unikalne = []
        for x in wejscie:
            if x not in wejscie:
                unikalne.append(x)
        unikalne.sort()
        return unikalne

    def zapiszdosql(self, data):
        engine = sqlalchemy.create_engine('sqlite:///acc.db')
        data.to_sql('stats', engine, if_exists='append')

    def dodataframe(self, data, nazwa_misji, mapa, dlugosc_misji, ilosc, lista_graczy):
        ilosc = len(lista_graczy)
        lista_graczy.sort()
        lista_graczy = ', '.join(lista_graczy)
        global d0
        d0 = {'data': data,
              'nazwa_misji': nazwa_misji,
              'mapa': mapa,
              'dlugosc_misji': dlugosc_misji,
              'ilosc_graczy': ilosc,
              'lista_graczy': [lista_graczy]}
        dane = DataFrame(d0, columns=['data',
                                      'nazwa_misji',
                                      'mapa',
                                      'dlugosc_misji',
                                      'ilosc_graczy',
                                      'lista_graczy'])
        if (ilosc > 4) and (dlugosc_misji > 300):
            self.zapiszdosql(dane)

    # parser danych z logfile
    def parserlogfile(self, file):
        # data, nazwa_misji, mapa, długość_misji, ilość_graczy, lista_graczy
        t = time.gmtime(os.path.getmtime(file))
        t2 = time.strftime('%H', t)
        t = time.strftime('%Y-%m-%d', t)
        odjete = False
        if t2 == '06':
            t = t + relativedelta(days=-1)
            t = time.strftime('%Y-%m-%d', t.timetuple())
            odjete = True
        plik = open(file, "r", encoding='utf-8')
        lista_graczy = []
        dlugosc_misji = 0
        mapa = ''
        data = t
        nazwa_misji = ''
        ilosc = 0

        for line in plik:

            if 'Mission read' in line:
                if not line.startswith(('20', '21', '22', '23')):
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
                if (endtime.tm_hour < 6) and not odjete:
                    data = data + relativedelta(days=-1)
                    data = time.strftime('%Y-%m-%d', data.timetuple())

            if 'class Session' in line:
                self.dodataframe(data, nazwa_misji, mapa, dlugosc_misji, ilosc, lista_graczy)
                lista_graczy = []
                dlugosc_misji = 0
                mapa = ''
                data = t
                nazwa_misji = ''
                ilosc = 0

        self.dodataframe(data, nazwa_misji, mapa, dlugosc_misji, ilosc, lista_graczy)


# TODO: sortowanie bazy po datach
def bazacleanup():
    try:
        engine = sqlalchemy.create_engine('sqlite:///acc.db')
        data = read_sql_table('stats', engine)
        data.sort(columns='data', inplace=True)
        del data['index']
        data.drop_duplicates(subset='dlugosc_misji', inplace=True)
        data.to_sql('stats', engine, if_exists='replace')
    except Exception as e:
        print('blad w bazacleanup...  ', e)


# tworzy tabelę pokazującą, kiedy danych gracz był na misji
def wyswietl(name):
    engine = sqlalchemy.create_engine('sqlite:///acc.db')
    data = read_sql_table('stats', engine)
    name = name.lower()
    data = data[data['lista_graczy'].str.lower().str.contains(name)]
    data.to_sql('statswynik', engine, if_exists='replace')


# jednak wszystko w jednym pliku, ta klasa parsuje plik logfile
Parsuj()

# cleanup bazy danych
bazacleanup()

# ta klasa bedzie zawierala wyswietlanie wynikow wedlug kryteriow
# jako parametr należy podać nick gracza
wyswietl('tomeek')

print('GOTOWE')