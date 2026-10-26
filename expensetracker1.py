
# Smart Expense Tracker
# A Python command-line expense tracking application

import csv
import os
import tempfile
from datetime import date
from decimal import Decimal, InvalidOperation

FILE_NAME = "expenses.csv"
FIELDNAMES = ["date", "description", "category", "amount"]

expenses = []


def load_expenses():
    """Load expenses from the CSV file."""
    expenses.clear()

    try:
        with open(FILE_NAME, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None or not all(
                field in reader.fieldnames for field in FIELDNAMES
            ):
                raise ValueError("Invalid CSV columns")

            loaded = []

            for row in reader:
                amount = Decimal(row["amount"])
                date.fromisoformat(row["date"])

                if not amount.is_finite() or amount <= 0:
                    raise ValueError("Invalid saved amount")

                loaded.append({
                    "date": row["date"],
                    "description": row["description"],
                    "category": row["category"],
                    "amount": amount
                })

            expenses.extend(loaded)

    except FileNotFoundError:
        # First run: no CSV file exists yet
        pass

    except (ValueError, KeyError, TypeError,
            InvalidOperation, csv.Error, OSError) as error:
        print("Could not load expenses:", error)
        print("Please check the CSV file before continuing.")
        raise SystemExit(1)


def save_expenses():
    """Write expenses to a temporary CSV, then replace the old file."""
    folder = os.path.dirname(os.path.abspath(FILE_NAME))
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            dir=folder,
            prefix=".expenses_",
            suffix=".tmp",
            delete=False
        ) as file:
            temporary_path = file.name
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()

            for expense in expenses:
                writer.writerow({
                    **expense,
                    "amount": str(expense["amount"])
                })

        os.replace(temporary_path, FILE_NAME)

    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.remove(temporary_path)


def show_menu():
    print("\n=== SMART EXPENSE TRACKER ===")
    print("1. Add expense")
    print("2. View expenses")
    print("3. View spending summary")
    print("4. Search by category")
    print("5. Exit")


def add_expense():
    print("\n--- Add New Expense ---")

    expense_date = input(
        "Enter date (YYYY-MM-DD), or press Enter for today: "
    ).strip()

    if not expense_date:
        expense_date = date.today().isoformat()

    try:
        date.fromisoformat(expense_date)
    except ValueError:
        print("Invalid date.")
        return

    description = input("Enter description: ").strip()
    category = input("Enter category: ").strip().title()

    if not description or not category:
        print("Description and category cannot be empty.")
        return

    amount_text = input("Enter amount (S$): ").strip()

    try:
        amount = Decimal(amount_text)

        if not amount.is_finite() or amount <= 0:
            print("Amount must be a positive, finite number.")
            return

        if amount.as_tuple().exponent < -2:
            print("Enter no more than two decimal places.")
            return

        amount = amount.quantize(Decimal("0.01"))

    except InvalidOperation:
        print("Invalid amount. Please enter a number.")
        return

    expense = {
        "date": expense_date,
        "description": description,
        "category": category,
        "amount": amount
    }

    expenses.append(expense)

    try:
        save_expenses()
    except OSError as error:
        expenses.pop()
        print("Could not save expense:", error)
        return

    print("Expense added and saved successfully!")


def view_expenses():
    print("\n--- Expense History ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    for index, expense in enumerate(expenses, start=1):
        print(
            f"{index}. {expense['date']} | "
            f"{expense['description']} | "
            f"{expense['category']} | "
            f"S${expense['amount']:.2f}"
        )


def spending_summary():
    print("\n--- Spending Summary ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    total_spending = Decimal("0.00")
    category_totals = {}

    for expense in expenses:
        amount = expense["amount"]
        category = expense["category"].strip().title()

        total_spending += amount
        category_totals[category] = (
            category_totals.get(category, Decimal("0.00"))
            + amount
        )

    print(f"Total expenses: {len(expenses)}")
    print(f"Total spending: S${total_spending:.2f}")

    print("\nSpending by category:")

    for category, total in sorted(category_totals.items()):
        print(f"{category}: S${total:.2f}")

    highest_category = max(
        category_totals,
        key=category_totals.get
    )

    print("\nHighest spending category:")
    print(
        f"{highest_category} "
        f"(S${category_totals[highest_category]:.2f})"
    )


def search_by_category():
    print("\n--- Search by Category ---")

    search_category = input("Enter category: ").strip().lower()

    if not search_category:
        print("Please enter a category.")
        return

    matches = [
        expense for expense in expenses
        if expense["category"].strip().lower() == search_category
    ]

    if not matches:
        print("No expenses found in this category.")
        return

    total = Decimal("0.00")

    for index, expense in enumerate(matches, start=1):
        print(
            f"{index}. {expense['date']} | "
            f"{expense['description']} | "
            f"S${expense['amount']:.2f}"
        )
        total += expense["amount"]

    print(f"\nCategory total: S${total:.2f}")


def main():
    load_expenses()

    while True:
        show_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            spending_summary()
        elif choice == "4":
            search_by_category()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    main()
