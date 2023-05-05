# coding=UTF-8
import sqlite3
# sheet


def search_local_word(start):
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    sql = '''SELECT * from sheet WHERE start = "{}"'''.format(start)
    c.execute(sql)
    res = c.fetchone()
    conn.close()
    if res is not None:
        return res[-1]
    else:
        return None


def load_local_word(start,end):
    conn = sqlite3.connect('words.db')
    c = conn.cursor()
    sql = """INSERT INTO sheet(START,
         END)
         VALUES ("{}","{}")""".format(start,end)
    c.execute(sql)
    conn.commit()
    conn.close()

def search_local(start,end):
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()
    sql = '''SELECT * from sheet WHERE start = "{}" and end = "{}"'''.format(start,end)
    c.execute(sql)
    res = c.fetchone()
    conn.close()
    if res is not None:
        return res[-1]
    else:
        return None

def  load_local(start,end,number):
    conn = sqlite3.connect('keys.db')
    c = conn.cursor()
    sql = """INSERT INTO sheet(START,
         END, CORR)
         VALUES ("{}","{}",{})""".format(start,end,number)
    c.execute(sql)
    conn.commit()
    conn.close()

