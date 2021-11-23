import psycopg2
import json


class db_helper():
    def __init__(self):
        self.__conn = psycopg2.connect(user="postgres",
                                       password="postgres",
                                       host="database-1.cbftrecqzbgd.eu-west-2.rds.amazonaws.com",
                                       port="5432",
                                       dbname="candidates")
        self.__conn.autocommit = True
        self.__cursor = self.__conn.cursor()

    def drop_table(self, table_name):
        self.__cursor.execute("DROP TABLE %s CASCADE;" % (table_name))

    def __db_create_table__(self, table_name: str, columns: dict):
        try:
            formatted_columns = "".join(["%s %s, " % (key, value) for key, value in columns.items()])[:-2]
            self.__cursor.execute("CREATE TABLE %s (%s);" % (table_name, formatted_columns))
        except psycopg2.errors.DuplicateTable:
            self.drop_table(table_name)
            self.__db_create_table__(table_name, columns)

    def create_vacancy_table(self, table_name):
        with open("src/parsing/vacancy_db_columns.json", "r") as file:
            column_data = json.load(file)
        self.__db_create_table__(table_name, column_data)

    def create_candidate_table(self, table_name):
        with open("src/parsing/vacancy_db_columns.json", "r") as file:
            column_data = json.load(file)
        self.__db_create_table__(table_name, column_data)

    def __db_insert_vacancy__(self, table_name: str, formatted_vacancy: list):
        self.__cursor.execute('INSERT INTO %s (%s) values %s;',
                              (table_name, formatted_vacancy[0], formatted_vacancy[1]))

    def insert_vacancy(self, table_name: str, vacancy: dict):
        formatted_vacancy = [", ".join(vacancy.keys())[2:],
                             "(%s)" % " ,".join(list(map(lambda x: str(x), vacancy.values())))]
        self.__db_insert_vacancy__(table_name, formatted_vacancy)

    def insert_vacancies(self, table_name: str, vacancies: list):
        keys = ", ".join(vacancies[0].keys())
        values = "".join(
            ["(%s), " % ", ".join(list(map(lambda x: str(x), vacancy.values()))) for vacancy in vacancies])[:-2]
        print(values)
        formatted_vacancies = [keys, values]
        self.__db_insert_vacancy__(table_name, formatted_vacancies)

    def insert_candidate(self, ):
        column_data = {"": ""}

    def select_all(self, table_name: str):
        self.__cursor.execute('SELECT * FROM {};'.format(table_name))
        return self.__cursor.fetchall()

    def select_by_query_and_region(self, table_name: str, query: str, reqion: int):
        self.__cursor.execute("SELECT * FROM {0} WHERE query='{1}' and region={2};".format(table_name, query, reqion))
        return self.__cursor.fetchall()

    def get_column_names(self, table_name: str):
        self.__cursor.execute("Select * FROM {} LIMIT 0".format(table_name))
        return [desc[0] for desc in self.__cursor.description]


if __name__ == "__main__":
    db = db_helper()
    table_name = "testing"
    try:
        db.create_vacancy_table(table_name)
    except psycopg2.errors.DuplicateTable:
        db.drop_table(table_name)
