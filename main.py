import tkinter as tk
from tkinter import *
from tkinter import messagebox
import tkinter.scrolledtext as tkscrolled

from pylab import plot, show, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict
from pprint import pprint
import matplotlib.pyplot as plt
import math

from moneymanager import MoneyManager

# Creating login window
win = tk.Tk()
win.geometry('500x660')
win.winfo_toplevel().title('FedUni Money Manager')

# Testing Bools
legal_deposit = False
illegal_deposit_exception = False
legal_entry = False
illegal_entry_amount = False
illegal_entry_type = False
insuff_funds = False

# Money Manager object
user = MoneyManager()

# Set the user file by default to an empty string
user_file = ''

# --- Button Handlers for Login Screen ---
def clear_pin_entry(event):
    '''Function to clear the PIN number entry when the Clear / Cancel button is clicked.'''    
    user_pin_entry.delete(0,tk.END)


def handle_pin_button(event):
    '''Function to add the number of the button clicked to the PIN number entry.'''
    # Limit to 4 chars in length
    # below method freezes login window and user has to kill program
    current_entries = user_pin_entry.get()
    # while len(current_entries) <= 4:
    user_pin_entry.delete(0,tk.END)
    user_pin_entry.insert(0, current_entries + event)
    # Set the new pin number on the pin_number_var
    pin_number_var.set(user_pin_entry.get())
    

def log_in():
    '''Function to log in to the banking system using a known user number and PIN.'''
    global user
    global pin_number_var
    global user_file
    global user_num_entry
    global bal_in_file
    global transaction_list
    
    # Create the filename from the entered account number with '.txt' on the end
    user_file = user_num_entry.get() + '.txt'
    # Try to open the account file for reading
    try:
    # Open the account file for reading
        with open(user_file, 'r') as f:
            # First line is account number
            lines = f.readlines()
            temp = lines[1]
            # Read only first four characters of pin line to exclude '/n' or any other mistakes in file
            pin_in_file = temp[0:4]
            # Raise exceptionk if the PIN entered doesn't match account PIN read 
            if pin_in_file == user_pin_entry.get():
                # Read third line (balance)
                bal_in_file = float(lines[2])
                # Section to read account transactions from file
                # Reopen file to create list of transactions
                with open(user_file, "r") as f:
                    trans_list_temp = f.read().split()
                    transaction_list = []
                    # Slice first 3 items (user num, pin, and bal) from transaction list
                    trans_list_temp = trans_list_temp[3:]
                    trans_list_len = len(trans_list_temp)
                    item = 0
                    item2 = 2
                    # loop to group items into tuples and append to final transaction list
                    while trans_list_len > 0:
                        trans_tuple = tuple(trans_list_temp[item:item2])
                        transaction_list.append(trans_tuple)
                        item = item + 2
                        item2 = item2 + 2
                        trans_list_len = trans_list_len - 2

                # Close the file now we're finished with it
                f.close()
                
                # Remove the widgets and display the account screen
                remove_all_widgets()
                create_user_screen()
            else:
                # Catch exception if we couldn't open the file or PIN entered did not match account PIN
                # Show error messagebox and & reset to default also clear PIN entry and change focus to account number entry
                tk.messagebox.showerror(title='Invalid PIN', message='Invalid PIN was entered, please enter the correct credentials to proceed.')
                user_pin_entry.delete(0,tk.END)
    except FileNotFoundError:
        tk.messagebox.showerror(title='Invalid user number', message='Invalid user number was entered, please enter the correct credentials to proceed.')
        user_num_entry.delete(0,tk.END)


# --- Button Handlers for User Screen ---
def save_and_log_out():
    '''Function  to overwrite the user file with the current state of
       the user object, remove all widgets and display the login screen.'''
    global user

    # Check value of user balance
    with open(user_file, 'r') as f:
        lines = f.readlines()
        bal_in_file = float(lines[2])

    user.save_to_file(user_num_entry.get(), user_pin_entry.get(), bal_in_file)

    # Reset the account number and pin to blank
    user_pin_entry.delete(0,tk.END)
    user_num_entry.delete(0,tk.END)
    pin_number_var.set(' ')
    user_number_var.set(' ')

    # Remove all widgets and display the login screen again
    remove_all_widgets()
    create_login_screen()


def perform_deposit():
    '''Function to add a deposit for the amount in the amount entry to the user's transaction list.'''
    global user    
    global amount_entry
    global balance_label
    global balance_var
    global new_bal
    global transaction_list
    global legal_deposit
    global illegal_deposit_exception

    # Try to increase the account balance and append the deposit to the account file
    try:
        # Get the cash amount to deposit
        deposit = float(amount_entry.get())
        if deposit > 0:
            # Check value of user balance
            with open(user_file, 'r') as f:
                lines = f.readlines()
                bal_in_file = float(lines[2])
            # Deposit funds
            new_bal = bal_in_file + deposit
            # Update balance label
            balance_var.set('Balance: $' + str(new_bal))
            # Create a new entry list then convert to tuple and append to transaction list
            entry = ['Deposit']
            entry.append(str(deposit))
            transaction_list.append(tuple(entry))

            # Update transaction text field
            transaction_text_widget.config(state='normal')
            # Delete screen before inserting old + new transaction list to prevent duplicates
            transaction_text_widget.delete(1.0, tk.END)
            transaction_text_widget.insert(tk.INSERT, user.get_transaction_string(transaction_list))
            transaction_text_widget.config(state='disabled')

            # Save updated details to file
            user.save_to_file(user_num_entry.get(), user_pin_entry.get(), new_bal)

            # Clear the amount entry
            amount_entry.delete(0, tk.END)

            # Update graph
            plot_spending_graph()

            # Set legal_deposit to true for testing
            legal_deposit = True
            
        else:
            tk.messagebox.showerror(title='Deposit Error', message='Illegal amount entered.')

            # Set legal_deposit_exception to true for testing
            illegal_deposit_exception = True

    # Catch and display exception as a messagebox
    except Exception as e:
        amount_entry.delete(0,tk.END)
        depos_error = 'Error! {}'.format(e)
        tk.messagebox.showerror(title='Deposit Error', message=depos_error)

        # Set legal_deposit_exception to true for testing
        illegal_deposit_exception = True


def perform_transaction():
    '''Function to add the entry and the amount (taken from the user balance) the transaction list.'''
    global user    
    global amount_entry
    global balance_label
    global balance_var
    global user_entry
    global transaction_list
    global legal_entry
    global illegal_entry_amount
    global illegal_entry_type
    global insuff_funds

    # Try to decrease the account balance and append the deposit to the account file
    try:
        # Get the cash amount to deposit
        deposit = float(amount_entry.get())
        if deposit > 0:
            # Check value of user balance
            with open(user_file, 'r') as f:
                lines = f.readlines()
                bal_in_file = float(lines[2])
            # If the user has sufficient funds
            if bal_in_file >= deposit:
                # Get the type of entry that will be added
                user_entry = user_entry_type.get()
                # If user entry is illegal
                if len(user_entry) > 1:
                    # Subtract deposit from existing funds
                    new_bal = bal_in_file - deposit
                    # Update balance label
                    balance_var.set('Balance: $' + str(new_bal))
                    # Create a new entry list then convert to tuple and append to transaction list
                    entry = [str(user_entry)]
                    entry.append(str(deposit))
                    transaction_list.append(tuple(entry))

                    # Update transaction text field
                    transaction_text_widget.config(state='normal')
                    # Delete screen before inserting old + new transaction list to prevent duplicates
                    transaction_text_widget.delete(1.0, tk.END)
                    transaction_text_widget.insert(tk.INSERT, user.get_transaction_string(transaction_list))
                    transaction_text_widget.config(state='disabled')

                    # Save updated details to file
                    user.save_to_file(user_num_entry.get(), user_pin_entry.get(), new_bal)

                    # Clear the amount entry
                    amount_entry.delete(0, tk.END)

                    # Update graph
                    plot_spending_graph()

                    # Set legal entry to true for testing
                    legal_entry = True

                else:
                    amount_entry.delete(0, tk.END)
                    tk.messagebox.showerror(title='Illegal entry type', message='Please select an entry type.')
            else:
                amount_entry.delete(0, tk.END)
                tk.messagebox.showerror(title='Insufficient funds', message='You have insufficient funds to make this transaction.')
                # Set insuff funds to true for testing
                insuff_funds = True
        else:
            tk.messagebox.showerror(title='Deposit Error', message='Illegal amount entered.')
            # Set illegal entry type to true for testing
            illegal_entry_type = True
        
    except Exception as e:
        amount_entry.delete(0,tk.END)
        trans_error = 'Error! {}'.format(e)
        tk.messagebox.showerror(title='Transaction Error', message=trans_error)
        # Set illegal entry amount to true for testing
        illegal_entry_amount = True

    # Catch and display any returned exception as a messagebox 'showerror'

# --- Misc. Functions ---

def plot_spending_graph():
    '''Function to plot the user spending here.'''
    # Generating x and y lists to plot:
    # Convert list of tuples to list of dictionaries
    keys = ('entry', 'amount')
    transaction_list_dict = [dict(zip(keys, values)) for values in transaction_list]

    # add amounts of duplicate dictionary entries
    result = defaultdict(float)

    for i in transaction_list_dict:
        result[i['entry']] += float(i['amount'])

    added_transaction_list = [{'entry': entry, 'amount': amount} for entry, amount in result.items()]

    string_transaction_dict = []
    # unpack all dictionaries in list
    for d in added_transaction_list:
        # convert all dict items to strings so they can be gathered with .values()
        keys_values = d.items()
        temp = {str(key): str(value) for key, value in keys_values}
        # Repack into string_transaction_dict
        string_transaction_dict.append(temp)

    # Convert back to list of tuples
    final_plot_list = []
    index = 0
    for d in string_transaction_dict:
        item = tuple(string_transaction_dict[index].values())
        index += 1
        final_plot_list.append(item)

    # Add entries to list of entries and amounts to list of amounts
    entries = []
    amounts = []
    index = 0
    for d in string_transaction_dict:
        entry = final_plot_list[index][0]
        amount = final_plot_list[index][1]
        index += 1
        entries.append(entry)
        amounts.append(float(amount))

    # Plot and display graph:
    # figure containing subplot 
    fig = Figure(figsize = (6, 4), dpi = 80)
    spending_graph = fig.add_subplot(111)
  
    # plotting the graph
    spending_graph.bar(entries, amounts, width=.5)

    # Graph titles, etc.
    spending_graph.set_title('Spending by category')
    spending_graph.set_xlabel('Category')
    spending_graph.set_ylabel('Total amount spent ($)')
  
    # creating the Tkinter canvas 
    # containing the Matplotlib figure 
    canvas = FigureCanvasTkAgg(fig, master = win)   
    canvas.draw() 
  
    # placing the canvas on the Tkinter window 
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=3)

def remove_all_widgets():
    '''Function to remove all the widgets from the window.'''
    global win
    for widget in win.winfo_children():
        widget.grid_remove()


'''def read_line_from_user_file():
    #Function to read a line from the users file but not the last newline character.
    #Note: The user_file must be open to read from for this function to succeed.
    global user_file
    return user_file.readline()[0:-1]'''

# --- UI Functions ---

def create_login_screen():
    global user_number_var
    global user_num_entry
    global pin_number_var
    global user_pin_entry

    # ---ROW 0---
    subtitle = tk.Label(win, text='FedUni Money Manager', width=23, font=('', 28))
    subtitle.grid(row=0, column=0, columnspan=3)

    # ---ROW 1---
    num_pin_label = tk.Label(win, text='User Number / PIN')
    num_pin_label.grid(row=1, column=0, pady=40)

    # The user number entry and associated variables
    user_number_var = tk.StringVar()
    '''This is set as a default for ease of testing'''
    user_number_var.set('123456')
    user_num_entry = tk.Entry(win, textvariable=user_number_var)
    user_num_entry.grid(row=1, column=1, sticky='nsew')
    user_num_entry.focus_set()

    # The pin number entry and associated variables
    pin_number_var = tk.StringVar()
    '''This is set as a default for ease of testing'''
    pin_number_var.set('7890')
    user_pin_entry = tk.Entry(win, textvariable=pin_number_var, show='*')
    user_pin_entry.grid(row=1, column=2, sticky='nsew')

    # Login screen buttons and grid placements
    # ---ROW 2---
    B1 = tk.Button(win, text='1', command=lambda:handle_pin_button('1'))
    B2 = tk.Button(win, text='2', command=lambda:handle_pin_button('2'))
    B3 = tk.Button(win, text='3', command=lambda:handle_pin_button('3'))

    B1.grid(row=2, column=0, sticky='nsew')
    B2.grid(row=2, column=1, sticky='nsew')
    B3.grid(row=2, column=2, sticky='nsew')

    # ---ROW 3---
    B4 = tk.Button(win, text='4', command=lambda:handle_pin_button('4'))
    B5 = tk.Button(win, text='5', command=lambda:handle_pin_button('5'))
    B6 = tk.Button(win, text='6', command=lambda:handle_pin_button('6'))

    B4.grid(row=3, column=0, sticky='nsew')
    B5.grid(row=3, column=1, sticky='nsew')
    B6.grid(row=3, column=2, sticky='nsew')

    # ---ROW 4---
    B7 = tk.Button(win, text='7', command=lambda:handle_pin_button('7'))
    B8 = tk.Button(win, text='8', command=lambda:handle_pin_button('8'))
    B9 = tk.Button(win, text='9', command=lambda:handle_pin_button('9'))

    B7.grid(row=4, column=0, sticky='nsew')
    B8.grid(row=4, column=1, sticky='nsew')
    B9.grid(row=4, column=2, sticky='nsew')

    # ---ROW 5---
    login_button = tk.Button(win, text='Login', bg='light green', activebackground='green', command=lambda:log_in())
    login_button.grid(row=5, column=2, sticky='nsew')

    B0 = tk.Button(win, text='0', command=lambda:handle_pin_button('0'))
    B0.grid(row=5, column=1, sticky='nsew')

    clear_button = tk.Button(win, text='Clear', bg='red', activebackground='maroon', command=lambda:clear_pin_entry(''))
    clear_button.grid(row=5, column=0, sticky='nsew')

    # Column and row weights
    win.columnconfigure(0, weight=1)
    win.columnconfigure(1, weight=1)
    win.columnconfigure(2, weight=1)
    win.columnconfigure(3, weight=1)
    win.columnconfigure(4, weight=1)
    win.rowconfigure(0, weight=2)
    win.rowconfigure(1, weight=1)
    win.rowconfigure(2, weight=2)
    win.rowconfigure(3, weight=2)
    win.rowconfigure(4, weight=2)
    win.rowconfigure(5, weight=2)

def create_user_screen():
    '''Function to create the user screen.'''
    global amount_text
    global amount_label
    global transaction_text_widget
    global balance_var
    global user_entry_type
    global user
    global amount_entry
    
    # --- ROW 0 ---
    subtitle = tk.Label(win, text='FedUni Money Manager', font=('', 22))
    subtitle.grid(row=0, column=0, columnspan=5)

    # --- ROW 1 ---
    user_num_display = tk.Label(win, textvariable=user_number_var)
    user_num_display.grid(row=1, column=0)

    # The balance label and associated variable
    balance_var = tk.StringVar()
    balance_var.set('Balance: $' + str(bal_in_file))
    balance_label = tk.Label(win, textvariable=balance_var)

    user_bal_display = tk.Label(win, textvariable=balance_var)
    user_bal_display.grid(row=1, column=1)
    
    log_out_button = tk.Button(win, text='log out', command=lambda:save_and_log_out())
    log_out_button.grid(row=1, column=2, sticky='nsew')

    # --- ROW 2 ---
    amount_label = tk.Label(win, text='Amount ($):')
    amount_label.grid(row=2, column=0)

    # The amount widget variables
    amount_var = tk.StringVar()

    amount_entry = tk.Entry(win, textvariable=amount_var)
    amount_entry.grid(row=2, column=1)

    deposit_button = tk.Button(win, text='deposit', command=lambda:perform_deposit())
    deposit_button.grid(row=2, column=2, sticky='nsew')
    
    # --- ROW 3 --- 
    
    entry_type_label = tk.Label(win, text='Entry type:')
    entry_type_label.grid(row=3, column=0)

    # Type widget variable
    user_entry_type = tk.StringVar()
    
    entry_list = OptionMenu(win, user_entry_type, 'Food', 'Rent', 'Bills', 'Entertainment', 'Other')
    entry_list.grid(row=3, column=1)

    add_entry_button = tk.Button(win, text='Add entry', command=lambda:perform_transaction())
    add_entry_button.grid(row=3, column=2, sticky='nsew')

    # --- ROW 4 ---
    # ScrolledText combines scrollbar and text in the one widget
    transaction_text_widget = tkscrolled.ScrolledText(win, state='disabled', height=10)
    transaction_text_widget.grid(row=4, column=0, columnspan=3)

    # Initial update of text from file
    transaction_text_widget.config(state='normal')
    transaction_text_widget.insert(tk.INSERT, user.get_transaction_string(transaction_list))
    transaction_text_widget.config(state='disabled')

    # --- ROW 5 ---
    # Function to display the spending graph
    plot_spending_graph()
    
    # Column & row weights
    win.columnconfigure(0, weight=2)
    win.columnconfigure(1, weight=2)
    win.columnconfigure(2, weight=2)
    win.rowconfigure(0, weight=3)
    win.rowconfigure(1, weight=3)
    win.rowconfigure(2, weight=3)
    win.rowconfigure(3, weight=3)
    win.rowconfigure(4, weight=3)
    win.rowconfigure(5, weight=3)

# --- Start Main loop ---
create_login_screen()
win.mainloop()
