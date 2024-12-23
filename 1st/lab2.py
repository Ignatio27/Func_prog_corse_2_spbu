from functools import reduce
users = [
    {"name": "Alice", "expenses": [100, 50, 75, 200]},
    {"name": "Bob", "expenses": [50, 75, 80, 100]},
    {"name": "Charlie", "expenses": [200, 300, 50, 150]},
    {"name": "David", "expenses": [100, 200, 300, 400]},
    {"name": "Eve", "expenses": [150, 60, 90, 120]},
    {"name": "Frank", "expenses": [80, 200, 150, 100]},
    {"name": "Grace", "expenses": [300, 400, 250, 500]},
    {"name": "Hannah", "expenses": [120, 60, 70, 90]},
    {"name": "Ivy", "expenses": [500, 300, 250, 150]},
    {"name": "Jack", "expenses": [75, 100, 50, 150]},
    {"name": "Kim", "expenses": [100, 90, 80, 60]},
    {"name": "Liam", "expenses": [120, 200, 180, 160]},
    {"name": "Mia", "expenses": [400, 500, 450, 300]},
    {"name": "Noah", "expenses": [90, 80, 100, 150]},
    {"name": "Olivia", "expenses": [60, 90, 110, 140]},
    {"name": "Paul", "expenses": [200, 300, 150, 100]},
    {"name": "Quincy", "expenses": [100, 120, 130, 140]},
    {"name": "Rachel", "expenses": [90, 60, 50, 80]},
    {"name": "Sam", "expenses": [500, 400, 350, 600]},
    {"name": "Tina", "expenses": [150, 200, 300, 250]},
]

calculate_total_expenses = lambda users: reduce(
    lambda acc, user: acc + user["total_expenses"],
    users,
    0
)

calculate_expenses = lambda users: list(
    map(
        lambda user: {**user, "total_expenses": sum(user["expenses"])},
        users
    )
)

#1
filtered_users = list(filter(lambda user: any(expence > 300 for expence in user['expenses']), users))

print(f"Юзеры с хотя бы одним расходом больше 300 {filtered_users}")
print("-" * 100)

#2
users_with_total_expenses = list(map(lambda user: {**user, 'total_expenses': sum(user['expenses'])}, users))
print(f"Юзеры с общим расходом {users_with_total_expenses}")

users_with_expenses = calculate_expenses(filtered_users)
print(f'Общий расход: {users_with_expenses}')
print("-" * 100)

#3
filtered_users_with_total_expenses = list(map(lambda user: {**user, 'total_expenses': sum(user['expenses'])}, filtered_users))

print(f"Фильтрованные юзеры с общим расходом {users_with_total_expenses}")

total_expenses = calculate_total_expenses(users_with_expenses)
print(f'Общий расход: {total_expenses}')
print("-" * 100)
