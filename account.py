from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship, backref, mapped_column
from database import Base

from decimal import Decimal
from transaction import Transaction
from datetime import datetime, date, timedelta
from errors import OverdrawError, TransactionSequenceError
import logging

class Account(Base):

    __tablename__ = "account"
    _bank_id = mapped_column(Integer, ForeignKey("bank._id"))
    _transactions = relationship("Transaction", backref=backref("account"))
    _account_number = mapped_column(Integer, primary_key=True, autoincrement=False)
    _balance = mapped_column(Numeric)
    _type = mapped_column(String)

    __mapper_args__ = {
        'polymorphic_identity':'account',
        'polymorphic_on':_type
    }

    """Represents a generic bank account with functionality to manage transactions."""
    def __init__(self, account_number):
        """Initializes the account instance."""
        self._account_number = account_number
        self._balance = Decimal('0.00')

    def add_transaction(self, amount, date, typeof, session):
        """Adds a new transaction to the account and updates the balance."""
        transaction = Transaction(Decimal(amount), date, typeof)
        self._transactions.append(transaction)
        self._balance += Decimal(amount)
        self._transactions.sort()
        session.add(transaction)
        logging.debug(f"Created transaction: {self._account_number}, {amount}")
        session.commit()


    def can_add_transaction(self, amount, date):
        """Determines if this account can add transactions and raises OverdrawError if not."""
        new_balance = self._balance + Decimal(amount)
        if new_balance < Decimal('0.00'):
            raise OverdrawError()
        if len(self._transactions) > 0:
            latest_transaction_date = max(t.get_date() for t in self._transactions)
            if date < latest_transaction_date:
                raise TransactionSequenceError(latest_date=latest_transaction_date)
        return True

    def print_transactions(self):
        """Prints a list of all transactions sorted by date."""
        for transaction in self._transactions:
            print(transaction)
        
    def get_account_number(self):
        """Getter for the account number"""
        return self._account_number
    
    def get_transactions(self):
        return self._transactions
    
    def _get_last_day_of_month(self):
        if not self._transactions:
            return
        latest_transaction = max(self._transactions)
        first_of_next_month = date(latest_transaction.get_date().year + latest_transaction.get_date().month // 12,
                                   latest_transaction.get_date().month % 12 + 1, 1)

        return first_of_next_month - timedelta(days=1)
    
    def _has_interest_been_applied(self):
        if not self._transactions:
            return False  
        
        last_transaction = max(self._transactions)
        last_transaction_month = last_transaction.get_date().month
        last_transaction_year = last_transaction.get_date().year
        
        for transaction in self._transactions:
            if ((transaction.get_type() == "interest") and 
                transaction.get_date().year == last_transaction_year and 
                transaction.get_date().month == last_transaction_month):
                return True
                
        return False




    










    
    

