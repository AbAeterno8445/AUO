import pymysql


class DBConnection(object):
    def __init__(self, db_name, db_ip="127.0.0.1", db_user="root", db_pwd="alumno"):
        self.db_name = db_name
        self.db_ip = db_ip
        self.db_user = db_user
        self.db_pwd = db_pwd

    def run_query(self, query_string, query_args):
        db = pymysql.connect(host=self.db_ip,
                             user=self.db_user,
                             passwd=self.db_pwd,
                             db=self.db_name,
                             autocommit=True)
        try:
            cursor = db.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query_string, query_args)

            return cursor
        except Exception as e:
            print("Exception occurred while running query:{}".format(e))
        finally:
            db.close()
        return None