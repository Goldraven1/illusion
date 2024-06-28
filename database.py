import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, config):
        self.connection = psycopg2.connect(**config)
        self.cursor = self.connection.cursor()
    
    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            surname VARCHAR(50),
            name VARCHAR(50),
            patronymic VARCHAR(50),
            gender VARCHAR(10),
            age INT
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS muller_lyer_results (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users(id),
            illusion_index INT NOT NULL,
            absolute_error_mm FLOAT NOT NULL
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS vertical_horizontal_results (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users(id),
            illusion_index INT NOT NULL,
            absolute_error_mm FLOAT NOT NULL
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS poggendorff_results (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL REFERENCES users(id),
            illusion_index INT NOT NULL,
            absolute_error FLOAT NOT NULL
        );
        """)
        self.connection.commit()
    
    def insert_user(self, surname, name, patronymic, gender, age):
        self.cursor.execute(
            sql.SQL("INSERT INTO users (surname, name, patronymic, gender, age) VALUES (%s, %s, %s, %s, %s) RETURNING id"),
            [surname, name, patronymic, gender, age]
        )
        user_id = self.cursor.fetchone()[0]
        self.connection.commit()
        return user_id
    
    def insert_muller_lyer_result(self, user_id, illusion_index, absolute_error_mm):
        self.cursor.execute(
            sql.SQL("INSERT INTO muller_lyer_results (user_id, illusion_index, absolute_error_mm) VALUES (%s, %s, %s)"),
            [user_id, illusion_index, absolute_error_mm]
        )
        self.connection.commit()
    
    def insert_vertical_horizontal_result(self, user_id, illusion_index, absolute_error_mm):
        self.cursor.execute(
            sql.SQL("INSERT INTO vertical_horizontal_results (user_id, illusion_index, absolute_error_mm) VALUES (%s, %s, %s)"),
            [user_id, illusion_index, absolute_error_mm]
        )
        self.connection.commit()

    def insert_poggendorff_result(self, user_id, illusion_index, absolute_error):
        self.cursor.execute(
            sql.SQL("INSERT INTO poggendorff_results (user_id, illusion_index, absolute_error) VALUES (%s, %s, %s)"),
            [user_id, illusion_index, absolute_error]
        )
        self.connection.commit()

    def fetch_user_with_results(self, user_id):
        self.cursor.execute(
            sql.SQL("""
            SELECT u.surname, u.name, u.patronymic, u.gender, u.age,
                   ml.illusion_index AS ml_illusion_index, ml.absolute_error_mm AS ml_absolute_error_mm,
                   vh.illusion_index AS vh_illusion_index, vh.absolute_error_mm AS vh_absolute_error_mm,
                   pg.illusion_index AS pg_illusion_index, pg.absolute_error AS pg_absolute_error
            FROM users u
            LEFT JOIN muller_lyer_results ml ON u.id = ml.user_id
            LEFT JOIN vertical_horizontal_results vh ON u.id = vh.user_id
            LEFT JOIN poggendorff_results pg ON u.id = pg.user_id
            WHERE u.id = %s
            """),
            [user_id]
        )
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()
