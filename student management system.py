"""
Student Management System - Mini Project
Console based, uses only the Python standard library.
Data is saved in students.json so it persists between runs.
"""

import json
import os

DATA_FILE = "students.json"
SUBJECTS = ["Maths", "Science", "English", "Computer", "Social"]


# ---------------------------------------------------------------- storage
def load_data():
    """Load students from the JSON file. Returns a dict keyed by roll number."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read data file. Starting with empty data.")
        return {}


def save_data(students):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, indent=4)
    except OSError as e:
        print(f"Error saving data: {e}")


# ---------------------------------------------------------------- helpers
def read_text(prompt, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("Input cannot be empty. Try again.")


def read_int(prompt, low=None, high=None, allow_empty=False):
    while True:
        raw = input(prompt).strip()
        if raw == "" and allow_empty:
            return None
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a valid whole number.")
            continue
        if low is not None and value < low:
            print(f"Value must be at least {low}.")
            continue
        if high is not None and value > high:
            print(f"Value must be at most {high}.")
            continue
        return value


def read_marks(prompt_prefix=""):
    marks = {}
    for subject in SUBJECTS:
        marks[subject] = read_int(f"{prompt_prefix}{subject} marks (0-100): ", 0, 100)
    return marks


def calculate_result(marks):
    total = sum(marks.values())
    percentage = total / (len(SUBJECTS) * 100) * 100
    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 40:
        grade = "D"
    else:
        grade = "F"
    status = "FAIL" if any(m < 35 for m in marks.values()) else "PASS"
    return total, percentage, grade, status


def print_student(roll, s):
    total, percentage, grade, status = calculate_result(s["marks"])
    print("-" * 50)
    print(f"Roll No    : {roll}")
    print(f"Name       : {s['name']}")
    print(f"Age        : {s['age']}")
    print(f"Course     : {s['course']}")
    print(f"Phone      : {s['phone']}")
    print("Marks      : " + ", ".join(f"{k}={v}" for k, v in s["marks"].items()))
    print(f"Total      : {total}/{len(SUBJECTS) * 100}")
    print(f"Percentage : {percentage:.2f}%")
    print(f"Grade      : {grade}   Result: {status}")
    print("-" * 50)


# ---------------------------------------------------------------- features
def add_student(students):
    print("\n--- Add Student ---")
    roll = read_text("Roll number: ")
    if roll in students:
        print("A student with this roll number already exists.")
        return
    name = read_text("Name: ")
    age = read_int("Age: ", 3, 100)
    course = read_text("Course/Class: ")
    phone = read_text("Phone: ")
    marks = read_marks()
    students[roll] = {
        "name": name,
        "age": age,
        "course": course,
        "phone": phone,
        "marks": marks,
    }
    save_data(students)
    print("Student added successfully.")


def view_all(students):
    print("\n--- All Students ---")
    if not students:
        print("No records found.")
        return
    print(f"{'Roll':<10}{'Name':<20}{'Course':<15}{'%':<10}{'Grade':<6}{'Result'}")
    print("-" * 70)
    for roll in sorted(students):
        s = students[roll]
        _, pct, grade, status = calculate_result(s["marks"])
        print(f"{roll:<10}{s['name'][:18]:<20}{s['course'][:13]:<15}{pct:<10.2f}{grade:<6}{status}")
    print(f"\nTotal students: {len(students)}")


def search_student(students):
    print("\n--- Search Student ---")
    if not students:
        print("No records found.")
        return
    key = read_text("Enter roll number or name (part of name works): ").lower()
    found = False
    for roll, s in sorted(students.items()):
        if key == roll.lower() or key in s["name"].lower():
            print_student(roll, s)
            found = True
    if not found:
        print("No matching student found.")


def update_student(students):
    print("\n--- Update Student ---")
    roll = read_text("Roll number to update: ")
    if roll not in students:
        print("Student not found.")
        return
    s = students[roll]
    print("Leave a field empty to keep the current value.")
    name = read_text(f"Name [{s['name']}]: ", allow_empty=True)
    age = read_int(f"Age [{s['age']}]: ", 3, 100, allow_empty=True)
    course = read_text(f"Course [{s['course']}]: ", allow_empty=True)
    phone = read_text(f"Phone [{s['phone']}]: ", allow_empty=True)
    if name:
        s["name"] = name
    if age is not None:
        s["age"] = age
    if course:
        s["course"] = course
    if phone:
        s["phone"] = phone
    change = read_text("Update marks too? (y/n): ").lower()
    if change == "y":
        s["marks"] = read_marks()
    save_data(students)
    print("Student updated successfully.")


def delete_student(students):
    print("\n--- Delete Student ---")
    roll = read_text("Roll number to delete: ")
    if roll not in students:
        print("Student not found.")
        return
    confirm = read_text(f"Delete {students[roll]['name']}? (y/n): ").lower()
    if confirm == "y":
        del students[roll]
        save_data(students)
        print("Student deleted.")
    else:
        print("Deletion cancelled.")


def show_toppers(students):
    print("\n--- Top 3 Students ---")
    if not students:
        print("No records found.")
        return
    ranked = sorted(
        students.items(),
        key=lambda item: calculate_result(item[1]["marks"])[0],
        reverse=True,
    )
    for rank, (roll, s) in enumerate(ranked[:3], start=1):
        total, pct, grade, _ = calculate_result(s["marks"])
        print(f"{rank}. {s['name']} (Roll {roll}) - {total} marks, {pct:.2f}%, Grade {grade}")


def show_statistics(students):
    print("\n--- Class Statistics ---")
    if not students:
        print("No records found.")
        return
    percentages = [calculate_result(s["marks"])[1] for s in students.values()]
    passed = sum(1 for s in students.values() if calculate_result(s["marks"])[3] == "PASS")
    print(f"Total students  : {len(students)}")
    print(f"Passed          : {passed}")
    print(f"Failed          : {len(students) - passed}")
    print(f"Class average   : {sum(percentages) / len(percentages):.2f}%")
    print(f"Highest         : {max(percentages):.2f}%")
    print(f"Lowest          : {min(percentages):.2f}%")
    print("Subject averages:")
    for subject in SUBJECTS:
        avg = sum(s["marks"][subject] for s in students.values()) / len(students)
        print(f"  {subject:<10}: {avg:.2f}")


# ---------------------------------------------------------------- main menu
def menu():
    print("\n" + "=" * 40)
    print("     STUDENT MANAGEMENT SYSTEM")
    print("=" * 40)
    print("1. Add student")
    print("2. View all students")
    print("3. Search student")
    print("4. Update student")
    print("5. Delete student")
    print("6. Show top 3 students")
    print("7. Class statistics")
    print("8. Exit")


def main():
    students = load_data()
    actions = {
        "1": add_student,
        "2": view_all,
        "3": search_student,
        "4": update_student,
        "5": delete_student,
        "6": show_toppers,
        "7": show_statistics,
    }
    while True:
        menu()
        choice = input("Enter your choice (1-8): ").strip()
        if choice == "8":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action(students)
        else:
            print("Invalid choice. Please enter a number from 1 to 8.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")