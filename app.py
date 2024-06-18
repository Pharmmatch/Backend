from app import app
from fetch_data import fetch_kor_drugs, insert_data

if __name__ == '__main__':
    app.run(debug=True)