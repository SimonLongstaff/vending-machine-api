import sqlite3


def bootstrap_database():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS vending_machines
                        (id uuid primary key,
                         name text,
                         lat real,
                         lng real,
                         created_at text,
                         updated_at text)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS products
                            (id uuid primary key,
                            name text,
                            description text,
                            price real,
                            size number,
                            temperature text
                            )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS vending_item_link
                        (id uuid primary key,
                        vending_machine_id uuid references vending_machines(id),
                                                  product_id uuid references products(id)
                                                  )''')
    conn.commit()
    conn.close()
