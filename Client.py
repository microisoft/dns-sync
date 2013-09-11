#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'microisoft@gmail.com'

import socket, sys, base64, crypt, os, glob, logging, subprocess, filecmp

#--------------------------Настройки------------------------------------

#conn settings
conn_server = 'localhost'       #Мастер сервер.
conn_server_port = 10000        #Порт сервера.
conn_server_password = 'abc'    #Пароль для сервера.

#bind zone settings
master = '11.11.11.1'        #ip Мастер сервера
#bind_dir = '/etc/bind/'        #Директория c конфигами bind9
#zone_dir = '/etc/bind/slave/'  #Директория файлов зон
#zone_file = 'named.conf.zones' #Файл конфигурации для зон
#
bind_dir = ''        #Директория c конфигами bind9
zone_dir = 'slave'  #Директория файлов зон
zone_file = 'named.conf.zones' #Файл конфигурации для зон

#log
logfile = 'myapp.log'
log_level = 'war'

#----------------------------Настройки-----------------------------------

logger = logging.getLogger('dns-sync-client')
f_logfile = logging.FileHandler(logfile)
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
f_logfile.setFormatter(formatter)
logger.addHandler(f_logfile)

if log_level == 'war':
    logger.setLevel(logging.WARNING)
elif log_level == 'info':
    logger.setLevel(logging.INFO)
elif log_level == 'debug':
    logger.setLevel(logging.DEBUG)

def file_del():

    f_list = glob.glob(zone_dir+"/*.db")
    if f_list:
        for f in f_list:
            os.remove(f)
            logger.info('rm file %s', f)
        return True
    else:
        return False


def bind_restart():
    test = ['service','bind9','restart']
    r_bind = subprocess.call(test)

    if r_bind == 0:
        logger.info('Bind9 перезагружен.')
        return True
    else:
        logger.warn('Bind9 неудалось перезагрузить!')
        return False


def zone_add(data):

    data = base64.b64decode(data)
    d_lst = str.split(data)
    z_file = bind_dir+zone_file
    f = open(z_file, "w")

    for i in d_lst:

        zone = "zone \"%s\" {\n" \
               "type slave;\n" \
               "file \"/etc/bind/slave/%s.db\";\n" \
               "masters { %s; };\n" \
               "allow-query { localhost; 0.0.0.0/0; };\n" \
               "allow-notify { %s; };\n" \
               "allow-transfer { %s; };\n};\n" % (i, i, master, master, master)
        line = f.writelines(zone)

    if line:
        logger.error('Конфиг зон не создан!')
    else:
        logger.info('Конфиг зон создан.')

    f.close()

    if file_del():
        logger.info('Папка '+zone_dir+' очищена. ')
    else:
        logger.error(zone_dir+' Не найдено файлов для удаления!')

    bind_restart()


def get_zone():

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = s.connect_ex((conn_server, conn_server_port))
    s.close()
    if result == 0:

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect the socket to the port where the server is listening
        server_address = (conn_server, conn_server_port)
        logger.info('Соединяюсь с %s port %s' % server_address)
        sock.connect(server_address)

        try:

            # Send data

            message = crypt.crypt(conn_server_password,'MTMzMjQxMjQ')
            logger.info('Отправляем пароль.')

            sock.sendall(message)
            data = sock.recv(9999)

            if data == 'Not accepted command. \n Exit':

                logger.error('Некорректный пароль!')

            else:

                logger.info('Получаем данные..')
                return data

        finally:

            logger.info('Закрываем сокет.')
            sock.close()
    else:

        logger.error('Порт сервера закрыт или сервер не ртвечает!')
        return False

#Едим список доменов с master сервера
data = get_zone()
if data:
    #Расшифровываем, создаем конфиг
    #чистим директорию slave
    #перезагружаем сервис bind
    zone_add(data)
#todo Добавить проверку на изменение!
