import sqlite3
import csv


# Scrip to convert CSV files to SQL database
def main():
    sqlite_file = 'bristol.db'
    conn = sqlite3.connect(sqlite_file)
    conn.text_factory = str

    cur = conn.cursor()

    # Create node table and insert data from nodes.csv
    cur.execute('''
        CREATE TABLE node (
            id INTEGER PRIMARY KEY,
            lat REAL,
            lon REAL,
            user TEXT,
            uid INTEGER,
            version TEXT,
            changeset INTEGER,
            timestamp TEXT
            );
            ''')

    conn.commit()

    with open('nodes.csv', 'rt') as f:
        dr = csv.DictReader(f)
        to_db = [(i['id'], i['lat'], i['lon'], i['user'].decode('utf-8'), i['uid'], i['version'], i['changeset'],
                  i['timestamp']) for i in dr]

    cur.executemany(
        'INSERT INTO node(id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
        to_db)

    conn.commit()

    # Create node_tags table and insert data from nodes_tags.csv
    cur.execute('''
        CREATE TABLE node_tags (
            id INTEGER REFERENCES node (id),
            key TEXT,
            value TEXT,
            type TEXT
            );
            ''')

    conn.commit()

    with open('nodes_tags.csv', 'rt') as f:
        dr = csv.DictReader(f)
        to_db = [(i['id'], i['key'], i['value'].decode('utf-8'), i['type']) for i in dr]

    cur.executemany('INSERT INTO node_tags(id, key, value, type) VALUES (?, ?, ?, ?);', to_db)

    conn.commit()

    # Create way table and insert data from ways.csv
    cur.execute('''
        CREATE TABLE way (
            id INTEGER PRIMARY KEY,
            user TEXT,
            uid INTEGER,
            version TEXT,
            changeset INTEGER,
            timestamp TEXT
            );
            ''')

    conn.commit()

    with open('ways.csv', 'rt') as f:
        dr = csv.DictReader(f)
        to_db = [(i['id'], i['user'].decode('utf-8'), i['uid'], i['version'], i['changeset'], i['timestamp']) for i in
                 dr]

    cur.executemany('INSERT INTO way(id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);', to_db)

    conn.commit()

    # Create way_nodes table and insert data from ways_nodes.csv
    cur.execute('''
        CREATE TABLE way_nodes (
            id INTEGER REFERENCES way (id),
            node_id INTEGER,
            position INTEGER
            );
            ''')

    conn.commit()

    with open('ways_nodes.csv', 'rt') as f:
        dr = csv.DictReader(f)
        to_db = [(i['id'], i['node_id'], i['position']) for i in dr]

    cur.executemany('INSERT INTO way_nodes(id, node_id, position) VALUES (?, ?, ?);', to_db)

    conn.commit()

    # Create way_tags table and insert data from ways_tags.csv
    cur.execute('''
        CREATE TABLE way_tags (
            id INTEGER REFERENCES way (id),
            key TEXT,
            value TEXT,
            type TEXT
            );
            ''')

    conn.commit()

    with open('ways_tags.csv', 'rt') as f:
        dr = csv.DictReader(f)
        to_db = [(i['id'].decode('utf-8'), i['key'], i['value'].decode('utf-8'), i['type']) for i in dr]

    cur.executemany('INSERT INTO way_tags(id, key, value, type) VALUES (?, ?, ?, ?);', to_db)

    conn.commit()

    conn.close()


if __name__ == '__main__':
    main()
