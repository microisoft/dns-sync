#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'microisoft@gmail.com'

import socket, re, base64, crypt, logging

#----------------------------Настройки-----------------------------------

server_address = '11.11.11.1'             #Адрес сервера для входящих соединений
server_port = 10000             #Порт
conn_password = 'abc'           #Пароль для входящих соединений
named_file = '/etc/named.conf'  #Файл настроек Bind со списком зон (полный путь !!)

#log
logfile = 'myapp.log'
log_level = 'war'

#----------------------------Настройки-----------------------------------


def s_server():
    logger = logging.getLogger('dns-sync-server')
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



    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    f = open(named_file, 'r')
    conf = f.read()

    zones = re.findall('zone "([a-zA-Z0-9.-]+.*?)', conf)

    # Bind the socket to the port
    server_addr = (server_address, server_port)
    logger.info('starting up on %s port %s', server_address, server_port)

    sock.bind(server_addr)

    # Listen for incoming connections
    sock.listen(5)

    while True:
        # Wait for a connection
        logger.info('Ждем новых соединений.')
        connection, client_address = sock.accept()

        try:
            print >> logger.info('connection from %s', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(9999)
                logger.info('Получаю данные "%s"', data)


                c_pass = crypt.crypt(conn_password, 'MTMzMjQxMjQ')
                if data == c_pass:
                    logger.info('Передаю данные %s', client_address)

                    zone = ''
                    for i in zones:
                        zone = zone + i + '\n'
                    zone = base64.b64encode(zone)
                    connection.sendall(zone)
                    break
                elif data:
                    mess = 'Not accepted command. \n Exit'
                    logger.error('Неправильная комманда %s', client_address)
                    connection.sendall(mess)
                break

        finally:
            # Clean up the connection
            connection.close()

    return True
s_server()
