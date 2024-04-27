
#Developed and tested in MacOS
from megawidgets import AccountListFrame, TransactionListFrame, OpenAccountFrame, AddTransactionFrame
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine
from database import Base
from bank import Bank
from errors import TransactionLimitError
import sys
import logging
import tkinter as tk
from tkinter import messagebox, font, ttk

def handle_exception(exc_value):
    error_message = f"An unexpected error occurred: {exc_value}"
    messagebox.showerror("Error", error_message)
    sys.exit(0)

class BankGUI:
    """Main driver for Bank user interface"""
    def __init__(self):

        #global selected account variable
        self._selected_account = None
        #sets up the main window and general characteristics
        self._window = tk.Tk()
        self._window.title("Bank")
        self._window.geometry("500x500") 
        self._window.configure(bg='#f0f0f0')
        self._top_frame = tk.Frame(self._window, bg = '#f0f0f0')
        self._top_frame.pack(side=tk.TOP, fill=tk.X)
        my_font = font.Font(family="Helvetica", size=24, weight="bold")
        self._logo_label = tk.Label(self._top_frame, text="Bank", font=my_font, bg = '#f0f0f0', fg='black')
        self._logo_label.pack(side=tk.LEFT, padx=10)

        #style
        self._style = ttk.Style(self._window)
        self._style.theme_use('default')
        
        #sets up logo
        self._logo_image = tk.PhotoImage(file="bank-flat.png") 
        self._logo_image = self._logo_image.subsample(7, 7)
        self._logo_label = tk.Label(self._top_frame, image=self._logo_image, bg= '#f0f0f0')
        self._logo_label.image = self._logo_image 
        self._logo_label.pack(side=tk.LEFT, padx=10)

        #sets up the session and retrieves the bank
        self._session = Session()
        self._bank = self._session.query(Bank).first()
        if not self._bank:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")

        self._session.add(self._bank)
        self._session.commit()

        self._button_frame = tk.Frame(self._window, bg='#f0f0f0') 
        self._button_frame.pack(side=tk.TOP, fill=tk.X)

        #open account button
        self._open_account_button = tk.Button(self._button_frame, text="Open Account", command=self._open_account, bg='white', fg='black', highlightbackground='#f0f0f0') 
        self._open_account_button.pack(side=tk.LEFT)

        #add transaction button
        self._add_transaction_button = tk.Button(self._button_frame, text="Add Transaction", command=self._add_transaction, bg='white', fg='black', highlightbackground='#f0f0f0')  
        self._add_transaction_button.pack(side=tk.LEFT)

        #add interest/fees button
        self._apply_interest_fees_button = tk.Button(self._button_frame, text="Interest and Fees", command=self._apply_interest_fees, bg='white', fg='black', highlightbackground='#f0f0f0')  
        self._apply_interest_fees_button.pack(side=tk.LEFT)

        #transaction list frame
        self._transaction_list_frame = None
        self._transaction_list_frame = TransactionListFrame(self._window, self._session, self._bank)

        self._open_account_frame = None
        self._add_transaction_frame = None
        self._account_list_frame = AccountListFrame(self._window, self._session, self._bank, self._on_account_selected)
        self._account_list_frame.pack(side=tk.TOP, fill=tk.X)
        self._transaction_list_frame.pack(side=tk.TOP, fill=tk.X, after=self._account_list_frame)
        self._transaction_list_frame.refresh()

        self._window.mainloop()


    #method to activate the open account window
    def _open_account(self):
        if self._open_account_frame is not None:
            self._open_account_frame.destroy()

        if self._add_transaction_frame is not None:
            self._add_transaction_frame.destroy()
        
        self._open_account_frame = OpenAccountFrame(self._window, self._session, self._bank, self._account_list_frame)
        self._open_account_frame.pack(side=tk.TOP, fill=tk.X, after=self._button_frame)
        self._account_list_frame.refresh()

    #method to activate the add transaction window. 
    def _add_transaction(self):
        if self._add_transaction_frame is not None:
            self._add_transaction_frame.destroy()
            self._add_transaction_frame = None

        if self._open_account_frame is not None:
            self._open_account_frame.destroy()

        if self._selected_account == None:
            messagebox.showwarning("Error", "This command requires that you first select an account.")
        else:
            self._add_transaction_frame = AddTransactionFrame(self._window, self._session, self._bank, self._selected_account, self._account_list_frame, self._transaction_list_frame)
            self._add_transaction_frame.pack(side=tk.TOP, fill=tk.X, after=self._button_frame)
            self._account_list_frame.refresh()

    def _apply_interest_fees(self):
        try:
            if len(self._selected_account.get_transactions()) >= 1:
                self._bank.apply_interest_and_fees(self._selected_account, self._session)
                logging.debug("Triggered interest and fees")
                self._session.commit()
                logging.debug("Saved to bank.db")
            self._account_list_frame.refresh()
            self._transaction_list_frame.refresh()
        except AttributeError:
            messagebox.showwarning("Error", "This command requires that you first select an account.")
        except TransactionLimitError as e:
            messagebox.showwarning("Error", e.message)
    
    def _on_account_selected(self, account):
        self._selected_account = account
        if self._add_transaction_frame is not None:
            self._add_transaction_frame.update_selected_account(account)
        self._transaction_list_frame.set_selected_account(account)
        self._transaction_list_frame.refresh()

    
if __name__ == "__main__":
    engine = create_engine(f"sqlite:///bank.db")
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine) 

    logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    try:
       app = BankGUI()
       app._window.mainloop()
    except Exception as e:
        error_message = str(e).replace('\n', '\\n')
        logging.error(f"{type(e).__name__}: '{error_message}'")
        handle_exception(e)


