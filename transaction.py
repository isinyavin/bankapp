from decimal import Decimal

from sqlalchemy import Integer, String, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship, backref, mapped_column
from database import Base

class Transaction(Base):

    __tablename__ = "transactions"
    _id = mapped_column(Integer, primary_key=True)
    _amount = mapped_column(Numeric)
    _date = mapped_column(Date)
    _typeof = mapped_column(String)
    _account_id = mapped_column(Integer, ForeignKey('account._account_number')) 

    def __init__(self, amount, date, typeof):
        """Initialize a new Transaction instance."""
        self._amount = Decimal(amount)
        self._date = date
        self._typeof = typeof

    def get_date(self):
        """Returns the full date of the transaction."""
        return self._date

    def get_day(self):
        """Returns the day of the transaction."""
        return self._date.day

    def get_amount(self):
        """Returns the amount of the transaction."""
        return self._amount
    
    def get_type(self):
        """Returns the type of transaction."""
        return self._typeof

    def __str__(self):
        """Returns string representation of instance"""
        formatted_date = self._date.strftime("%Y-%m-%d")
        return f"{formatted_date}, ${self._amount:,.2f}"
    
    def __lt__(self, other):
        """Allows comparison of transactions with date"""
        return self._date < other._date
    
    def __eq__(self, other):
        """Allows comparison of transactions based on date"""
        return self._date == other._date
    

