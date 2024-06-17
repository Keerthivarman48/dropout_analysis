import io
import pandas as pd
from flask import Flask, flash, render_template, request, redirect, url_for, send_file
import json
import openpyxl
from matplotlib.figure import Figure
import matplotlib.backends.backend_agg as agg
import base64

app = Flask(__name__)
app.secret_key = 'keerthi'
dropout_data = {
    "school": {},
    "area": {},
    "gender": {},
    "caste": {},
    "age_standard": {},
}



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check for user/admin credentials (for demonstration purposes only)
        if username == 'admin' and password == '2':
            # Admin is logged in, redirect to admin dashboard
            return redirect(url_for('admin_dashboard'))
        elif username == 'user' and password == '1':
            # User is logged in, redirect to user dashboard
            return redirect(url_for('user_dashboard'))
        else:
            # Invalid credentials, show an error message
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    # Read the Excel data
    excel_data = pd.read_excel('dropout_data.xlsx')
    
    # Extract relevant columns
    categories = excel_data['Category'].tolist()  # Convert Series to list
    dropout_counts = excel_data['Dropout Count'].tolist()  # Convert Series to list

    # Create a pie chart
    pie_chart_data = [{
        'labels': categories,
        'values': dropout_counts,
        'type': 'pie',
    }]

    # Create a bar chart
    bar_chart_data = [{
        'x': categories,
        'y': dropout_counts,
        'type': 'bar',
    }]

    # Create a line chart (example data)
    line_chart_data = [{
        'x': categories,
        'y': dropout_counts,  # Example data, replace with your actual data
        'type': 'line',
        'name': 'Line Chart',
    }]

    # Create a scatter plot (example data)
    scatter_plot_data = [{
        'x': categories,
        'y': dropout_counts,  # Example data, replace with your actual data
        'mode': 'markers',
        'type': 'scatter',
        'name': 'Scatter Plot',
    }]

    return render_template('admin_dashboard.html', pie_chart_data=pie_chart_data, bar_chart_data=bar_chart_data, line_chart_data=line_chart_data, scatter_plot_data=scatter_plot_data,)

@app.route('/user_dashboard')
def user_dashboard():
    # Check if the user is a regular user (for demonstration purposes only)
    return render_template('user_dashboard.html', dropout_data=dropout_data)

@app.route('/update', methods=['POST'])
def update_data():
    category = request.form['category']
    subcategory = request.form['subcategory']
    dropout_count = int(request.form['dropout_count'])
    total_students = int(request.form['total_students'])

    if category in dropout_data and subcategory:
        if subcategory not in dropout_data[category]:
            dropout_data[category][subcategory] = {
                'dropout_count': 0,
                'total_students': 0,
            }

        dropout_data[category][subcategory]['dropout_count'] += dropout_count
        dropout_data[category][subcategory]['total_students'] += total_students

    # Save data to an Excel file
    save_to_excel()

    return redirect(url_for('user_dashboard'))

def calculate_percentage(dropout_count, total_students):
    if total_students == 0:
        return 0.0
    return (dropout_count / total_students) * 100.0

def save_to_excel():
    # Create a Pandas DataFrame from the dropout_data dictionary
    data_list = []
    for category, subcategories in dropout_data.items():
        for subcategory, values in subcategories.items():
            dropout_count = values['dropout_count']
            total_students = values['total_students']
            percentage = calculate_percentage(dropout_count, total_students)
            data_list.append([category, subcategory, dropout_count, total_students, percentage])
    
    df = pd.DataFrame(data_list, columns=['Category', 'Subcategory', 'Dropout Count', 'Total Students', 'Percentage'])

    # Save the DataFrame to an Excel file
    df.to_excel('dropout_data.xlsx', index=False)

@app.route('/modify_entry/<category>/<subcategory>', methods=['GET', 'POST'])
def modify_entry(category, subcategory):
    if request.method == 'POST':
        # Handle the form submission to update the entry
        updated_dropout_count = int(request.form['updated_dropout_count'])
        updated_total_students = int(request.form['updated_total_students'])
        
        if category in dropout_data and subcategory in dropout_data[category]:
            dropout_data[category][subcategory]['dropout_count'] = updated_dropout_count
            dropout_data[category][subcategory]['total_students'] = updated_total_students

            # Save data to an Excel file
            save_to_excel()

            # Redirect to the user dashboard after updating
            return redirect(url_for('user_dashboard'))

    if category in dropout_data and subcategory in dropout_data[category]:
        entry = dropout_data[category][subcategory]
        return render_template('modify_entry.html', category=category, subcategory=subcategory, entry=entry)

    # Handle cases where the category or subcategory is not found
    flash('Category or subcategory not found', 'error')
    return redirect(url_for('user_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
