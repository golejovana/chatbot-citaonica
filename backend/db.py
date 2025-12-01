import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="citaonica"
)

cursor = db.cursor(dictionary=True)
