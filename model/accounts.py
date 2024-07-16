import json
class Account:
    def __init__(self, username, password, email = "example@example.com"):
        self.username = username
        self.password = password
        self.email = email
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    def __eq__(self, other):
        if isinstance(other, Account):
            return (self.username == other.username and
                    self.password == other.password)
        return False
    def show(self):
        print("US:", self.username, "-PW:", self.password, "-EM:", self.email)
    def setNewPassword(self, password):
        self.password = password
    def getUserName(self):
        return self.username
    def getPassWord(self):
        return self.password

class ListAccounts:
    def __init__(self):
        self.list = []
        self.loadAllAccounts()
    
    def addAccount(self, account)->bool:
        if not self.checkAccount(account):
            self.list.append(account)
            self.saveAllAccounts()
            return True
        else:
            return False
        
    def showAllAccount(self):
        for account in self.list:
            account.show()
    def changePasswordAccount(self, username, oldpassword, newpassword):
        for account in self.list:
            if account.username == username:
                if account.password == oldpassword:
                    account.setNewPassword(newpassword)
                else:
                    print("Wrong password!!!!")
    def saveAllAccounts(self):
        jsonfiles = list()
        for account in self.list:
            jsonfiles.append(account.__dict__)
        with open("data/accounts.json", "w") as file:
            json.dump(jsonfiles, file, indent=3)

    def loadAllAccounts(self):
        try:
            with open("data/accounts.json", "r") as file:
                jsonFile =  json.load(file)
                for account in jsonFile:
                    self.list.append(Account.from_dict(account))
        except FileNotFoundError:
            print("The file 'data/accounts.json' was not found.")
        except json.JSONDecodeError:
            print("The file 'data/accounts.json' does not contain valid JSON data.")
    def checkAccount(self, account:Account):
        return account in self.list
