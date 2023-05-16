from datetime import datetime
import shutil
import tempfile
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField
from wtforms.validators import InputRequired, URL
import pymysql
import folium
import configparser
from werkzeug.utils import secure_filename
import os
import uuid
import pandas as pd
from io import BytesIO
from tempfile import NamedTemporaryFile

app = Flask(__name__)

app.config['SECRET_KEY'] = 'jsdbkhtow47e63784w9yrpofhsow84er5r98wyr'

app.config['UPLOAD_FOLDER'] = 'static/images'

# Read MySQL configuration from config file
config = configparser.ConfigParser()
config.read('config.ini')

# MySQL configuration
app.config['MYSQL_HOST'] = config.get('mysql', 'host')
app.config['MYSQL_USER'] = config.get('mysql', 'user')
app.config['MYSQL_PASSWORD'] = config.get('mysql', 'password')
app.config['MYSQL_DB'] = config.get('mysql', 'database')

# Create MySQL connection
mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=True  # Set autocommit mode to True
)

# Form for Node data
class NodeForm(FlaskForm):
    latitude = FloatField('Latitude', validators=[InputRequired()])
    longitude = FloatField('Longitude', validators=[InputRequired()])
    popup = StringField('Popup', validators=[InputRequired()])
    #image_filename = StringField('Rename Uploaded Image (.png)', validators=[InputRequired()])
    
    

@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Function to check and reopen MySQL connection
def check_mysql_connection():
    if not mysql.ping():
        mysql.connect()

@app.route('/')
def index():
    
    check_mysql_connection()
    
    #get default settings to Greece, zoom=6
    set_latitude = 37.908380
    set_longitude = 23.725310
    set_zoom = 6
    set_x_image = 25
    set_y_image = 25
    
    # Create a cursor object to execute queries
    with mysql.cursor() as cursor:
        # Execute a query to fetch latitude, longitude, and zoom from the settings_tbl table
        cursor.execute("SELECT map_latitude, map_longitude, zoom_level, x_image, y_image FROM settings_tbl")

        # Fetch the first row from the result
        row = cursor.fetchone()

        if row:
            set_latitude = row['map_latitude']
            set_longitude = row['map_longitude']
            set_zoom = row['zoom_level']
            set_x_image = row['x_image']
            set_y_image = row['y_image']
            
    cursor.close()        

    # Create a cursor object to execute queries
    cursor1 = mysql.cursor()

    # Execute a query to fetch latitude and longitude from the database
    cursor1.execute("SELECT latitude, longitude, popup, image_filename FROM nodes_tbl")

    # Fetch all the rows from the result
    rows = cursor1.fetchall()

    # Clear the m variable
    m = None
    
     # Create the Folium map
    m = folium.Map(location=[set_latitude, set_longitude], zoom_start=set_zoom)

    # Loop through the rows and add markers to the map
    for row in rows:
        latitude = row['latitude']
        longitude = row['longitude']
        popup = row['popup']
        image = row['image_filename']

        folium.Marker([latitude, longitude], popup=popup,
                      icon=folium.features.CustomIcon('static/images/' + image, icon_size=(set_x_image, set_y_image))).add_to(m)

    # Close the cursor
    
    cursor1.close()

    mysql.close()

    # render the map in a template
    return render_template('index.html', map=m._repr_html_())


@app.route('/list')
def list():
    check_mysql_connection()
    
    with mysql.cursor() as cursor:
        cursor.execute('SELECT * FROM nodes_tbl')
        nodes = cursor.fetchall()
    
    mysql.close()
    
    return render_template('list.html', nodes=nodes)



@app.route('/add', methods=['GET', 'POST'])
def add_node():
    check_mysql_connection()
    
    form = NodeForm()
    
    # Generate a random filename using timestamp and unique identifier
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_id = str(uuid.uuid4().hex)
    random_filename = f"{timestamp}_{unique_id}.png"
    
    
    if form.validate_on_submit():
        latitude = form.latitude.data
        longitude = form.longitude.data
        popup = form.popup.data


        # Save the uploaded image with the desired filename
        image = request.files['image']
        image.save(os.path.join('static/images', random_filename))

        with mysql.cursor() as cursor:
            sql = 'INSERT INTO nodes_tbl (latitude, longitude, popup, image_filename) VALUES (%s, %s, %s, %s)'
            cursor.execute(sql, (latitude, longitude, popup, random_filename))
            mysql.commit()

        mysql.close()
        return redirect(url_for('index'))
    mysql.close()
    return render_template('add.html', form=form)




# Edit node
@app.route('/edit/<int:node_id>', methods=['GET', 'POST'])
def edit_node(node_id):
    check_mysql_connection()
    
    form = NodeForm()
    if form.validate_on_submit():
        latitude = form.latitude.data
        longitude = form.longitude.data
        popup = form.popup.data
        #image_filename = form.image_filename.data
        # Generate a random filename using timestamp and unique identifier
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4().hex)
        random_filename = f"{timestamp}_{unique_id}.png"

        # Save the uploaded image
        image = request.files['image']
        image.save(os.path.join('static/images', random_filename))

        with mysql.cursor() as cursor:
            sql = 'UPDATE nodes_tbl SET latitude=%s, longitude=%s, popup=%s, image_filename=%s WHERE id=%s'
            cursor.execute(sql, (latitude, longitude, popup, random_filename, node_id))
            mysql.commit()

        return redirect(url_for('index'))
    else:
        with mysql.cursor() as cursor:
            sql = 'SELECT * FROM nodes_tbl WHERE id=%s'
            cursor.execute(sql, node_id)
            node = cursor.fetchone()
            form.latitude.data = node['latitude']
            form.longitude.data = node['longitude']
            form.popup.data = node['popup']
            #form.image_filename.data = node['image_filename']
    mysql.close()
    
    return render_template('edit.html', form=form, node_id=node_id)

# Delete node
@app.route('/delete/<int:node_id>', methods=['GET', 'POST'])
def delete_node(node_id):
    check_mysql_connection()
    
    with mysql.cursor() as cursor:
        sql = 'SELECT image_filename FROM nodes_tbl WHERE id=%s'
        cursor.execute(sql, node_id)
        node = cursor.fetchone()

        if node:
            # Delete the image file
            image_filename = node['image_filename']
            image_path = os.path.join('static/images', image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

            # Delete the node from the database
            delete_sql = 'DELETE FROM nodes_tbl WHERE id=%s'
            cursor.execute(delete_sql, node_id)
            mysql.commit()
    
    mysql.close()

    return redirect(url_for('list'))


@app.route('/edit-settings', methods=['GET', 'POST'])
def edit_settings():
    check_mysql_connection()
    
    # Retrieve the current settings from the database
    with mysql.cursor() as cursor:
        cursor.execute("SELECT map_latitude, map_longitude, zoom_level, x_image, y_image FROM settings_tbl")
        row = cursor.fetchone()

    if request.method == 'POST':
        # Get the updated values from the form submission
        map_latitude = request.form['map_latitude']
        map_longitude = request.form['map_longitude']
        zoom_level = request.form['zoom_level']
        x_image = request.form['x_image']
        y_image = request.form['y_image']

        # Update the settings in the database
        with mysql.cursor() as cursor:
            cursor.execute("UPDATE settings_tbl SET map_latitude = %s, map_longitude = %s, zoom_level = %s, "
                           "x_image = %s, y_image = %s", (map_latitude, map_longitude, zoom_level, x_image, y_image))
            mysql.commit()

        # Redirect to the settings page or any other desired location
        return redirect(url_for('edit_settings'))
    
    mysql.close()
    # Render the edit settings form template with the current values
    return render_template('edit_settings.html', settings=row)


@app.route('/import', methods=['GET'])
def import_form():
    return render_template('import.html')


@app.route('/import-nodes', methods=['POST'])
def import_nodes():
    check_mysql_connection()

    # Check if the request contains the Excel file and image file
    if 'excel-file' not in request.files or 'image-file' not in request.files:
        flash('Excel file or image file not provided', 'error')
        return redirect(url_for('import_form'))

    excel_file = request.files['excel-file']
    image_file = request.files['image-file']

    # Check if the file names are empty
    if excel_file.filename == '' or image_file.filename == '':
        flash('Excel file or image file name is empty', 'error')
        return redirect(url_for('import_form'))

    # Read the Excel file and import data
    try:
        df = pd.read_excel(excel_file)

        # Save the image file to a temporary buffer
        temp_image = NamedTemporaryFile(delete=False, dir='static/images/tmp')
        image_file.save(temp_image.name)
        temp_image.close()  # Close the temporary file

        for index, row in df.iterrows():
            latitude = row['latitude']
            longitude = row['longitude']
            popup = row['popup']
            image_filename = row['image_filename']

            # Copy the image file multiple times with the provided filename
            for _ in range(5):
                new_image_path = os.path.join('static/images', secure_filename(image_filename))
                shutil.copy2(temp_image.name, new_image_path)

            # Insert the node data into the database
            with mysql.cursor() as cursor:
                sql = 'INSERT INTO nodes_tbl (latitude, longitude, popup, image_filename) VALUES (%s, %s, %s, %s)'
                cursor.execute(sql, (latitude, longitude, popup, image_filename))

        flash('Nodes imported successfully', 'success')
    except Exception as e:
        flash(f'Failed to import nodes: {str(e)}', 'error')

    mysql.close()

    # Remove the temporary image file with retry
    max_retries = 5
    retries = 0
    while retries < max_retries:
        try:
            os.remove(temp_image.name)
            break
        except PermissionError:
            time.sleep(0.1)  # Wait for a short delay before retrying
            retries += 1

    return redirect(url_for('import_form'))




if __name__ == '__main__':
    app.run(debug=True)
