import unittest

from moneymanager import MoneyManager
from main import *

class TestMoneyManager(unittest.TestCase):

    def setUp(self):
        # Create a test BankAccount object
        self.user = MoneyManager()
        # Provide it with some initial balance values        
        self.user.balance = 1000.0

        # Write new userfile for testing
        # Default username and pin
        with open('123456.txt', 'w+') as f:
            f.write('123456' + '\n')
            f.write('7890' + '\n')
            f.write('1000.0' + '\n')
            f.write('Deposit' + '\n')
            f.write('1000.0' + '\n')
            f.close()
        
    def test_legal_deposit_works(self):
        # legal deposit bool will be set to true in main if legal deposit is made.
        self.assertTrue(legal_deposit)
                

    def test_illegal_deposit_raises_exception(self):
        # illegal deposit exception bool will be set to true in main if exception raised
        self.assertTrue(illegal_deposit_exception)
        

    def test_legal_entry(self):
        # legal entry bool will be set to true in main if legal entry is made.
        self.assertTrue(legal_entry)
        

    def test_illegal_entry_amount(self):
        # illegal entry amount will be set to true in main if negative number entered.
        self.assertTrue(illegal_entry_amount)
        
        
    def test_illegal_entry_type(self):
        # illegal entry type will be set to true if string entered.
        self.assertTrue(illegal_entry_type)
        

    def test_insufficient_funds_entry(self):
        # insuff funds will be set to true if amount entered is higher than bal.
        self.assertTrue(insuff_funds)

# Run the unit tests in the above test case
unittest.main()       
