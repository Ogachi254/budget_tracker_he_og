from models import User, BudgetCategory, BudgetAccount, Transaction, engine, Base
from sqlalchemy.orm import sessionmaker
from passlib.hash import bcrypt
import getpass

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

current_user = None 

def create_user(name, age, username, password):
    new_user = User(name=name, age=age, username=username)
    new_user.set_password(password)
    session.add(new_user)
    session.commit()
    print("User created successfully.")

def login():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    user = session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        print("Login successful.")
        return user
    else:
        print("Invalid username or password.")
        return None
    
def logout():
    print("Logout successful.")

def create_budget_category(user_id, name, budget_amount, period):
    new_category = BudgetCategory(user_id=user_id, name=name, budget_amount=budget_amount, period=period)
    session.add(new_category)
    session.commit()
    print("Budget category created successfully.")

def view_budget_categories(user_id):
    categories = session.query(BudgetCategory).filter_by(user_id=user_id).all()
    if categories:
        print("Budget Categories:")
        for category in categories:
            print(f"ID: {category.id}, Name: {category.name}, Budget Amount: {category.budget_amount}, Period: {category.period}")
    else:
        print("No budget categories found for the user.")

def create_budget_account(user_id):
    new_account = BudgetAccount(user_id=user_id)
    session.add(new_account)
    session.commit()
    print("Budget account created successfully.")

def make_transaction(user_id, amount, transaction_type, category_id):
    user_accounts = session.query(BudgetAccount).filter_by(user_id=user_id).all()
    if not user_accounts:
        print("No accounts found for the user. Please create an account first.")
        return

    print("Available accounts for user:")
    for account in user_accounts:
        print(f"{account.id}. Balance: {account.balance}")
    
    account_ids = [account.id for account in user_accounts]
    print("Account IDs:", account_ids)  # Debug print
    
    while True:
        account_id = int(input("Choose account ID: "))
        if account_id in account_ids:
            break
        else:
            print("Invalid account ID. Please choose from the available accounts.")

    transaction = Transaction(amount=amount, transaction_type=transaction_type, category_id=category_id, account_id=account_id)
    session.add(transaction)

    if transaction_type == 'deposit':
        user_accounts[0].balance += amount  
    elif transaction_type == 'withdrawal':
        user_accounts[0].balance -= amount  

    session.commit()
    print("Transaction made successfully.")

def update_transaction(user_id, transaction_id, amount):
    transaction = session.query(Transaction).filter_by(id=transaction_id).first()
    if transaction:
        if transaction.account.user_id == user_id:
            old_amount = transaction.amount
            transaction.amount = amount

            account = transaction.account
            if transaction.transaction_type == 'deposit':
                account.balance += (amount - old_amount)
            elif transaction.transaction_type == 'withdrawal':
                account.balance -= (amount - old_amount)

            session.commit()
            print("Transaction updated successfully.")
        else:
            print("You don't have access to update this transaction.")
    else:
        print("Transaction not found.")

def view_transactions(user_id):
    transactions = session.query(Transaction).join(BudgetCategory).filter(BudgetCategory.user_id == user_id).all()
    if transactions:
        print("Transactions:")
        for transaction in transactions:
            print(f"ID: {transaction.id}, Amount: {transaction.amount}, Type: {transaction.transaction_type}, Category: {transaction.category.name}")
    else:
        print("No transactions found.")

def transfer_funds(user_id, from_category_id, to_category_id, amount):
    from_category = session.query(BudgetCategory).filter_by(id=from_category_id).first()
    to_category = session.query(BudgetCategory).filter_by(id=to_category_id).first()

    if not from_category or not to_category:
        print("One or both of the categories do not exist.")
        return

    from_account = session.query(BudgetAccount).filter_by(user_id=user_id).filter_by(id=from_category.account_id).first()
    to_account = session.query(BudgetAccount).filter_by(user_id=user_id).filter_by(id=to_category.account_id).first()

    if not from_account or not to_account:
        print("One or both of the accounts do not exist.")
        return

    if from_account.balance < amount:
        print("Insufficient funds in the source category.")
        return

    from_account.balance -= amount
    to_account.balance += amount

    session.commit()
    print("Funds transferred successfully.")

def transfer_funds_within_categories(user_id, from_category_id, to_category_id, amount):
    from_category = session.query(BudgetCategory).filter_by(id=from_category_id, user_id=user_id).first()
    to_category = session.query(BudgetCategory).filter_by(id=to_category_id, user_id=user_id).first()

    if not from_category or not to_category:
        print("One or both of the categories do not exist.")
        return

    if from_category.id == to_category.id:
        print("Source and destination categories cannot be the same.")
        return

    spent_amount = from_category.calculate_spent_amount()
    if spent_amount + amount > from_category.budget_amount:
        print("Transfer amount exceeds the budget of the source category.")
        return

    from_category.spent_amount = spent_amount + amount
    to_category.spent_amount = to_category.calculate_spent_amount() - amount

    session.commit()
    print("Funds transferred successfully between budget categories.")

def transfer_funds_from_account(user_id, from_account_id, to_category_id, amount):
    from_account = session.query(BudgetAccount).filter_by(id=from_account_id, user_id=user_id).first()
    to_category = session.query(BudgetCategory).filter_by(id=to_category_id, user_id=user_id).first()

    if not from_account or not to_category:
        print("One or both of the account or category do not exist.")
        return

    if from_account.balance < amount:
        print("Insufficient funds in the source account.")
        return

    if to_category.spent_amount + amount > to_category.budget_amount:
        print("Transfer amount exceeds the budget of the destination category.")
        return

    from_account.balance -= amount
    to_category.spent_amount += amount

    session.commit()
    print("Funds transferred successfully from account to budget category.")

def transfer_funds_to_account(user_id, from_category_id, to_account_id, amount):
    from_category = session.query(BudgetCategory).filter_by(id=from_category_id, user_id=user_id).first()
    to_account = session.query(BudgetAccount).filter_by(id=to_account_id, user_id=user_id).first()

    if not from_category or not to_account:
        print("One or both of the category or account do not exist.")
        return

    if from_category.spent_amount < amount:
        print("Insufficient funds in the source category.")
        return

    from_category.spent_amount -= amount
    to_account.balance += amount

    session.commit()
    print("Funds transferred successfully from budget category to account.")

def delete_budget_category(user_id, category_id):
    category = session.query(BudgetCategory).filter_by(id=category_id, user_id=user_id).first()
    if category:
        session.delete(category)
        session.commit()
        print("Budget category deleted successfully.")
    else:
        print("Budget category not found.")

def update_budget_category(user_id, category_id, name=None, budget_amount=None, period=None):
    category = session.query(BudgetCategory).filter_by(id=category_id, user_id=user_id).first()
    if category:
        if name:
            category.name = name
        if budget_amount is not None:
            category.budget_amount = budget_amount
        if period:
            category.period = period
        session.commit()
        print("Budget category updated successfully.")
    else:
        print("Budget category not found.")

def delete_transaction_outside_main(user_id, transaction_id):
    transaction = session.query(Transaction).filter_by(id=transaction_id).join(BudgetCategory).filter(BudgetCategory.user_id == user_id).first()
    if transaction:
        session.delete(transaction)
        session.commit()
        print("Transaction deleted successfully.")
    else:
        print("Transaction not found.")

def delete_transaction(user_id, transaction_id):
    transaction = session.query(Transaction).filter_by(id=transaction_id).join(BudgetCategory).filter(BudgetCategory.user_id == user_id).first()
    if transaction:
        session.delete(transaction)
        session.commit()
        print("Transaction deleted successfully.")
    else:
        print("Transaction not found.")

def view_account_balances(user_id):
    accounts = session.query(BudgetAccount).filter_by(user_id=user_id).all()
    if accounts:
        print("Account Balances:")
        for account in accounts:
            print(f"Account ID: {account.id}, Balance: {account.balance}")
    else:
        print("No accounts found for the user.")

def view_transactions(user_id):
    transactions = session.query(Transaction).join(BudgetCategory).filter(BudgetCategory.user_id == user_id).all()
    if transactions:
        print("Transactions:")
        for transaction in transactions:
            print(f"ID: {transaction.id}, Amount: {transaction.amount}, Type: {transaction.transaction_type}, Category: {transaction.category.name}")
    else:
        print("No transactions found.")

def main():
    global current_user
    print("Welcome to Budget CLI App!")

    while True:
        print("\nAvailable commands:")
        print("1. Register")
        print("2. Login")
        print("3. Logout")
        print("4. Create Budget Category")
        print("5. Create Budget Account")
        print("6. Deposit Funds")
        print("7. Make Transaction")
        print("8. Update Transaction")
        print("9. Transfer Funds")
        print("10. View Budget Categories")
        print("11. Delete Budget Category")
        print("12. Update Budget Category")
        print("13. Delete Transaction")
        print("14. View Account Balances")  
        print("15. View Transactions")     
        print("16. Exit")


        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter name: ")
            age = int(input("Enter age: "))
            username = input("Enter username: ")
            password = input("Enter password: ")
            create_user(name, age, username, password)
        elif choice == '2':
            if not current_user:
                current_user = login()
        elif choice == '2':
            if not current_user:
                username = input("Enter username: ")
                password = input("Enter password: ")
                current_user = login(username, password)
        elif choice == '3':
            if current_user:
                logout()
                current_user = None
            else:
                print("No user logged in.")
        elif choice == '4':
            if current_user:
                name = input("Enter category name: ")
                budget_amount = float(input("Enter budget amount: "))
                period = input("Enter period: ")
                create_budget_category(current_user.id, name, budget_amount, period)
            else:
                print("No user logged in.")
        elif choice == '5':
            if current_user:
                create_budget_account(current_user.id)
            else:
                print("No user logged in.")
        elif choice == '6':
            if current_user:
                print("Available accounts for user:")
                accounts = session.query(BudgetAccount).filter_by(user_id=current_user.id).all()
                for account in accounts:
                    print(f"{account.id}. Balance: {account.balance}")
                account_id = int(input("Choose account ID: "))
                amount = float(input("Enter amount to deposit: "))
                if amount > 0:
                    account = session.query(BudgetAccount).filter_by(id=account_id).first()
                    account.balance += amount
                    session.commit()
                    print("Funds deposited successfully.")
                else:
                    print("Invalid amount.")
            else:
                print("No user logged in.")
        elif choice == '7':
            if current_user:
                print("Available categories for user:")
                categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                for category in categories:
                    print(f"{category.id}. {category.name}")
                category_id = int(input("Choose category ID to make transaction from: "))
                amount = float(input("Enter amount: "))
                transaction_type = input("Enter transaction type (deposit/withdrawal): ")
                if transaction_type in ['deposit', 'withdrawal']:
                    make_transaction(current_user.id, amount, transaction_type, category_id)
                else:
                    print("Invalid transaction type.")
            else:
                print("No user logged in.")
        elif choice == '8':
            if current_user:
                print("Available transactions for user:")
                transactions = session.query(Transaction).join(BudgetCategory).filter(BudgetCategory.user_id == current_user.id).all()
                if transactions:
                    for transaction in transactions:
                        print(f"ID: {transaction.id}, Amount: {transaction.amount}, Type: {transaction.transaction_type}, Category: {transaction.category.name}")
                    transaction_id = int(input("Enter transaction ID to update: "))
                    transaction = session.query(Transaction).get(transaction_id)
                    if transaction:
                        print(f"Transaction details: Amount: {transaction.amount}, Type: {transaction.transaction_type}, Category: {transaction.category.name}")
                        amount = float(input("Enter new amount: "))
                        update_transaction(current_user.id, transaction_id, amount)
                    else:
                        print("Transaction not found.")
                else:
                    print("No transactions found.")
            else:
                print("No user logged in.")
        elif choice == '9':
            if current_user:
                print("Transfer Options:")
                print("1. Transfer funds between budget categories")
                print("2. Transfer funds from account to budget category")
                print("3. Transfer funds from budget category to account")
                transfer_option = input("Enter transfer option: ")

                if transfer_option == '1':
                    print("Available budget categories for user:")
                    categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                    for category in categories:
                        spent_amount = category.calculate_spent_amount()
                        remaining_budget = category.budget_amount - spent_amount
                        print(f"{category.id}. {category.name} - Budget: {category.budget_amount}, Remaining: {remaining_budget}")
                    from_category_id = int(input("Enter source category ID: "))
                    to_category_id = int(input("Enter destination category ID: "))
                    amount = float(input("Enter amount to transfer: "))
                    transfer_funds_within_categories(current_user.id, from_category_id, to_category_id, amount)

                elif transfer_option == '2':
                    print("Available accounts for user:")
                    accounts = session.query(BudgetAccount).filter_by(user_id=current_user.id).all()
                    for account in accounts:
                        print(f"{account.id}. Balance: {account.balance}")

                    from_account_id = int(input("Enter source account ID: "))

                    print("Available budget categories for user:")
                    categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                    for category in categories:
                        print(f"{category.id}. {category.name} - Budget: {category.budget_amount}, Remaining: {category.budget_amount - category.calculate_spent_amount()}")

                    to_category_id = int(input("Enter destination category ID: "))

                    amount = float(input("Enter amount to transfer: "))

                    transfer_funds_from_account(current_user.id, from_account_id, to_category_id, amount)

                elif transfer_option == '3':
                    print("Available budget categories for user:")
                    categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                    for category in categories:
                        spent_amount = category.calculate_spent_amount()
                        remaining_budget = category.budget_amount - spent_amount
                        print(f"{category.id}. {category.name} - Budget: {category.budget_amount}, Remaining: {remaining_budget}")
                    from_category_id = int(input("Enter source category ID: "))
                    print("Available accounts for user:")
                    accounts = session.query(BudgetAccount).filter_by(user_id=current_user.id).all()
                    for account in accounts:
                        print(f"{account.id}. Balance: {account.balance}")
                    to_account_id = int(input("Enter destination account ID: "))
                    amount = float(input("Enter amount to transfer: "))
                    transfer_funds_to_account(current_user.id, from_category_id, to_account_id, amount)

                else:
                    print("Invalid transfer option.")
            else:
                print("No user logged in.")

        elif choice == '10':
            if current_user:
                view_budget_categories(current_user.id)
            else:
                print("No user logged in.")

        elif choice == '11':
            if current_user:
                print("Available budget categories for user:")
                categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                for category in categories:
                    print(f"{category.id}. {category.name}")
                category_id = int(input("Enter category ID to delete: "))
                delete_budget_category(current_user.id, category_id)
            else:
                print("No user logged in.")

        elif choice == '12':
            if current_user:
                print("Available budget categories for user:")
                categories = session.query(BudgetCategory).filter_by(user_id=current_user.id).all()
                for category in categories:
                    print(f"{category.id}. {category.name}")
                category_id = int(input("Enter category ID to update: "))
                name = input("Enter new name (press Enter to keep the same): ")
                budget_amount = float(input("Enter new budget amount (press Enter to keep the same): ") or -1)
                period = input("Enter new period (press Enter to keep the same): ")
                update_budget_category(current_user.id, category_id, name, budget_amount, period)
            else:
                print("No user logged in.")

        elif choice == '13':
            if current_user:
                print("Available transactions for user:")
                transactions = session.query(Transaction).join(BudgetCategory).filter(BudgetCategory.user_id == current_user.id).all()
                if transactions:
                    for transaction in transactions:
                        print(f"ID: {transaction.id}, Amount: {transaction.amount}, Type: {transaction.transaction_type}, Category: {transaction.category.name}")
                    transaction_id = int(input("Enter transaction ID to delete: "))
                    delete_transaction(current_user.id, transaction_id)
                else:
                    print("No transactions found.")
            else:
                print("No user logged in.")

        elif choice == '14':
            if current_user:
                view_account_balances(current_user.id) 
            else:
                print("No user logged in.")
        elif choice == '15':
            if current_user:
                view_transactions(current_user.id) 
            else:
                print("No user logged in.")
        elif choice == '16':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            
if __name__ == "__main__":
    current_user = None
    main()

                                                                                                               