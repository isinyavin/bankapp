
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine


from database import Base
from decimal import Decimal, InvalidOperation
from bank import Bank
from datetime import datetime
from account import Account
from errors import OverdrawError, TransactionSequenceError, TransactionLimitError
import sys
import logging


class BankCLI:
    """Class representing the command line interface for the banking application."""
    def __init__(self):
        """Initialize the CLI with a Bank instance and no selected account."""
        self._session = Session()  
        self._bank = self._session.query(Bank).first()

        if not self._bank:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")

        self._selected_account = None
        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._interest_and_fees,
            "7": self._quit
        }
    
    def _display_menu(self):
        if self._selected_account:
            account_info = str(self._selected_account)
        else:
            account_info = "None"
        print(
f"""--------------------------------
Currently selected account: {account_info}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit""")
        
    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print("{0} is not a valid choice".format(choice))
    
    def _open_account(self):
        account_type = input("Type of account? (checking/savings)\n>")
        if account_type in ["checking", "savings"]:
            self._bank.open_account(account_type, self._session)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            print("Invalid account type.")

    def _summary(self):
        self._bank.print_summary()

    def _select_account(self):
        account_number = input("Enter account number\n>")
        self._selected_account = self._bank.get_account(account_number)

    def _add_transaction(self):
        try:
            while True:
                amount_str = input("Amount?\n>")
                try:
                    amount = Decimal(amount_str)
                    break  
                except InvalidOperation:
                    print("Please try again with a valid dollar amount.")

            while True:
                date_str = input("Date? (YYYY-MM-DD)\n>")
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    break  
                except ValueError:
                    print("Please try again with a valid date in the format YYYY-MM-DD.")

            self._bank.add_transaction(self._selected_account, amount, date, self._session)

        except AttributeError:
            print("This command requires that you first select an account.")
        except OverdrawError as e:
            print(e.message)
        except TransactionLimitError as e:
            print(e.message)
        except TransactionSequenceError as e:
            print(e.message)

    def _list_transactions(self):
        try:
            self._bank.list_transactions(self._selected_account)
        except AttributeError:
            print("This command requires that you first select an account.")

    def _interest_and_fees(self):
        try:
            self._bank.apply_interest_and_fees(self._selected_account, self._session)
            logging.debug("Triggered interest and fees")
            self._session.commit()
            logging.debug("Saved to bank.db")
        except AttributeError:
            print("This command requires that you first select an account.")
        except TransactionLimitError as e:
            print(e.message)
            
        
    def _quit(self):
        sys.exit(0)

if __name__ == "__main__":

    engine = create_engine(f"sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine) 

    logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
        BankCLI().run()
    except Exception as e:
        error_message = str(e).replace('\n', '\\n')
        logging.error(f"{type(e).__name__}: '{error_message}'")
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        sys.exit(0)



