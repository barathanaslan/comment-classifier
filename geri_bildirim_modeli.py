from flask import Flask, jsonify, request, json, Response
import mariadb
from datetime import datetime, timedelta
import bert_app
import os
from jsonschema import validate
import logging
from rest_framework import status

from schemas import tarih_schema, comment_schema, creating_comment_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# Function to create a connection to the MariaDB database
def create_connection():
    try:
        # Connect to the database using environment variables for credentials
        conn = mariadb.connect(
            user=os.environ.get("DB_USER", "NOT SET"),
            password=os.environ.get("DB_PASSWORD", "NOT SET"),
            host=os.environ.get("DB_HOST", "NOT SET"),
            port=int(os.environ.get("DB_PORT", "-1")),
            database=os.environ.get("DB_NAME", "NOT SET")
        )
        return conn
    except mariadb.Error as e:
        # Log a warning message and return a response if connection fails
        logging.warning(f"Error connecting to MariaDB Platform: {e}")
        return Response(json.dumps({
            "response_code": 500,
            "response_message": f"Error connecting to server! {e}",
        }),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Initialize the Flask application
app = Flask(__name__)

# Establish a database connection
conn = create_connection()

# Sample comments list
comments = [
    {
        'id': '1',
        'comment': "Uygulamada teknik sorun var",
        "label": "Teknik"
    },
    {
        'id': '2',
        'comment': "Rehberlik desteğe ihtiyacım var",
        "label": "Rehberlik"
    }
]

# Route for the homepage
@app.route('/')
def home():
    return "homepage"

# Route to create a new comment
@app.route('/comment', methods=['POST'])
def create_comment():
    try:
        # Get and validate the JSON request data
        request_data = request.get_json()
        validate(request_data, comment_schema)
    except:
        # Log a warning message and return a response if validation fails
        logging.warning("User did not enter a valid input for 'JSON type comment'.")
        return Response(json.dumps({
            "response_code": 400,
            "response_message": "Method not allowed. Wrong request type.",
        }),
            status=status.HTTP_400_BAD_REQUEST
        )
    # Predict the label for the comment using the bert_app
    label = bert_app.predict(request_data["comment"])["label"].to_string()
    # Create a new comment with an incremented ID
    new_comment = {
        'id': str(len(comments) + 1),
        'items': request_data["comment"],
        "label": label[5:]
    }
    # Append the new comment to the comments list
    comments.append(new_comment)
    return jsonify(new_comment)

# Route to label comments by date
@app.route('/tarih', methods=['GET'])
def label_comment_by_date(conn=conn):
    try:
        # Get and validate the JSON request data
        request_data = request.get_json()
        validate(request_data, tarih_schema)
    except:
        # Log a warning message and return a response if validation fails
        logging.warning("User did not enter a valid input for 'JSON type date'.")
        return Response(json.dumps({
            "response_code": 400,
            "response_message": "Method not allowed. Wrong request type.  Required key: tarih - Pattern: 2019-10-01",
        }),
            status=status.HTTP_400_BAD_REQUEST
        )
    # Create a cursor to interact with the database
    cursor = conn.cursor()
    get_tarih = request_data["tarih"]
    try:
        # Execute the query to fetch records by date
        cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?", (get_tarih,))
    except:
        # Reconnect and retry the query if the connection is lost
        logging.info("Connection lost. Reconnecting to database.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?", (get_tarih,))
    list = []
    # Process the fetched records
    for id, sorun, tarih in cursor:
        aciklama = bert_app.predict(sorun).to_string().split(" ")[-1]
        tarih = tarih.strftime("%Y-%m-%d %H:%M:%S")
        list.append({"id": id, "sorun": sorun, "label": aciklama, "tarih": tarih})
    cursor.close()
    return json.dumps(list)

# Route to label comments by a range of days
@app.route('/days/<int:number_of_days>', methods=['GET'])
def label_comment_by_today(number_of_days, conn=conn):
    today = datetime.now()
    cursor = conn.cursor()
    comment_list = []
    # Iterate over the range of days
    for day in range(number_of_days):
        n_days_ago = today - timedelta(days=day)
        try:
            # Execute the query to fetch records by date
            cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?",
                       (str(n_days_ago).split(" ")[0],))
        except:
            # Reconnect and retry the query if the connection is lost
            logging.info("Connection lost. Reconnecting to database.")
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?",
                           (str(n_days_ago).split(" ")[0],))
        # Process the fetched records
        for id, sorun, tarih in cursor:
            tarih = tarih.strftime("%Y-%m-%d %H:%M:%S")
            aciklama = bert_app.predict(sorun).to_string().split(" ")[-1]
            comment_list.append({
                "id": id,
                "tarih": tarih,
                "label": aciklama,
                "sorun": sorun
            })
    cursor.close()
    return json.dumps(comment_list)

# Route to get a specific comment by ID
@app.route('/comment/<int:id>', methods=['GET'])
def get_comment(id, conn=conn):
    cursor = conn.cursor()
    try:
        # Execute the query to fetch the comment by ID
        cursor.execute(f"SELECT id,sorun,tarih FROM sorun_bildir WHERE id={id}")
    except:
        # Reconnect and retry the query if the connection is lost
        logging.info("Connection lost. Reconnecting to database.")
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id,sorun,tarih FROM sorun_bildir WHERE id={id}")
    # Process the fetched record
    for id, sorun, tarih in cursor:
        tarih = tarih.strftime("%Y-%m-%d %H:%M:%S")
        aciklama = bert_app.predict(sorun).to_string().split(" ")[-1]
        return jsonify({"id": id, "sorun": sorun, "label": aciklama, "tarih": tarih})
    return jsonify({'message': 'comment not found'})

# Function to create a comment using JSON data
def create_comment_by_json(conn=conn):
    try:
        # Get and validate the JSON request data
        request_data = request.get_json()
        validate(request_data, creating_comment_schema)
    except:
        # Log a warning message and return a response if validation fails
        logging.warning("User did not enter a valid input for 'JSON type date'.")
        return Response(json.dumps({
            "response_code": 400,
            "response_message": "Method not allowed. Wrong request type. Required keys: ogrenciId, dersId, secenekId, icerikId, sorun, durum, tip",
            }),
            status=status.HTTP_400_BAD_REQUEST
        )
    cursor = conn.cursor()
    aciklama = bert_app.predict(request_data["sorun"]).to_string().split(" ")[-1]
    try:
        # Execute the query to insert the new comment into the database
        cursor.execute(
            "INSERT INTO sorun_bildir (ogrenciId, dersId, secenekId, icerikId, sorun, durum, tip, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
            (request_data["ogrenciId"], request_data["dersId"], request_data["secenekId"], request_data["icerikId"], request_data["sorun"], request_data["durum"], request_data["tip"], aciklama))
        conn.commit()
    except:
        # Reconnect and retry the query if the connection is lost
        logging.info("Connection lost. Reconnecting to database.")
        conn = create_connection()
        cursor = conn.cursor()
        aciklama = bert_app.predict(request_data["sorun"]).to_string().split(" ")[-1]
        cursor.execute(
            "INSERT INTO sorun_bildir (ogrenciId, dersId, secenekId, icerikId, sorun, durum, tip, aciklama) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
            (request_data["ogrenciId"], request_data["dersId"], request_data["secenekId"], request_data["icerikId"], request_data["sorun"], request_data["durum"], request_data["tip"], aciklama))
        conn.commit()
    cursor.close()
    return json.dumps(list)

# Route to label comments by a range of days and update the database
@app.route('/label_days/<int:number_of_days>', methods=['POST'])
def label_comments_by_today(number_of_days, conn=conn):
    today = datetime.now()
    cursor = conn.cursor()
    comment_list = []
    # Iterate over the range of days
    for day in range(number_of_days):
        n_days_ago = today - timedelta(days=day)
        try:
            # Execute the query to fetch records by date
            cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?",
                            (str(n_days_ago).split(" ")[0],))
        except:
            # Reconnect and retry the query if the connection is lost
            logging.info("Connection lost. Reconnecting to database.")
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id,sorun,tarih FROM sorun_bildir WHERE SUBSTRING(tarih, 1, 10)=?",
                           (str(n_days_ago).split(" ")[0],))
        # Process the fetched records
        for id, sorun, tarih in cursor:
            tarih = tarih.strftime("%Y-%m-%d %H:%M:%S")
            aciklama = bert_app.predict(sorun).to_string().split(" ")[-1]
            comment_list.append({
                "id": id,
                "tarih": tarih,
                "label": aciklama,
                "sorun": sorun
            })
            # Update the record with the predicted label
            cursor.execute(f"UPDATE sorun_bildir SET aciklama = {aciklama} WHERE id = {id}")
    conn.commit()
    cursor.close()
    return jsonify({'message': f"{len(comment_list)} soruna label eklendi."})

# Run the Flask application
app.run(port=5562)
