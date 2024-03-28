from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref, mapped_column
from database import Base

from account import Account
from checking_account import Checking
from savings_account import Savings
import pickle
import logging


class Bank(Base):
    """A class to manage bank accounts and transactions."""

    __tablename__ = "bank"
    _id = mapped_column(Integer, primary_key=True)
    _number_accounts_opened = mapped_column(Integer)
    _accounts = relationship("Account")

    def __init__(self):
        """Initializes the bank instance"""
        self._number_accounts_opened = 0

    def get_accounts(self):
        return self._accounts

    def open_account(self, account_type, session):
        """Open a new account of a specified type ('checking' or 'savings')."""
        self._number_accounts_opened += 1
        if (account_type == "checking"):
            account = Checking(self._number_accounts_opened)
        if (account_type == "savings"):
            account = Savings(self._number_accounts_opened)
        self._accounts.append(account)
        session.add(account)
        logging.debug(f"Created account: {account.get_account_number()}")
        return account

    def print_summary(self):
        """Print a summary of all accounts and their current balances."""
        for account in self._accounts:
            print(account)

    def get_account(self, account_number):
        """Retrieve an account by its number. """
        account_number = int(account_number)
        for account in self._accounts: 
            if account.get_account_number() == account_number:
                return account

    def add_transaction(self, account, amount, date, session):
        """Attempt to add a transaction to an account."""
        if account.can_add_transaction(amount, date):
            account.add_transaction(amount, date, "normal", session)
            logging.debug("Saved to bank.db")
        else:
            pass
    
    def list_transactions(self, account):
        """Print all the transactions for the account."""
        account.print_transactions()

    def apply_interest_and_fees(self, account, session):
        """Apply interest and fees to an account."""
        account.apply_interest_and_fees(session)

