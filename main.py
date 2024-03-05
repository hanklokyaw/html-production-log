from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# Get today's date
today_date = datetime.now()
# Format the date as mm-dd-%y
formatted_date = today_date.strftime("%m-%d-%y")

operator_df = pd.read_excel('operator_list.xlsx')
machine_df = pd.read_excel('machine_list.xlsx')
item_df = pd.read_excel('item_list.xlsx')

# Extract choices for operators, machines, and item codes
operator_list = list(operator_df['Operator'])
machine_list = list(machine_df['Machine'])
item_list = list(item_df['Item'])

# # Create a folder for each operator if it doesn't exist
# for operator_name in operator_list:
#     operator_folder = f'operators/{operator_name}'
#     os.makedirs(operator_folder, exist_ok=True)

class MachineForm(FlaskForm):
    # operator = SelectField("Operator", choices=operator_list, validators=[DataRequired()])
    machine = SelectField("Machine", choices=machine_list, validators=[DataRequired()])
    item = SelectField("Item", choices=item_list, validators=[DataRequired()])
    setup_time = StringField('Setup Time', validators=[DataRequired()])
    machine_cycle_time = StringField('Machine Cycle Time', validators=[DataRequired()])
    parts_per_cycle = StringField('Parts Per Cycle', validators=[DataRequired()])
    total_quantity = StringField('Total Quantity', validators=[DataRequired()])
    job_time = StringField('Job Time', validators=[DataRequired()])
    operation_number = StringField('Op #', validators=[DataRequired()])
    notes = StringField('Notes')
    start_time = StringField('Start Time')
    end_time = StringField('End time')
    submit = SubmitField('Submit')


def get_csv_file_path(operator_name):
    folder_path = f'operators/{operator_name}'
    os.makedirs(folder_path, exist_ok=True)

    file_path = f'{folder_path}/daily_entry_{formatted_date}.csv'

    # If the file doesn't exist, create it with headers
    if not os.path.exists(file_path):
        with open(file_path, mode='w', newline='', encoding='utf-8') as new_csv_file:
            csv_writer = csv.writer(new_csv_file)
            # Add headers to the new file
            csv_writer.writerow([
                'Date',
                'Operator',
                'Machine',
                'Item',
                'Setup Time',
                'Machine Cycle Time',
                'Parts Per Cycle',
                'Total Quantity',
                'Job Time',
                'Op #',
                'Notes',
                'Start Time',
                'End time'
            ])

    return file_path



@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add/<string:operator_name>', methods=["GET", "POST"])
def add_record(operator_name):
    form = MachineForm()
    if form.validate_on_submit():
        with open(get_csv_file_path(operator_name), mode="a", encoding='utf-8', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([
                formatted_date,
                operator_name,
                form.machine.data,
                form.item.data,
                form.setup_time.data,
                form.machine_cycle_time.data,
                form.parts_per_cycle.data,
                form.total_quantity.data,
                form.job_time.data,
                form.operation_number.data,
                form.notes.data,
                form.start_time.data,
                form.end_time.data
            ])
        return redirect(url_for('operators', operator_name=operator_name))
    return render_template('add.html', form=form, operator_name=operator_name)




@app.route('/machine/<string:operator_name>')
def operators(operator_name):
    csv_file_path = get_csv_file_path(operator_name)
    if os.path.exists(csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
            csv_data = csv.reader(csv_file, delimiter=',')
            list_of_rows = [row for row in csv_data]
        return render_template('operators.html', operators=list_of_rows, operator_name=operator_name, today=formatted_date)
    else:
        return f"No data available for {operator_name} today."


@app.route('/edit/<string:operator_name>/<int:index>', methods=["GET", "POST"])
def edit_record(operator_name, index):
    csv_file_path = get_csv_file_path(operator_name)
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode="r", encoding='utf-8', newline='') as csv_file:
            csv_data = list(csv.reader(csv_file, delimiter=','))
            if index < len(csv_data):
                record = csv_data[index]
                form = MachineForm(data={
                    'operator': record[1],
                    'machine': record[2],
                    'item': record[3],
                    'setup_time': record[4],
                    'machine_cycle_time': record[5],
                    'parts_per_cycle': record[6],
                    'total_quantity': record[7],
                    'job_time': record[8],
                    'operation_number': record[9],
                    'notes': record[10],
                    'start_time': record[11],
                    'end_time': record[12]
                })
                if form.validate_on_submit():
                    # Update the record in the CSV file
                    csv_data[index] = [
                        formatted_date,
                        operator_name,
                        form.machine.data,
                        form.item.data,
                        form.setup_time.data,
                        form.machine_cycle_time.data,
                        form.parts_per_cycle.data,
                        form.total_quantity.data,
                        form.job_time.data,
                        form.operation_number.data,
                        form.notes.data,
                        form.start_time.data,
                        form.end_time.data
                    ]
                    with open(csv_file_path, mode="w", encoding='utf-8', newline='') as updated_csv_file:
                        csv_writer = csv.writer(updated_csv_file)
                        csv_writer.writerows(csv_data)
                    return redirect(url_for('operators', operator_name=operator_name))
                return render_template('edit.html', form=form, operator_name=operator_name, index=index)
            else:
                return f"Invalid index for editing record for {operator_name}."
    else:
        return f"No data available for {operator_name} today."


@app.route('/delete/<string:operator_name>/<int:index>')
def delete_record(operator_name, index):
    csv_file_path = get_csv_file_path(operator_name)
    if os.path.exists(csv_file_path):
        with open(csv_file_path, newline='', encoding='utf-8') as csv_file:
            csv_data = list(csv.reader(csv_file, delimiter=','))
            if index < len(csv_data):
                # Delete the record from the CSV file
                del csv_data[index]
                with open(csv_file_path, mode="w", newline='', encoding='utf-8') as updated_csv_file:
                    csv_writer = csv.writer(updated_csv_file)
                    for row in csv_data:
                        csv_writer.writerow(row)
                return redirect(url_for('operators', operator_name=operator_name))
            else:
                return f"Invalid index for deleting record for {operator_name}."
    else:
        return f"No data available for {operator_name} today."



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5002)
