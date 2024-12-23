from functools import reduce
students = [
    {"name": "Alice", "age": 20, "grades": [85, 90, 88, 92]},
    {"name": "Bob", "age": 22, "grades": [78, 89, 76, 85]},
    {"name": "Charlie", "age": 21, "grades": [92, 95, 88, 94]},
    {"name": "David", "age": 23, "grades": [65, 75, 70, 68]},
    {"name": "Eve", "age": 20, "grades": [88, 91, 87, 90]},
    {"name": "Frank", "age": 22, "grades": [72, 85, 80, 77]},
    {"name": "Grace", "age": 21, "grades": [93, 90, 89, 92]},
    {"name": "Hannah", "age": 23, "grades": [80, 85, 88, 84]},
    {"name": "Ivy", "age": 19, "grades": [95, 97, 93, 96]},
    {"name": "Jack", "age": 24, "grades": [60, 65, 62, 68]},
    {"name": "Kim", "age": 20, "grades": [89, 91, 87, 92]},
    {"name": "Liam", "age": 22, "grades": [79, 82, 85, 80]},
    {"name": "Mia", "age": 21, "grades": [91, 92, 93, 94]},
    {"name": "Noah", "age": 23, "grades": [67, 72, 70, 68]},
    {"name": "Olivia", "age": 20, "grades": [87, 89, 85, 88]},
    {"name": "Paul", "age": 22, "grades": [82, 85, 79, 83]},
    {"name": "Quincy", "age": 21, "grades": [90, 92, 89, 91]},
    {"name": "Rachel", "age": 23, "grades": [75, 80, 78, 82]},
    {"name": "Sam", "age": 19, "grades": [98, 95, 96, 99]},
    {"name": "Tina", "age": 24, "grades": [63, 68, 65, 66]},
]

#1
age_filter = 21
filtered_students = list(filter(lambda student: student['age'] == age_filter, students))
print(f"Студенты в возрасте {age_filter} год: {filtered_students}")
print("-" * 100)

#2.1
calculate_average = lambda grades: sum(grades) / len(grades)

students_with_averages = list(map(lambda student: {**student, 'average': calculate_average(student['grades'])}, students))
print("Студенты со средними баллами:", students_with_averages)
print("-" * 100)

#2.2
all_averages = list(map(lambda student: student['average'], students_with_averages))

overall_average = reduce(lambda acc, avg: acc + avg, all_averages) / len(all_averages)
print(f"Общий средний балл: {overall_average:.2f}")
print("-" * 100)

#3
top_student = reduce(lambda best, student: student if student['average'] > best['average'] else best, students_with_averages)
print(f"Студент с самым высоким средним баллом: {top_student}")
