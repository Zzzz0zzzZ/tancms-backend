import pymysql
from pymysql import cursors

"""
    sql = '''
        INSERT INTO `数据库名`.`数据表名` (需要插入的字段)
        VALUES (
            "使用%s占位，有多少个%s，传入的data_list就有多少个元素。数量要对应！"
        )
    '''
    
    例如：
    
    sql = '''
        INSERT INTO comments(job_id, platform, comment)
        VALUES (%s, %s, %s)
    '''
    
"""


class DBManager(object):

    def __init__(self, db: dict, sp_num: int = 2000):
        self.conn = pymysql.connect(
            host=db['host'],
            user=db['user'],
            password=db['password'],
            database=db['database'],
            port=db['port'],
            cursorclass=cursors.DictCursor
        )
        self.cur = self.conn.cursor()
        self.data_list = None
        self.sp_num = sp_num

    # 不用改
    def insert(self, sql, data_list):
        self.data_list = data_list
        sp_list = self.list_of_groups()
        for sp in sp_list:
            try:
                self.cur.executemany(sql, sp)
                self.conn.commit()
            except pymysql.Error as e:
                self.conn.rollback()
                raise e

    def finish(self, job_id: str):
        try:
            sql = '''
                UPDATE jobs SET status = status + 1 WHERE job_id = %s
            '''
            self.cur.execute(sql, (job_id, ))
            self.conn.commit()
        except pymysql.Error as e:
            self.conn.rollback()
            raise e

        self.cur.close()
        self.conn.close()

    # 不用改
    def list_of_groups(self):
        list_of_groups = zip(*(iter(self.data_list),) * self.sp_num)
        end_list = [list(i) for i in list_of_groups]
        count = len(self.data_list) % self.sp_num
        end_list.append(self.data_list[-count:]) if count != 0 else end_list
        return end_list
