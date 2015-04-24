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
import shutil
from bokeh.plotting import figure, output_file, show, VBox
import accftp
# import numpy as np  # do gryzienia danych, panda tez to importuje
# import matplotlib.pyplot as plt  # do wykresów, jeszcze brak użycia

set_option('display.width', 3000)
set_option('display.max_colwidth', 1000)

engine = sqlalchemy.create_engine('sqlite:///acc.db')

class Parsuj:
    def __init__(self):
        directory = 'F:/LOGS'
        # directory = 'F:/LOGS/STARE/20150302'
        self.changedir(directory)
        file = self.findfile()
        for x in file:
            self.parserlogfile(x)
        self.bazacleanup()

    # zmienia folder
    # może ścieżka jako argument? /kiedyś
    def changedir(self, directory):
        os.chdir(directory)

    # szuka zgodnego pliku
    # zazwyczaj plik ma datę o jeden dzień w przód!!
    def findfile(self):
        log = glob.glob('logfile_console*')
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

    def bazacleanup(self):
        try:
            data = read_sql_table('stats', engine)
            data.drop_duplicates(subset='dlugosc_misji', inplace=True)
            data.sort(columns=['data', 'ilosc_graczy'], inplace=True)
            del data['index']
            data.to_sql('stats', engine, if_exists='replace')
        except Exception as e:
            print('blad w bazacleanup...  ', e)

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
            # print("Dopisuje do bazy danych:\n",dane)
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


# tworzy tabele graczy
def wyswietl(name):
    data = read_sql_table('stats', engine)
    data.drop_duplicates(subset='data', take_last=True, inplace=True)
    del data['index']
    for x in name:
        z = x
        x = x.lower()
        gracz = data[data['lista_graczy'].str.lower().str.contains(x)]
        htmlf = '<head><meta charset="UTF-8"></head> \n'
        htmlf += '<font size="6">'+z+' wzial udzial w '+str(data.count()[1])+' rozgrywkach.\n\n<br><br></font>'
        htmlf += gracz.to_html(index=False)
        with open('html/'+x+'.html', mode='w', encoding='utf-8') as file:
            # print('tworze plik '+x+'.html')
            file.write(htmlf)

    htmlf = '<head><meta charset="UTF-8"></head> \n'
    htmlf += '<font size="4">Baza przeprowadzonych misji:<br><br></font>'
    htmlf += data.to_html(index=False)
    with open('html/_misje.html', mode='w', encoding='utf-8') as file:
        file.write(htmlf)


def lista_graczy():
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
    df_gracze = df_gracze.sort(columns=['gracz'], ascending=True)

    htmlf = '<head><meta charset="UTF-8"></head> \n'
    htmlf += '<font size="3">' \
             'Gracze posortowani alfabetycznie. <br>' \
             'Ilość rozgrywek liczona od wprowadzenia nowego systemu rang (27.03.2015)' \
             '<br><br></font>'
    htmlf += df_gracze.to_html(index=False)
    with open('html/_all.html', mode='w', encoding='utf-8') as file:
        file.write(htmlf)

    return df_gracze['gracz']


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


def czysc_katalog():
    shutil.rmtree('html', ignore_errors=True)
    os.mkdir('html')


def ftpupload(ok):
    if ok:
        accftp.upload()


# czysci katalog html
czysc_katalog()

# Parsuje logfile i zapisuje do sql
Parsuj()

# tworzy liste graczy z iloscia rozegranych misji
# zwraca liste nickow graczy
wszyscy = lista_graczy()

# wyswietlanie wynikow wedlug kryteriow
# jako parametr należy podać nick gracza (lub wszystkie jako listę)
wyswietl(wszyscy)


# tworzenie grafów
# graf()


# upload na dhosting
ftpupload(True)

print('GOTOWE')