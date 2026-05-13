from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    select,
    insert,
    Integer,
    String,
    update,
    delete
)

from sqlalchemy.sql import sqltypes

def init_database(location):
    db = Database(location)
    db.create_table(
        "users",
        {
            "id" : Integer,
            "username" : String,
            "password_hash" : String
        }
    )
    db.init_database()
    return db

class Database:

    def __init__(self, location="app.db"):

        self.location = location

        self.engine = create_engine(
            f"sqlite:///{self.location}",
            connect_args = {"check_same_thread": False}
        )

        self.metadata = MetaData()

    def init_database(self):
        self.metadata.create_all(self.engine)

    def create_table(self, table_name, columns):
        """
        columns format:

        {
            "id": Integer,
            "username": String,
            "age": Integer
        }
        """
        sql_columns = []

        for col_name, col_type in columns.items():

            # primary key convenience
            if col_name == "id":
                sql_columns.append(
                    Column(
                        col_name,
                        col_type,
                        primary_key=True
                    )
                )

            else:
                sql_columns.append(
                    Column(col_name, col_type)
                )

        table = Table(
            table_name,
            self.metadata,
            *sql_columns
        )

        self.metadata.create_all(self.engine)

        return table

    def get_table(self, table_name):

        return Table(
            table_name,
            self.metadata,
            autoload_with=self.engine
        )

    def get_entry(
        self,
        table_name,
        column_name,
        value
    ):

        table = self.get_table(table_name)

        query = select(table).where(
            table.c[column_name] == value
        )

        with self.engine.connect() as conn:

            result = conn.execute(query).mappings().first()

            return result

    def does_entry_exist(
        self,
        table_name,
        column_name,
        value
    ):

        entry = self.get_entry(
            table_name,
            column_name,
            value
        )

        return entry is not None

    def create_entry(
        self,
        table_name,
        data
    ):
        """
        data format:

        {
            "username": "bob",
            "age": 32
        }
        """

        table = self.get_table(table_name)

        query = insert(table).values(**data)

        with self.engine.begin() as conn:
            result = conn.execute(query)
            return result.inserted_primary_key
    
    def update_entry(
        self,
        table_name,
        search_column,
        search_value,
        data
    ):
        """
        data format:

        {
            "username": "newname"
        }
        """

        table = self.get_table(table_name)

        query = (
            update(table)
            .where(table.c[search_column] == search_value)
            .values(**data)
        )

        with self.engine.begin() as conn:

            result = conn.execute(query)

            return result.rowcount
    
    def delete_entry(
        self,
        table_name,
        search_column,
        search_value
    ):

        table = self.get_table(table_name)

        query = delete(table).where(
            table.c[search_column] == search_value
        )

        with self.engine.begin() as conn:

            result = conn.execute(query)

            return result.rowcount
    
    def list_entries(
        self,
        table_name
    ):

        table = self.get_table(table_name)

        query = select(table)

        with self.engine.connect() as conn:

            result = conn.execute(query).mappings().all()

            return result
    
db = init_database("app.db")