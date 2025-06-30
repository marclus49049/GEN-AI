class Student:
    def __init__(self, student_id, name, age, grade):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade

    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}, Age: {self.age}, Grade: {self.grade}"

class StudentManagementSystem:
    def __init__(self):
        self.students = {}

    def add_student(self, student):
        if student.student_id in self.students:
            print(f"Student with ID {student.student_id} already exists.")
        else:
            self.students[student.student_id] = student
            print(f"Student {student.name} added successfully.")

    def list_students(self):
        if not self.students:
            print("No students found.")
            return
        for student in self.students.values():
            print(student)

    def find_student(self, student_id):
        student = self.students.get(student_id)
        if student:
            print(student)
        else:
            print(f"No student found with ID {student_id}")

    def delete_student(self, student_id):
        if student_id in self.students:
            del self.students[student_id]
            print(f"Student with ID {student_id} deleted.")
        else:
            print(f"No student found with ID {student_id}")

def main():
    sms = StudentManagementSystem()

    while True:
        print("\nStudent Management System")
        print("1. Add Student")
        print("2. List Students")
        print("3. Find Student by ID")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            student_id = input("Enter student ID: ")
            name = input("Enter name: ")
            age = input("Enter age: ")
            grade = input("Enter grade: ")
            student = Student(student_id, name, age, grade)
            sms.add_student(student)

        elif choice == '2':
            sms.list_students()

        elif choice == '3':
            student_id = input("Enter student ID to find: ")
            sms.find_student(student_id)

        elif choice == '4':
            student_id = input("Enter student ID to delete: ")
            sms.delete_student(student_id)

        elif choice == '5':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
