__author__ = 'Dom4n'

import os
import ftputil
import glob
import sensitive as s
import time
import threading


def upload():
    directory = 'F:/LOGS/html/'
    os.chdir(directory)
    nieudane = []
    pool_sema = threading.BoundedSemaphore(4)

    pliki = glob.glob('*.html')
    if len(pliki) == 0:
        raise FileNotFoundError('BRAK PLIKOW!!!')

    tim = time.time()
    print('FTP -> START')

    with ftputil.FTPHost(s.ftp_host, s.ftp_login, s.ftp_pass) as ftp_host:
        for x in pliki:
            try:
                isok = ftp_host.upload_if_newer(x, ftp_host.curdir+'/all/'+x)
                if isok:
                    print('upload pliku: '+x+' zakonczony powodzeniem')
                else:
                    print('upload pliku: '+x+' NIEUDANY!!!!')
                    nieudane.append(x)
            except Exception as e:
                print('nieudane przeslanie pliku: '+x)

    if len(nieudane) > 0:
        print('Nieprzeslane pliki:\n'+str(nieudane))
    else:
        print('Wszystkie pliki przeslane!')

    tim = time.time() - tim
    print('Czas: '+str(tim))
    print('FTP -> KONIEC')