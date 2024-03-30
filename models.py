from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from passlib.hash import bcrypt

Base = declarative_base()
engine = create_engine('sqlite:///mydatabase.db')

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.hash(password)

    def check_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class BudgetCategory(Base):
    __tablename__ = 'budget_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    budget_amount = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='budget_categories')
    period = Column(String, nullable=False)
    spent_amount = Column(Float, default=0.0)

    def calculate_spent_amount(self):
        spent_amount = sum(transaction.amount for transaction in self.transactions)
        return spent_amount

class BudgetAccount(Base):
    __tablename__ = 'budget_accounts'

    id = Column(Integer, primary_key=True)
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='budget_accounts')

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'deposit' or 'withdrawal'
    category_id = Column(Integer, ForeignKey('budget_categories.id'))
    category = relationship('BudgetCategory', back_populates='transactions')
    account_id = Column(Integer, ForeignKey('budget_accounts.id'))
    account = relationship('BudgetAccount', back_populates='transactions')

User.budget_categories = relationship('BudgetCategory', order_by=BudgetCategory.id, back_populates='user')
User.budget_accounts = relationship('BudgetAccount', order_by=BudgetAccount.id, back_populates='user')
BudgetCategory.transactions = relationship('Transaction', order_by=Transaction.id, back_populates='category')
BudgetAccount.transactions = relationship('Transaction', order_by=Transaction.id, back_populates='account')

Base.metadata.create_all(engine)
