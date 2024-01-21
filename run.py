import json
import csv
from collections import defaultdict
import matplotlib.pyplot as plt
from jinja2 import Template
import os
import numpy as np

# Constants
STUDENTS_FILE = "students.json"
COURSES_FILE = "courses.json"

# Load existing data
def load_data(filename):
    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    return data


def save_data(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=2)

# Students
def list_students():
    students = load_data(STUDENTS_FILE)
    for student in students:
        print(f"Code: {student['code']}, Name: {student['name']}, Birthdate: {student['birthdate']}")

def add_student():
    students = load_data(STUDENTS_FILE)
    code = input("Enter student code: ")
    name = input("Enter student name: ")
    birthdate = input("Enter student birthdate: ")
    students.append({"code": code, "name": name, "birthdate": birthdate})
    save_data(STUDENTS_FILE, students)

# Courses
def list_courses():
    courses = load_data(COURSES_FILE)
    for course in courses:
        print(f"Code: {course['code']}, Name: {course['name']}, Max Degree: {course['max_degree']}")

def add_course():
    courses = load_data(COURSES_FILE)
    code = input("Enter course code: ")
    name = input("Enter course name: ")
    max_degree = input("Enter max degree: ")
    courses.append({"code": code, "name": name, "max_degree": max_degree})
    save_data(COURSES_FILE, courses)

# Grades
def supply_grades():
    students = load_data(STUDENTS_FILE)
    courses = load_data(COURSES_FILE)

    student_code = input("Enter student code: ")
    course_code = input("Enter course code: ")
    grade = input("Enter grade: ")

    # Save grade to CSV file
    with open(f"{course_code}.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([student_code, grade])

# Results
def generate_html_result():
    students = load_data(STUDENTS_FILE)
    courses = load_data(COURSES_FILE)

    student_code = input("Enter student code: ")
    grades = defaultdict(list)

    # Load grades from CSV files or create an empty file if it doesn't exist
    for course in courses:
        course_code = course["code"]
        csv_filename = f"{course_code}.csv"

        if os.path.exists(csv_filename):
            with open(csv_filename, "r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row[0] == student_code:
                        grades[course_code].append(int(row[1]))
        else:
            print(f"CSV file for course {course_code} doesn't exist. Creating an empty file.")
            with open(csv_filename, "w", newline=""):
                pass  # Create an empty file

    # Calculate final result using credit hours grading system (simplified)
    final_result = {}
    for course in courses:
        course_code = course["code"]
        total_credits = len(grades[course_code])
        if total_credits > 0:
            average_grade = sum(grades[course_code]) / total_credits
            final_result[course_code] = average_grade

    # Generate Bar Chart
    bar_chart_filename = f"{student_code}_bar_chart.png"
    generate_bar_chart(final_result, bar_chart_filename)

    # Generate Pie Chart
    pie_chart_filename = f"{student_code}_pie_chart.png"
    generate_pie_chart(courses, pie_chart_filename)

    # Generate HTML file
    with open(f"{student_code}.html", "w") as html_file:
        template = Template("""
        <html>
        <head>
            <title>Student Result</title>
            <style>
                img {
                    max-width: 50%;
                    height: auto;
                }
            </style>
        </head>
        <body>
        <h1>Student Result</h1>
        <p>Student Code: {{ student_code }}</p>
        <table border="1">
            <tr>
                <th>Course Code</th>
                <th>Final Grade</th>
            </tr>
            {% for course, grade in final_result.items() %}
                <tr>
                    <td>{{ course }}</td>
                    <td>{{ grade }}</td>
                </tr>
            {% endfor %}
        </table>
        <h2>Bar Chart</h2>
        <img src="{{ bar_chart_filename }}" alt="Bar Chart">
        <h2>Pie Chart</h2>
        <img src="{{ pie_chart_filename }}" alt="Pie Chart">
        </body>
        </html>
        """)
        html_file.write(template.render(student_code=student_code, final_result=final_result,
                                       bar_chart_filename=bar_chart_filename,
                                       pie_chart_filename=pie_chart_filename))

# Charts
def generate_bar_chart(final_result, filename):
    courses = list(final_result.keys())
    grades = list(final_result.values())

    fig, ax = plt.subplots()
    ax.bar(courses, grades)
    ax.set_ylabel('Final Grade')
    ax.set_xlabel('Course Code')
    ax.set_title('Student Results per Course')
    plt.savefig(filename)
    plt.close()

def generate_pie_chart(courses, filename):
    course_names = [course['name'] for course in courses]
    course_registration = [len(load_data(f"{course['code']}.csv")) for course in courses]

    # Handle NaN and negative values
    valid_values = [value if not np.isnan(value) and value >= 0 else 0 for value in course_registration]

    total_students = sum(valid_values)

    # Check if total_students is zero to avoid division by zero
    if total_students == 0:
        percentages = [0] * len(valid_values)
    else:
        percentages = [value / total_students * 100 for value in valid_values]

    fig, ax = plt.subplots()
    ax.pie(valid_values, labels=course_names, autopct=lambda p: '{:.1f}%'.format(p) if p != 0 else '',
           startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that the pie is drawn as a circle.
    ax.set_title('Course Registration Distribution')
    plt.savefig(filename)
    plt.close()


# Main program
while True:
    print("\n1. List/Add Students")
    print("2. List/Add Courses")
    print("3. Supply Grades")
    print("4. Generate HTML Result")
    print("5. Generate Bar Chart")
    print("6. Generate Pie Chart")
    print("7. Exit")

    choice = input("Enter your choice (1-7): ")

    if choice == "1":
        list_students()
        add_student()
    elif choice == "2":
        list_courses()
        add_course()
    elif choice == "3":
        supply_grades()
    elif choice == "4":
        generate_html_result()
    elif choice == "5":
        generate_bar_chart()
    elif choice == "6":
        generate_pie_chart()
    elif choice == "7":
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 7.")
