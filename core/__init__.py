import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
MySQLdb.__version__ = '2.2.1'
MySQLdb.version_info = (2, 2, 1, 'final', 0)

# Patch to bypass MariaDB version check for Django 4.2+ on XAMPP
try:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.backends.mysql.features import DatabaseFeatures
    BaseDatabaseWrapper.check_database_version_supported = lambda self: None
    DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
    DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)
except ImportError:
    pass

