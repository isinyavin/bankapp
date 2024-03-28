from account import Account
from decimal import Decimal
from errors import *

class Checking(Account):

    __mapper_args__ = {
        'polymorphic_identity':'checking',
    }

    def __init__(self, account_number):
        """Initializes checking account."""
        super().__init__(account_number)
        
    def apply_interest_and_fees(self, session):
        """Applies interest and fee calculation on account"""
        if self._has_interest_been_applied():
            raise TransactionLimitError(latest_date = max(self._transactions).get_date())
        last_day = self._get_last_day_of_month()
        self.add_transaction(self._balance * Decimal('0.0008'), last_day, "interest", session)
        #for checking accounts, check overdraft
        if (self._balance < Decimal(100)):
            self.add_transaction(Decimal('-5.44'), last_day, "fees", session)

    def __str__(self):
        """String representation of the account."""
        return f"Checking#{self._account_number:09d},\tbalance: ${self._balance:,.2f}"


    