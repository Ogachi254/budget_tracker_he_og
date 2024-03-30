### Budget Management CLI Application

This CLI (Command Line Interface) application is designed to help users manage their budgets efficiently. Users can register, log in, create budget categories, accounts, make transactions, transfer funds between categories and accounts, view budget categories, account balances, and transaction history.
## Features
User Management: Users can register and log in securely to manage their budgets.
Budget Categories: Users can create budget categories with specified amounts and periods.
Accounts: Users can create budget accounts for managing their finances.
Transactions: Users can make transactions (deposits or withdrawals) and view transaction history.
Transfer Funds: Users can transfer funds between budget categories and accounts.
Update and Delete: Users can update and delete budget categories, transactions, and view account balances.

## Requirements

Python 3.x
SQLAlchemy
Passlib

## Installation

Clone or download the repository to your local machine.
Install the required Python packages:

pip install sqlalchemy passlib

Run the main.py file to start the CLI application:
css
python main.py

## Usage

Upon running the application, you will be presented with a menu of options:

Register: Register as a new user.
Login: Log in to an existing account.
Logout: Logout from the current session.
Create Budget Category: Create a new budget category.
Create Budget Account: Create a new budget account.
Deposit Funds: Deposit funds into an account.
Make Transaction: Make a transaction (deposit or withdrawal) from a budget category.
Update Transaction: Update a transaction amount.
Transfer Funds: Transfer funds between categories or accounts.
View Budget Categories: View all budget categories.
Delete Budget Category: Delete a budget category.
Update Budget Category: Update details of a budget category.
Delete Transaction: Delete a transaction.
View Account Balances: View balances of all accounts.
View Transactions: View transaction history.
Exit: Exit the application.


## Acknowledgements
This application is inspired by personal finance management needs.
