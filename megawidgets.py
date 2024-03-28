from tkcalendar import Calendar
from decimal import Decimal, InvalidOperation
from datetime import datetime
from errors import OverdrawError, TransactionSequenceError, TransactionLimitError
import tkinter as tk
from tkinter import messagebox, ttk
import logging


class TransactionListFrame(tk.Frame):
    """Class that manages the transaction list window for the selected account."""
    def __init__(self, parent, session, bank, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg='white')
        self._session = session
        self._bank = bank
        self._selected_account = None
        self._title_label = None

    def _update_transactions(self, account):
        for widget in self.winfo_children():
            widget.destroy()

        self._title_label = tk.Label(self, text="Transactions", bg='white', fg='black', font=('Helvetica', 14, 'bold'))
        self._title_label.pack(side=tk.TOP, pady=(10, 5)) 

        if account is not None:
            transactions = account.get_transactions() 
            for transaction in transactions:
                if transaction.get_amount() < 0:
                    tk.Label(self, text=str(transaction), bg='white', fg='red', font=('Helvetica', 11)).pack(anchor='w', padx=20, pady=(0, 2))
                else:
                    tk.Label(self, text=str(transaction), bg='white', fg='green', font=('Helvetica', 11)).pack(anchor='w', padx=20, pady=(0, 2))
        else:
            self._title_label = tk.Label(self, text="Select/Open an account to view transactions", bg='white', fg='black', font=('Helvetica', 14, 'bold'))
            self._title_label.pack(side=tk.TOP, pady=(10, 5))

    def set_selected_account(self, account):
        """Recieves new account as parameter and resets the display of transactions based on passed account"""
        self._selected_account = account
        self._update_transactions(account)

    def refresh(self):
        """Refreshes the transactions when called on of the selected account"""
        self._update_transactions(self._selected_account)


class AddTransactionFrame(tk.Frame):
    """Class that manages the transaction entry window"""
    def __init__(self, parent, session, bank, selected_account, account_list_frame, transaction_list_frame, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg='white')
        
        #variable initializations 
        self._session = session
        self._bank = bank
        self._selected_account = selected_account
        self._account_list = account_list_frame
        self._transaction_list = transaction_list_frame

        #sets up the amount subframe (both label and input)
        self._amount_frame = tk.Frame(self, bg='white')
        self._amount_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self._amount_frame, text="Amount", bg='white', fg='black').pack(side=tk.LEFT)
        self._amount_var = tk.StringVar()
        self._amount_entry = tk.Entry(self._amount_frame, textvariable=self._amount_var, bg='white', fg='black')
        self._amount_entry.bind('<KeyRelease>', self._validate_amount) 
        self._amount_entry.pack(side=tk.RIGHT, padx=5, pady=5)

        #sets up the date subframe (both label and entry)
        self._date_frame = tk.Frame(self, bg='white')
        self._date_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Label(self._date_frame, text="Date", bg='white', fg='black').pack(side=tk.LEFT, padx=5, pady=5)
        self._date_picker = Calendar(self._date_frame, date_pattern="yyyy-mm-dd", width=12, background='white', foreground='black', borderwidth=2)
        self._date_picker.pack(side=tk.RIGHT, padx=5, pady=5)

        #enter and cancel buttons
        self._buttons_frame = tk.Frame(self, bg='white')
        self._buttons_frame.pack(side=tk.TOP, fill=tk.X)
        self._enter_button = tk.Button(self._buttons_frame, text="Enter", command=self._add_transaction_in_frame, bg='white', fg='black')
        self._enter_button.pack(side=tk.LEFT, padx=5, pady=5)
        self._cancel_button = tk.Button(self._buttons_frame, text="Cancel", command=self.destroy, bg='white', fg='black')
        self._cancel_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def _add_transaction_in_frame(self):
        try:
            amount = self._amount_entry.get()
            date_str = self._date_picker.get_date() 
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if self._validate_amount():
                self._bank.add_transaction(self._selected_account, amount, date, self._session)
                self.destroy()
                self._session.commit()
                self._account_list.refresh()
                self._transaction_list.refresh()
            else:
                messagebox.showerror("Error", "Invalid amount format")
        except OverdrawError as e:
            messagebox.showwarning("Error", e.message)
        except TransactionLimitError as e:
            messagebox.showwarning("Error", e.message)
        except TransactionSequenceError as e:
            messagebox.showwarning("Error", e.message)
            

    def _validate_amount(self, event = None):
        amount = self._amount_entry.get()
        try:
            Decimal(amount)
            self._amount_entry.config(highlightbackground='green', highlightcolor='green', highlightthickness=2)
            return True
        except InvalidOperation:
            self._amount_entry.config(highlightbackground='red', highlightcolor='red', highlightthickness=2)
            return False

    def _validate_date(self, event=None):
        date_str = self._date_entry.get()
        if len(date_str) != 10: 
            self._date_entry.config(highlightbackground='red', highlightcolor='red', highlightthickness=2)
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            self._date_entry.config(highlightbackground='green', highlightcolor='green', highlightthickness=2)
            return True
        except ValueError:
            self._date_entry.config(highlightbackground='red', highlightcolor='red', highlightthickness=2)
            return False

    def update_selected_account(self, account):
        """Updates the currently selected account to which the frame will add transactions."""
        self._selected_account = account


class AccountListFrame(tk.Frame):
    """Frame that presents all the available accounts and their balances, as well as current account selection."""
    def __init__(self, parent, session, bank, on_account_select, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg='white')
        self._session = session
        self._bank = bank
        self._selected_account = tk.StringVar()
        self._on_account_select = on_account_select
        self._update_accounts()

        self._accounts = self._bank.get_accounts()
        self._account_selected()

    def _update_accounts(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._accounts = self._bank.get_accounts()
        for account in self._accounts:
            rb = tk.Radiobutton(self, text=str(account),
                                variable=self._selected_account, value=account.get_account_number(),
                                bg='white', fg='black', selectcolor='blue', highlightthickness=0, 
                                command=self._account_selected)
            rb.pack(anchor='w', padx=20)
        if self._accounts:
            self._account_selected()

    def refresh(self):
        """Refreshes the accounts by calling update_accounts."""
        self._update_accounts()
    
    def _account_selected(self):
        account_number = self._selected_account.get()
        if account_number:
            self._on_account_select(self._bank.get_account(account_number))


class OpenAccountFrame(tk.Frame):
    """A megawidget for opening a new bank account."""
    def __init__(self, parent, session, bank, account_list, *args, **kwargs):
        super().__init__(parent, *args, **kwargs, bg='#53a9ee')
        self._session = session
        self._bank = bank
        self._account_list = account_list
        style = ttk.Style(parent)
        style.configure('TCombobox', highlightbackground='#53a9ee', background='#53a9ee', foreground='white')

        #sets up the combobox
        self._account_type_var = tk.StringVar()
        self._account_type_combobox = ttk.Combobox(self, textvariable=self._account_type_var, state="readonly",style='TCombobox')
        self._account_type_combobox['values'] = ("checking", "savings")
        self._account_type_combobox.pack(side=tk.LEFT, padx=5, pady=5)

        #enter button
        self._enter_button = tk.Button(self, text="Enter", command=self._create_account, bg='white', fg='black', highlightbackground='#53a9ee')
        self._enter_button.pack(side=tk.LEFT, padx=5, pady=5)

        #cancel button
        self._cancel_button = tk.Button(self, text="Cancel", command=self._cancel, bg='white', fg='black',highlightbackground='#53a9ee')
        self._cancel_button.pack(side=tk.LEFT, padx=5, pady=5)

    def _create_account(self):
        if (self._account_type_var.get() == "checking" or self._account_type_var.get() == "savings"):
            account_type = self._account_type_var.get()
            self._bank.open_account(account_type, self._session)
            logging.debug("Saved to bank.db")
        self._session.commit()
        self._account_list.refresh()
        self.destroy()

    def _cancel(self):
        self.destroy()

