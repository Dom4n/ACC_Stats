__author__ = 'Dom4n'

import os
import ftputil
import glob
import sensitive as s


def upload():
    directory = 'F:/LOGS/html/'
    os.chdir(directory)
    nieudane = []

    pliki = glob.glob('*.html')
    if len(pliki) == 0:
        raise FileNotFoundError('BRAK PLIKOW!!!')

    with ftputil.FTPHost(s.ftp_host, s.ftp_login, s.ftp_pass) as ftp_host:
        for x in pliki:
            isok = ftp_host.upload_if_newer(x, ftp_host.curdir+'/all/'+x)
            if isok:
                print('upload pliku: '+x+' zakonczony powodzeniem')
            else:
                print('upload pliku: '+x+' NIEUDANY!!!!')
                nieudane.append(x)

    if len(nieudane) == 0:
        print('Nieprzeslane pliki:\n'+nieudane)
    else:
        print('Wszystkie pliki przeslane!')
    print('FTP -> KONIEC')