from flask import Flask, render_template, request, redirect
import mysql.connector
from nltk.chat.util import Chat, reflections
from datetime import datetime
from datetime import timedelta
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
CORS(app)


patterns = [
    (r'(.*\bhi\b.*|.*\bhello\b.*|.*\bhey\b.*)', ['Hello!', 'Hi there!', 'How can I assist you today?']),
    (r'(.*book.*room.*)', ['Sure, I can help you with that']),
    (r'(.*cancel.*booking|.*cancel.*reservation.*)', ['Please provide your booking ID or reservation details for cancellation.']),
    #(r'(.*check.*availability.*)', ['Which type of room are you interested in? Standard, Double, or Suite?']),
    (r'(.*check.*availability.*)', ['You can <a href="/check_availability"> check availability for room here.']),
    (r'(.*available.*rooms|.*rooms.*available.*)', ['Currently, we have the following rooms available: Standard, Double, and Suite.']),
    (r'(.*room.*service.*)', ['Our room service includes a variety of options such as dining, cleaning, and laundry services.']),
    (r'(.*amenitie.*)', ['We offer various amenities including a swimming pool, gym, and restaurant.']),
    (r'(.*help.*)', ['How can I assist you today?']),
    (r'(.*breakfast.*time.*)', ['Breakfast is offered free to our customers, from 6:30AM to 8:30AM on weekdays and from 6:30AM to 9:30AM on weekends.']),
    (r'(.*WiFi.*)', ['High-speed wireless internet is offered for free throughout the hotel.']),
    (r'(.*check.*in.*time.*)', ['Customers are expected to arrive at 2PM. We will gladly provide you with access to your room earlier if possible.']),
    (r'(.*check.*out.*time.*)', ['Customers must check out at 12PM. However, we can keep your luggage for free if need be.']),
    (r'(.*early.*check.*in.*)', ['Early check-in is subject to availability. You can request it during booking or contact us closer to your arrival date.']),
    (r'(.*late.*check.*out.*)', ['Late check-out may be available upon request and is subject to availability. Please inform us in advance.']),
    (r'(.*payment.*methods.*)', ['We accept major credit cards such as Visa, MasterCard, and American Express.']),
    (r'(.*cancellation.*policy.*)', ['Our cancellation policy varies depending on the rate and booking conditions. Please refer to your booking confirmation or contact us for details.']),
    (r'(.*parking.*)', ['We offer complimentary parking for our guests.']),
    (r'(.*pet.*)', ['Unfortunately, we do not allow pets in our hotel.']),
    (r'(.*special.*request.*)', ['Please let us know of any special requests or preferences you have, and we will do our best to accommodate them.']),
    (r'(.*fitness.*center.*)', ['Our fitness center is open 24/7 for our guests.']),
    (r'(.*smoking.*policy.*)', ['Smoking is not permitted in any indoor areas of the hotel.']),
    (r'(.*conference.*facility.*)', ['We have conference facilities available for meetings and events.']),
    (r'(.*shuttle.*service.*)', ['We provide shuttle services to and from the airport/train station upon request.']),
    (r'.*', ["I'm sorry, I didn't understand that. How can I assist you today?"]),
    # Add more patterns and responses as needed
]

# Create a chatbot
chatbot = Chat(patterns, reflections)

# MySQL connection configuration
db_config = {
    'host': 'localhost',
    'port': 3307,
    'user': 'root',
    'password': 'root',
    'database': 'hotel_management',
    #'auth_plugin':'caching_sha2_password'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/rooms")
def getRoomsfromDB():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = "SELECT * from RoomInfo"
        cursor.execute(query)

        # Get column names from description
        column_names = [i[0] for i in cursor.description] 

        # Fetch all results as a list of dictionaries
        rooms = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        
        cursor.close()
        cnx.close()
        return jsonify(rooms)
        
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return False


@app.route("/spaServices")
def spa_services():
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = "SELECT * from spa_services"
        cursor.execute(query)

        # Get column names from description
        column_names = [i[0] for i in cursor.description] 

        # Fetch all results as a list of dictionaries
        services = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        
        cursor.close()
        cnx.close()
        return jsonify(services)
        
    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return False
        

@app.route('/book-room')
def book_room():
    # Calculate the current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    # Calculate the date one month from the current date
    max_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    return render_template('book_room.html', current_date=current_date, max_date=max_date)

# Define route to handle chatbot interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response = chatbot.respond(user_input)
    return response

@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    room_type = request.form['room_type']
    check_in_date = request.form['check_in_date']
    check_out_date = request.form['check_out_date']
    num_guests = request.form['num_guests']
    num_rooms = request.form['num_rooms']
    guest_name = request.form['guest_name']
    guest_contact = request.form['guest_contact']
    guest_email = request.form['guest_email']

    # Connect to MySQL database
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    

    # Query the database to count the number of booked rooms for the specified date and room type
    availability_query = ("SELECT IFNULL(SUM(num_rooms), 0) FROM bookings "
                          "WHERE room_type = %s AND check_in_date = %s")
    cursor.execute(availability_query, (room_type, check_in_date))
    booked_rooms_count = cursor.fetchone()[0]

    # Close the cursor
    cursor.close()

    # Check if the number of booked rooms plus the requested rooms exceeds the maximum capacity (10)
    if booked_rooms_count + int(num_rooms) > 10:
        # Redirect the user to a page indicating that rooms are fully booked for the specified date and room type
        return redirect('/rooms_fully_booked')

    # If room availability is confirmed, proceed with inserting booking data into the database
    # Reconnect to the database and create a new cursor
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Insert booking data into the database
    insert_query = ("INSERT INTO bookings (room_type, check_in_date, check_out_date, "
                    "num_guests, num_rooms, guest_name, guest_contact, guest_email) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    booking_data = (room_type, check_in_date, check_out_date, num_guests, num_rooms,
                    guest_name, guest_contact, guest_email)
    cursor.execute(insert_query, booking_data)

    # Commit the transaction and close the connection
    cnx.commit()
    cursor.close()
    cnx.close()

    return redirect('/confirmation')

def check_room_availability(room_type, check_in_date):
    try:
        # Connect to MySQL database
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        # Query the database to count the number of booked rooms for the specified room type and check-in date
        query = ("SELECT IFNULL(SUM(num_rooms), 0) FROM bookings "
                 "WHERE room_type = %s AND check_in_date = %s")
        cursor.execute(query, (room_type, check_in_date))
        booked_rooms_count = cursor.fetchone()[0]

        # Close cursor and database connection
        cursor.close()
        cnx.close()

        # Total rooms available for each room type
        total_rooms = 10  # Example: Total rooms available for each room type is 10

        # Check if the number of booked rooms exceeds the total rooms available
        return booked_rooms_count < total_rooms

    except mysql.connector.Error as err:
        print("MySQL Error:", err)
        return False  # Return False in case of any database error


# Route to render the HTML form for checking availability
@app.route('/check_availability', methods=['GET', 'POST'])
def check_availability():
    if request.method == 'GET':
        # Render the availability check form
        return render_template('availability_form.html')
    elif request.method == 'POST':
        try:
            # Retrieve form data
            room_type = request.form['room_type']
            check_in_date = request.form['check_in_date']
            
            # Check room availability in the database
            rooms_available = check_room_availability(room_type, check_in_date)

            if rooms_available:
                return 'Rooms are available for booking.'
            else:
                return 'Rooms are fully booked for the specified date and room type.'

        except Exception as e:
            # Handle errors
            return 'An error occurred while processing your request.'

@app.route('/rooms_fully_booked')
def rooms_fully_booked():
    return 'Rooms are fully booked for the specified date and room type. Please select another day or room type.'

@app.route('/confirmation')
def confirmation():
    return 'Booking submitted successfully!'
    
@app.route('/chatbot-popup')
def chatbot_popup():
    return render_template('chatbot_popup.html')

if __name__ == '__main__':
    app.run(debug=True)
