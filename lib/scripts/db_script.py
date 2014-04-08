#! /usr/bin/env python
import getpass
import MySQLdb
import os
from lib.scripts.base_script import BaseScript

__author__ = 'andresantos'

class DBScript(BaseScript):
    def _build_parser(self, parser):
        super(DBScript, self)._build_parser(parser)
        parser.add_option('-H', '--host', dest='host',
                          help='MySQL server host address',
                          default = '127.0.0.1')
        parser.add_option('-P', '--port', dest='port',
                          help='MySQL server port',
                          default = '3306')
        parser.add_option('-u', '--user', dest='user',
                          help='MySQL server username',
                          default=getpass.getuser())
        parser.add_option('-p', '--passwd', dest='passwd',
                          help='MySQL server password')
        parser.add_option('-d', '--dbname', dest='dbname',
                          help='MySQL server database')
        return parser

    def _build(self):
        super(DBScript, self)._build()
        host = self._get_option('host')
        port = int(self._get_option('port'))
        user = self._get_option('user')
        pswd = self._get_option('passwd')
        db = self._get_option('dbname')

        if pswd is None or db is None:
            self._parser().error("You must inform your mysql password and "
                                 "database")

        self.__db = MySQLdb.connect(host = host, port = port, user = user,
                                    passwd = pswd, db = db)
        self.__cursor = self.__db.cursor()

    def _query(self, query, *args):
        self.__cursor.execute(query, tuple(self.__flatten(args)))
        return self.__cursor.fetchall()

    def __flatten(self, arg):
        set = list()
        for i in arg:
            if isinstance(i, list) or isinstance(i, tuple):
                set += self.__flatten(i)
            else:
                set.append(i)
        return  set

    def run(self):
        try:
            self._run()
            self._report()
        finally:
            self.__db.close()