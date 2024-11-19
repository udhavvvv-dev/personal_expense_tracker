import json
import os
import matplotlib.pyplot as plt
import mplcursors
import pandas as pd
from datetime import datetime

# File paths
DATA_FILE = "data.json"
HISTORY_FILE = "history.json"

# Load or initialize data
def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {"expenses": [], "budgets": {}}
        with open(DATA_FILE, "w") as file:
            json.dump(default_data, file, indent=4)
        return default_data
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Error: The JSON file is corrupt. Resetting file.")
        default_data = {"expenses": [], "budgets": {}}
        with open(DATA_FILE, "w") as file:
            json.dump(default_data, file, indent=4)
        return default_data

# Save data to file
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Save history to file (For past month data)
def save_history(data):
    with open(HISTORY_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Add expense
def add_expense(date, category, amount):
    data = load_data()
    data["expenses"].append({"date": date, "category": category, "amount": amount})
    save_data(data)
    print(f"\nExpense Added: {category} - {amount} on {date}")
    check_budget()  # Check for budget alert after adding expense

# Set budget with a name
def set_budget():
    data = load_data()
    budget_name = input("Enter a name for this budget: ")
    try:
        amount = float(input("Enter your budget amount: "))
        data["budgets"][budget_name] = {"amount": amount, "expenses": []}
        save_data(data)
        print(f"\nBudget '{budget_name}' set to {amount}")
    except ValueError:
        print("Invalid budget amount. Please try again.")

# Analyze expenses
def analyze_expenses():
    data = load_data()
    print("\n1. Current Table Analysis")
    print("2. Old Table Analysis")
    choice = input("Choose an option (1/2): ")

    if choice == "1":
        analyze_current_expenses(data)
    elif choice == "2":
        if not data["budgets"]:
            print("No old budgets available for analysis.")
            return
        print("\nAvailable Budgets:")
        for idx, budget_name in enumerate(data["budgets"].keys(), start=1):
            print(f"{idx}. {budget_name}")
        try:
            selected = int(input("Select a budget by number: "))
            budget_name = list(data["budgets"].keys())[selected - 1]
            analyze_old_expenses(data["budgets"][budget_name], budget_name)
        except (IndexError, ValueError):
            print("Invalid selection. Returning to menu.")
    else:
        print("Invalid choice. Returning to menu.")

# Current expenses analysis
def analyze_current_expenses(data):
    expenses = data["expenses"]
    if not expenses:
        print("No current expenses to analyze.")
        return
    plot_expenses(expenses, "Current Expenses")

# Old expenses analysis
def analyze_old_expenses(budget_data, budget_name):
    expenses = budget_data["expenses"]
    if not expenses:
        print(f"No expenses recorded under the budget '{budget_name}'.")
        return
    plot_expenses(expenses, f"Expenses for Budget '{budget_name}'")

# Plot expenses
def plot_expenses(expenses, title):
    total_expenses = sum(expense["amount"] for expense in expenses)
    category_totals = {}
    for expense in expenses:
        category_totals[expense["category"]] = category_totals.get(expense["category"], 0) + expense["amount"]

    print(f"\nTotal Expenses: {total_expenses}")
    print("Expenses by Category:")

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(category_totals.values(), labels=category_totals.keys(),
                                      autopct="%1.1f%%", startangle=90)
    ax.axis('equal')
    plt.title(title)
    plt.show()

# Display spending table
def display_spending_table(option):
    data = load_data()
    if option == "1":
        print("\nCurrent Spending Table")
        expenses = data["expenses"]
        budget = "N/A"
    elif option == "2":
        if not data["budgets"]:
            print("No old budgets available to display.")
            return
        print("\nAvailable Budgets:")
        for idx, budget_name in enumerate(data["budgets"].keys(), start=1):
            print(f"{idx}. {budget_name}")
        try:
            selected = int(input("Select a budget by number: "))
            budget_name = list(data["budgets"].keys())[selected - 1]
            expenses = data["budgets"][budget_name]["expenses"]
            budget = data["budgets"][budget_name]["amount"]
        except (IndexError, ValueError):
            print("Invalid selection. Returning to menu.")
            return
    else:
        print("Invalid option. Returning to menu.")
        return

    if not expenses:
        print("No expenses to display.")
        return

    df = pd.DataFrame(expenses)
    df.rename(columns={"date": "Date", "category": "Category", "amount": "Amount"}, inplace=True)
    print(f"\nBudget: {budget}\n")
    print(df.to_string(index=False))
    input("\nPress Enter to return to the menu.")

# Budget alerts
def check_budget():
    data = load_data()
    total_expenses = sum(expense["amount"] for expense in data["expenses"])
    for budget_name, budget in data["budgets"].items():
        if total_expenses > budget["amount"]:
            print(f"❌ Alert: Total expenses exceeded the budget '{budget_name}'.")

# Main Menu
def print_heading():
    print("\n" + "=" * 50)
    print("     PERSONAL EXPENSE TRACKER")
    print("=" * 50)

def main():
    while True:
        print_heading()
        print("1. Add Expense")
        print("2. Set Budget")
        print("3. Analyze Expenses")
        print("4. Display Spending Table")
        print("5. Exit")

        choice = input("\nChoose an option (1-5): ")
        if choice == "1":
            date = input("Enter date (YYYY-MM-DD): ")
            category = input("Enter category: ")
            try:
                amount = float(input("Enter amount: "))
                add_expense(date, category, amount)
            except ValueError:
                print("Invalid amount. Please try again.")
        elif choice == "2":
            set_budget()
        elif choice == "3":
            analyze_expenses()
        elif choice == "4":
            print("1. Current Spending Table")
            print("2. Old Spending Table")
            option = input("Choose option (1/2): ")
            display_spending_table(option)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
