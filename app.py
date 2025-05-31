from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Needed for flash messages

def get_db_connection():
    conn = sqlite3.connect('survey.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        contact_number = request.form.get('contact_number')
        favorite_foods = ','.join(request.form.getlist('favorite_foods'))  # Handle multiple checkboxes
        movies_rating = request.form.get('movies_rating')
        radio_rating = request.form.get('radio_rating')
        eating_out_rating = request.form.get('eating_out_rating')
        tv_rating = request.form.get('tv_rating')

        # Server-side validation
        errors = []
        if not all([full_name, email, date_of_birth, contact_number]):
            errors.append('All personal details fields are required.')
        
        # Validate age
        try:
            dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
            age = (datetime.now() - dob).days / 365.25
            if age < 5 or age > 120:
                errors.append('Age must be between 5 and 120 years.')
        except ValueError:
            errors.append('Invalid date of birth format.')

        # Validate ratings
        if not all([movies_rating, radio_rating, eating_out_rating, tv_rating]):
            errors.append('All rating questions must be answered.')
        else:
            try:
                ratings = [int(movies_rating), int(radio_rating), int(eating_out_rating), int(tv_rating)]
                if not all(1 <= r <= 5 for r in ratings):
                    errors.append('Ratings must be between 1 and 5.')
            except ValueError:
                errors.append('Ratings must be valid numbers.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('survey.html')

        # Save to database
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO surveys (full_name, email, date_of_birth, contact_number, favorite_foods,
                                movies_rating, radio_rating, eating_out_rating, tv_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (full_name, email, date_of_birth, contact_number, favorite_foods,
              movies_rating, radio_rating, eating_out_rating, tv_rating))
        conn.commit()
        conn.close()
        flash('Survey submitted successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('survey.html')

@app.route('/results')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)