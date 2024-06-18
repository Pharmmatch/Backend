db = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'port':3306,
    'database':'kordrugs',
}

class Config:
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False