class MoneyManager():

       
    def __init__(self, user_number='', pin_number='', balance=0.0, transaction_list=[]):
        '''Constructor to set username to '', pin_number to an empty string,
           balance to 0.0, and transaction_list to an empty list.'''
        self.user_number = user_number
        self.pin_number = pin_number
        self.balance = balance
        self.transaction_list = transaction_list

    # def add_entry(self, amount, entry_type):
    # see perform_transaction() in main

    # def deposit_funds(self, amount):
    # see perform_deposit() in main
        
    def get_transaction_string(self, list_to_convert):
        '''Function to create and return a string of the transaction list.'''
        # unpack list of tuples into words in a string seperated by \n
        global transaction_string
        
        temp_list = []

        for i in list_to_convert:
            temp_list.append(i[0])
            temp_list.append(i[1])

        seperator = '\n'
        transaction_string = seperator.join(temp_list)
        return transaction_string

    def save_to_file(self, user_num, user_pin, current_balance):
        '''Function to overwrite the user text file with the current user
           details.'''
        user_file = user_num + '.txt'
        # rewrite file with new information
        with open(user_file, 'w') as f:
            f.write(user_num + '\n')
            f.write(user_pin + '\n')
            f.write(str(current_balance) + '\n')
            # no need for current_transactions parameter as transaction_string
            # can be accessed from the function above
            f.write(transaction_string)
            f.close()

        


        
