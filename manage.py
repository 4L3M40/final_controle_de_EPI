#!/usr/bin/env python
import os, sys
import pymysql

pymysql.install_as_MySQLdb()
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'epi_mvp.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
