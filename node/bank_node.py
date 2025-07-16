class BankNode:
    def __init__(self):
        self.accounts = {}  

    def deposit(self, account, amount):
        if account not in self.accounts:
            self.accounts[account] = 0
        self.accounts[account] += amount
        return self.accounts[account]

    def transfer(self, from_acc, to_acc, amount):
        if self.accounts.get(from_acc, 0) < amount:
            return False
        self.accounts[from_acc] -= amount
        self.accounts[to_acc] = self.accounts.get(to_acc, 0) + amount
        return True

    def get_balances(self):
        return self.accounts
