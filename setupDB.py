import sqlite3
from sqlite3 import Error
 
def execute_query(conn, sql_query,is_insert):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_query)
        if is_insert:
            conn.commit()
    except Error as e:
        print(e)
 
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        return conn
    except Error as e:
        print(e)
    #finally:
        #conn.close()
    
    return None
 
def main():
    database = "pokedex.db"
    sql_create_pokemones_table = """ CREATE TABLE IF NOT EXISTS pokemones (
                                        id integer PRIMARY KEY,
                                        nombre text NOT NULL
                                    ); """
    sql_create_users_table = """ CREATE TABLE IF NOT EXISTS usuarios (
                                        id integer PRIMARY KEY,
                                        nombre text NOT NULL
                                    ); """
    sql_create_pokemones_capturados_table = """ CREATE TABLE IF NOT EXISTS pokemones_capturados (
                                        id_usuario integer NOT NULL,
                                        id_pokemon integer NOT NULL,
                                        cantidad integer NOT NULL,
                                        FOREIGN KEY (id_usuario) REFERENCES usuarios (id),
                                        FOREIGN KEY (id_pokemon) REFERENCES pokemones (id)
                                    ); """
    sql_insert_pokemones = """ INSERT INTO pokemones (id,nombre) VALUES  
                                (0, 'Bidoof'),
                                (1, 'Magikarp'),
                                (2, 'Klefki'),
                                (3, 'Smeargle'),
                                (4, 'Shuckle'),
                                (5, 'Rattata'),
                                (6, 'Pidgey'),
                                (7, 'Weedle'),
                                (8, 'Ducklett'),
                                (9, 'Arceus'); """
    sql_insert_users = """ INSERT INTO usuarios (id,nombre) VALUES  
                                (0, 'ash ketchup'),
                                (1, 'nieves'),
                                (2, 'tonio'); """

    conn = create_connection(database)
    if conn is not None:
        execute_query(conn, sql_create_pokemones_table,False)
        execute_query(conn, sql_create_users_table,False)
        execute_query(conn, sql_create_pokemones_capturados_table,False)
        execute_query(conn, sql_insert_pokemones,True)
        execute_query(conn, sql_insert_users,True)
        conn.close()
        
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
