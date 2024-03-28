from account import Account
from decimal import Decimal
from errors import TransactionLimitError

class Savings(Account):

    __mapper_args__ = {
        'polymorphic_identity':'savings',
    }

    def __init__(self, account_number):
        """Initializes savings account"""
        super().__init__(account_number)

    def can_add_transaction(self, amount, date):
        """Determines if this account can add transactions"""
        if not super().can_add_transaction(amount, date):
            return False
        year_month = date.strftime('%Y-%m')
        same_day_transactions = sum(1 for transaction in self._transactions 
                                if transaction.get_date() == date 
                                and transaction.get_type() == "normal")
        same_month_transactions = sum(1 for transaction in self._transactions 
                                  if transaction.get_date().strftime('%Y-%m') == year_month 
                                  and transaction.get_type() == "normal")
        if same_day_transactions >= 2:
            raise TransactionLimitError(daily=True)
        elif same_month_transactions >= 5:
            raise TransactionLimitError(monthly=True)
        else:
            return True
        
    def apply_interest_and_fees(self, session):
        """Applies interest and fees to the account."""
        if self._has_interest_been_applied():
            raise TransactionLimitError(latest_date = max(self._transactions).get_date())
        last_day = self._get_last_day_of_month() 
        self.add_transaction(self._balance * Decimal('0.0041'), last_day, "interest", session)

    def __str__(self):
        """String representation of the savings account object"""
        return f"Savings#{self._account_number:09d},\tbalance: ${self._balance:,.2f}"