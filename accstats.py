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
from bokeh.plotting import figure, output_file, show, VBox
# import numpy as np  # do gryzienia danych, panda tez to importuje
# import matplotlib.pyplot as plt  # do wykresów, jeszcze brak użycia


engine = sqlalchemy.create_engine('sqlite:///acc.db')
set_option('display.width', 3000)
set_option('display.max_colwidth', 1000)

class Parsuj:
    def __init__(self):
        directory = 'F:/LOGS'
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
        if int(t2) <= 7:
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


def print_full(x):
    set_option('display.max_rows', len(x))
    print(x)
    reset_option('display.max_rows')

def bazacleanup():
    try:
        data = read_sql_table('stats', engine)
        data.drop_duplicates(subset='dlugosc_misji', inplace=True)
        data.sort(columns=['data', 'ilosc_graczy'], inplace=True)
        del data['index']
        data.to_sql('stats', engine, if_exists='replace')
    except Exception as e:
        print('blad w bazacleanup...  ', e)


# tworzy tabelę pokazującą, kiedy danych gracz był na misji
def wyswietl(name):
    for x in name:
        data = read_sql_table('stats', engine)
        data.drop_duplicates(subset='data', take_last=True, inplace=True)
        x = x.lower()
        data = data[data['lista_graczy'].str.lower().str.contains(x)]
    del data['index']
    print_full(data)
    print(data.to_html(index=False))
        # gracze = {'gracz': name,
        #           'ilosc': len(data.index)}
        # df_gracze = DataFrame(gracze, columns=['gracz',
        #                                        'ilosc'])
        # print('[m=', name, ']', ' bral udzial w ', len(data.index), ' misjach', sep='')
        # # data.to_sql('statswynik', engine, if_exists='replace')


def wyswietl_wszystkich():
    data = read_sql_table('stats', engine)
    data.drop_duplicates(subset='data', take_last=True, inplace=True)
    names = []
    for x in data.index:
        names += data.loc[x]['lista_graczy'].split(", ")
    names = unique(names)
    df_gracze = DataFrame(columns=['gracz', 'ilosc'])
    for name in names:
        gracz = data[data['lista_graczy'].str.contains(name)]
        gracz = {'gracz': name,
                 'ilosc': len(gracz.index)}
        df_gracze = df_gracze.append(gracz, ignore_index=True)
    df_gracze = df_gracze.sort(columns=['ilosc'], ascending=False)
    for x in df_gracze.index:
        print('[m=', df_gracze.loc[x][0], ']', ' wzial udzial w ', int(df_gracze.loc[x][1]), ' rozgrywkach.', sep='')

    print(df_gracze['gracz'])

    # gracze.sort(columns=['data', 'ilosc_graczy'], inplace=True)
        # print('[m=', name, ']', ' bral udzial w ', len(gracze.index), ' misjach', sep='')


        # data = data[data['lista_graczy'].str.lower().str.contains(name)]
        # data.drop_duplicates(subset='data', take_last=True, inplace=True)
        # print(name, ' bral udzial w tych misjach: ', len(data.index))
        # data.to_sql('statswynik', engine, if_exists='replace')


def graf():
    data = read_sql_table('stats', engine, parse_dates={'data', '%Y-%m-%d'}, columns=['data', 'ilosc_graczy'])
    data.drop_duplicates(subset='data', take_last=True, inplace=True)
    # data.plot(kind='bar')
    # print(data)
    try:
        p1 = figure(title="Stocks",
                    x_axis_label="Data",
                    y_axis_label="Graczy")
        p1.line(
            data['data'],  # x coordinates
            data['ilosc_graczy'],  # y coordinates
            color='#A6CEE3',  # set a color for the line
            legend='AAPL',  # attach a legend label
        )
        p1.title = 'Ilosc graczy na rozgrywkach ACC'
        p1.grid.grid_line_alpha = 0.3

        show(VBox(p1))
    except Exception as e:
        print('bokeh: ', e)

# jednak wszystko w jednym pliku, ta klasa parsuje plik logfile
Parsuj()

# cleanup bazy danych
bazacleanup()

# wyswietla wszystkich graczy z bazy oraz ilosc rozgrywek w ktorych wzieli udzial
wyswietl_wszystkich()

# ta klasa bedzie zawierala wyswietlanie wynikow wedlug kryteriow
# jako parametr należy podać nick gracza
wyswietl(['maras'])


# tworzenie grafów
# graf()

print('GOTOWE')