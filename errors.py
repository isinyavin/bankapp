class OverdrawError(Exception):
    """Exception raised for attempts to overdraw an account."""
    def __init__(self, message="This transaction could not be completed due to an insufficient account balance."):
        self.message = message
        super().__init__(self.message)

class TransactionSequenceError(Exception):
    """Exception raised when a new transaction is out of chronological order."""
    def __init__(self, latest_date, message = ""):
        self.latest_date = latest_date
        self.message = message or f"New transactions must be from {self.latest_date.strftime('%Y-%m-%d')} onward."
        super().__init__(self.message)

class TransactionLimitError(Exception):
    """Exception raised when transaction limits are exceeded."""
    def __init__(self, daily=False, monthly=False, latest_date = None, message = ""):
        self.latest_date = latest_date
        if daily:
            self.message = "This transaction could not be completed because this account already has 2 transactions in this day."
        elif monthly:
            self.message = "This transaction could not be completed because this account already has 5 transactions in this month."
        elif latest_date:
            self.message = f"Cannot apply interest and fees again in the month of {latest_date.strftime('%B')}."
        else:
            self.message = "Transaction limit error."
        super().__init__(message)
        self.daily = daily
        self.monthly = monthly