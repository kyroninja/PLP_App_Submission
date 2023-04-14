# -*- coding: utf-8 -*-
"""

Note: Merged LoginPass module into main module
as it was not necessary to have it in a seperate module.

"""
#Note on the return codes:
# 0 - Failure
# 1 - Success
# 2 - Special Failure

import pickle
import sys
import easygui
import hashlib
import os
import random
import mysql.connector

class Inventory():
    '''This allows the modification of the inventory'''
    
    def __init__(self):
        self.invControl = {}
        

    def unpackInv(self):
        '''This function takes no arguments and it's job
        is to unpack the existing inventory or create it
        if the inventory file does not exist.'''

##        if os.path.exists('invData.stock'):
##            fseek = open('invData.stock', 'rb')
##            try:
##                self.invControl = pickle.load(fseek)
##            except EOFError:
##                pass
##            else:
##                return 1
##            finally:
##                fseek.close()

        if True:
            fb = open('invData.stock', 'wb')
            # connect to mysql on localhost
            cnx = mysql.connector.connect(user='test', password='abcdefg123', host='127.0.0.1', database='inventoryapp')
            sql = "select * from shopinv"
            cursor = cnx.cursor()
            cursor.execute(sql)
            records = cursor.fetchall()

            for i in records:
                self.invControl[i[0]] = (i[1], i[2], i[3])

            pickle.dump(self.invControl, fb, protocol = 2)
            fb.close()
            cnx.close()
            cursor.close()
            
            return 1
        
    def trunc_database(self):
        cnx = mysql.connector.connect(user='test', password='abcdefg123', host='127.0.0.1', database='inventoryapp')
        sql = "truncate table shopinv "
        cursor = cnx.cursor()
        cursor.execute(sql)
        cnx.commit()
        cursor.close()
        cnx.close()

    def update_database(self):
        cnx = mysql.connector.connect(user='test', password='abcdefg123', host='127.0.0.1', database='inventoryapp')
        cursor = cnx.cursor()
        item = ("INSERT INTO shopinv "
               "(ID, DESCRIPTION, CP, SP) "
               "VALUES (%s, %s, %s, %s)")

        for i in self.invControl:
            data = (i, self.invControl[i][0], self.invControl[i][1], self.invControl[i][2])
            cursor.execute(item, data)
            cnx.commit()
        cursor.close()
        cnx.close()

    def addItem(self, name, description, costprice , sellprice):
        '''This function takes FOUR arguments to add an item to the inventory
        @arg name: Name of the item
        @arg description: Description of item
        @arg costprice: Cost Price of the item
        @arg sellprice: Selling Price of item.'''
        self.invControl[name] = (description, costprice, sellprice)

        #fseek = open('invData.stock','wb')
        #pickle.dump(self.invControl, fseek, protocol = 2)
        #fseek.close()

        #self.trunc_database()
        #self.update_database()

        if name in self.invControl:
            #print(name, self.invControl[name])
            return 1
        else:
            return 0

    def searchInv(self, name):
        '''This takes ONE argument and it retireves
        the infomation on the item. This is also used for
        other purposes.'''
        if name in self.invControl:
            fields = self.invControl[name]
            return (name, fields[0], fields[1], fields[2])
        else:
            return 0

    def deleteItem(self, name):
        '''This takes ONE argument and it deletes the item.'''
        if name in self.invControl:
            del self.invControl[name]

            #fseek2 = open('invData.stock','wb')
            #pickle.dump(self.invControl, fseek2, protocol = 2)
            #fseek2.close()

            if name in self.invControl:
                return 0
            else:
                return 1
        else:
            pass

    def reviewInv(self):
        '''This retrieves all items in the inventory and sorts it
        in a list for use elsewhere.'''
        tlist = []
        for n in self.invControl.keys():
            tlist.append(n)
        tlist.sort()
        if len(tlist) == 0:
            return 0
        else:
            return tlist

class LoginPass(): # Login and Password module code
    '''This allows us to verify or generate a new user account'''
    
    def __init__(self):
        self.hashpath = 'userHash.crypt'
        self.hashdb = {}

    def writePass(self, username, passwordhash):
        '''This function takes TWO arguements:
        @arg username: Name of user
        @arg passwordhash: Hashed version of raw password.
        This also writes the file that contains it, and the
        username is in plaintext.'''

        username = str(username)
        passwordhash = str(passwordhash)

        if os.path.exists(self.hashpath):
            f = open(self.hashpath,'rb')
            try:
                self.hashdb = pickle.load(f)
            except EOFError:
                sys.stderr.write('''Password file has no or invalid data but
the data will still be written to it''')
            finally:
                f.close()

                f = open(self.hashpath,'wb')

            self.hashdb[username] = passwordhash
            pickle.dump(self.hashdb, f, protocol = 2)
            
            f.close()
            return 1

        else:
            fb = open(self.hashpath,'wb')

            self.hashdb[username] = passwordhash
            pickle.dump(self.hashdb, fb, protocol = 2)
            
            fb.close()
            return 1

    def verifyId(self, username, password):
        '''This function is used to verify a user's credentials
        like in a logon scenario, to ensure that it is an authorised
        user. It reads the file created by the writePass() function and
        will output an error if it cannot be found or is empty. '''
        alpha = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        punct = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""

        username = str(username)
        password = str(password)

        if os.path.exists(self.hashpath):
            fb = open(self.hashpath, 'rb')

            try:
                self.hashdb = pickle.load(fb)
            except EOFError:
                sys.stderr.write('Password file has no or invalid data\n')
            finally:
                fb.close()

            if username in self.hashdb:
                passwd = self.hashdb[username]
            else:
                tempPass = []
                t = 0
                while t < 14:
                    t += 1
                    tempPass.append(random.choice(alpha + digits + punct))

                passwd = ''.join(tempPass)

            h = hashlib.sha224()
            h.update(password.encode('utf-8'))

            if h.hexdigest() == passwd:
                return 1
            else:
                return 0
        else:
            return 2

def checkPass(inpasswordraw):
    '''This just verifies that the password is in
    a correct format such that:
    Length >= 7 characters
    password must have a digit at the END'''

    inpasswordraw = str(inpasswordraw)

    if len(inpasswordraw) >= 7:
        sys.stdout.write('Password is of a sufficient length\n')
        try:
            if type(int(inpasswordraw[-1])) == int:
                sys.stdout.write('Password contains a digit at end\n')
                return 1
        except ValueError:
            sys.stderr.write('Password has no digit at end\n')
            return 0
    else:
        sys.stderr.write('Password has insufficient length (must be 7 or more characters)\n')
        return 0

def hashPassword(passwordraw):
    '''This converts the users raw password into a hash
    to be used for authentication.'''
    W = hashlib.sha224()
    W.update(str(passwordraw).encode('utf-8'))
    data = W.hexdigest()
    return data

if __name__ == '__main__':
    # This is where the functions are used in a system of if, elif, else and while loops
    if '--accgen' in sys.argv:
        if sys.argv.index('--accgen') == 1:
            try:
                UNAME = str(sys.argv[2])
                UPASS = str(sys.argv[3])
            except IndexError:
                sys.stderr.write('\nToo many or too few arguments, require TWO only\n')
                sys.exit(1)
            if checkPass(UPASS) == 1:
                if LoginPass().writePass(UNAME, hashPassword(UPASS)):
                    sys.stdout.write('\nAccount Generation: Success\n')
                    sys.exit(0)
                else:
                    sys.stderr.write('\nAccount Generation: Failure\n')
                    sys.exit(1)
            else:
                sys.stderr.write('\nPassword has incorrect format and \
it needs to be longer than 7 and have a digit at the end'
                )
                sys.exit(1)
        else:
            sys.stderr.write('"\n--passgen" is in the wrong position, must be first argument\n')
            sys.exit(1)
    else:
        sys.stdout.write('\nNo arguments specified, nothing to do\n')

    easygui.msgbox(msg="Welcome to Malume's Spaza Shop", title="Malume's Spaza Shop")

    # make sure that none of the fields was left blank
    # From easygui cookbook

    L_MSG = '''Enter your logon credentials
(NOTE): The default username is "SUT"'''
    L_TITLE = 'User Logon Dialog'
    L_FIELDNAMES = ["Username", "Password"]
    L_FIELDVALUES = []
    L_FIELDVALUES = easygui.multpasswordbox(msg=L_MSG, title=L_TITLE, fields=L_FIELDNAMES, values=L_FIELDVALUES)

    while 1:
        if L_FIELDVALUES == None:
            easygui.msgbox(msg='You have aborted the Logon', title='Operation(Logon): Failure')
            sys.exit(1)
        L_ERRMSG = ""
        for i in range(len(L_FIELDNAMES)):
            if L_FIELDVALUES[i].strip() == "":
                L_ERRMSG += ('"%s" is a required field\n\n' % L_FIELDNAMES[i])
        if L_ERRMSG == "":
            break # no problems found
        L_FIELDVALUES = easygui.multpasswordbox(msg=L_ERRMSG, title=L_TITLE, fields=L_FIELDNAMES, values=L_FIELDVALUES)

    L = LoginPass()

    if L.verifyId(L_FIELDVALUES[0], L_FIELDVALUES[1]) == 1:
        easygui.msgbox(msg='User: %s ---> Status: Verified' % L_FIELDVALUES[0],
        title='Operation(Logon): Success')

        P = Inventory()

        if P.unpackInv() == 1:

            while 1:
                MENUOPTS = '''Welcome, "%s" to Malume's Spaza Shop\n
Please select from one of the following options!''' % L_FIELDVALUES[0]

                DECISION = easygui.buttonbox(msg=MENUOPTS, title ="Malume's Spaza Shop",

                choices=('Add Item', 'Edit Item','Delete Item', 'Search Item (SP)',
                'Search Item (CP)', 'About Program', 'Quit Program'),
                image='shoplogo.gif')

                if DECISION == 'Add Item':
                    A_MSG = 'Enter the relevant item details'
                    A_TITLE = '(Add Item): Inventory Control'
                    A_FIELDNAMES = ['Item Name', 'Description', 'Cost Price', 'Selling Price']
                    A_FIELDVALUES = []
                    A_FIELDVALUES = easygui.multenterbox(msg=A_MSG, title=A_TITLE,
                    fields=A_FIELDNAMES, values=A_FIELDVALUES)

                # make sure that none of the fields was left blank
                # From easygui cookbook

                    while 1:
                        if A_FIELDVALUES == None:
                            break
                        A_ERRMSG = ""
                        for i in range(len(A_FIELDNAMES)):
                            if A_FIELDVALUES[i].strip() == "":
                                A_ERRMSG += ('"%s" is a required field\n\n' % A_FIELDNAMES[i])
                        if A_ERRMSG == "":
                            break # no problems found
                        A_FIELDVALUES = easygui.multenterbox(msg=A_ERRMSG, title=A_TITLE,
                        fields=A_FIELDNAMES, values=A_FIELDVALUES)

                    try:
                        float(A_FIELDVALUES[2])
                        float(A_FIELDVALUES[3])
                    except TypeError:
                        easygui.msgbox(msg='You cancelled the add item operation', title='Add Item: Operation Cancelled')
                    except ValueError:
                        easygui.msgbox(msg='Selling Price and Cost Price have to be numbers', title='Invalid Values')
                    else:
                        if P.addItem(A_FIELDVALUES[0], A_FIELDVALUES[1], float(A_FIELDVALUES[2]), float(A_FIELDVALUES[3])) == 1:
                            easygui.msgbox(msg='Item "%s" has been added' % A_FIELDVALUES[0],
title='Operation(Add Item): Success')
                        else:
                            easygui.msgbox(msg='Item "%s" has not been added' % A_FIELDVALUES[0],
title='Operation(Add Item): Failure')

                elif DECISION == 'Edit Item':
                    if P.reviewInv() == 0:
                        easygui.msgbox(msg='Warning: The inventory is empty', title='Important Infomation')
                    else:
                        EDITITEM = easygui.choicebox(msg='''This is the current contents of the inventory.

Select an item to edit it and it's data --- !

NOTE: This gives the cost price of the item as well!''',
title='(Edit Item): Inventory Control -- %s item(s) in inventory' % len(P.reviewInv()),
choices=[s for s in P.reviewInv()])

                        if EDITITEM == None:
                            easygui.msgbox(msg='You cancelled the edit item operation', title='Edit Item: Operation Cancelled')
                        else:
                            EDATA = P.searchInv(EDITITEM)

                            if EDATA != 0:
                                E_MSG = 'Modify the appropriate fields'
                                E_TITLE = '(Edit Item): [%s]' % EDATA[0]
                                E_FIELDNAMES = ['Description', 'Cost Price', 'Selling Price']
                                E_FIELDVALUES = [EDATA[1], EDATA[2], EDATA[3]]

                                E_FIELDVALUES = easygui.multenterbox(msg=E_MSG, title=E_TITLE,
                                fields=E_FIELDNAMES, values=E_FIELDVALUES)

                                while 1:
                                    if E_FIELDVALUES == None:
                                        break
                                    E_ERRMSG = ""
                                    for i in range(len(E_FIELDNAMES)):
                                        if E_FIELDVALUES[i].strip() == "":
                                            E_ERRMSG += ('"%s" is a required field\n\n' % E_FIELDNAMES[i])
                                    if E_ERRMSG == "":
                                        break # no problems found
                                    E_FIELDVALUES = easygui.multenterbox(msg=E_ERRMSG, title=E_TITLE,
                                    fields=E_FIELDNAMES, values=E_FIELDVALUES)

                                try:
                                    float(E_FIELDVALUES[1])
                                    float(E_FIELDVALUES[2])
                                except TypeError:
                                    easygui.msgbox(msg='You cancelled the edit operation', title='Edit Item: Operation Cancelled')
                                except ValueError:
                                    easygui.msgbox(msg='Selling Price and Cost Price have to be numbers', title='Invalid Values')
                                else:
                                    if P.addItem(EDATA[0], E_FIELDVALUES[0], float(E_FIELDVALUES[1]), float(E_FIELDVALUES[2])) == 1:
                                        easygui.msgbox(msg='Item "%s" has been edited' % EDATA[0],
title='Operation(Edit Item): Success')
                                    else:
                                        easygui.msgbox(msg='Item "%s" has not been edited' % EDATA[0],
title='Operation(Edit Item): Failure')
                            else:
                                pass

                elif DECISION == 'Delete Item':
                    if P.reviewInv() == 0:
                        easygui.msgbox(msg='Warning: The inventory is empty', title='Important Infomation')
                    else:
                        DELETEITEM = easygui.choicebox(msg='''This is the current contents of the inventory.

Select an item to delete --- !''',
title='(Delete): Inventory Control -- %s item(s) in inventory' % len(P.reviewInv()),
choices=[m for m in P.reviewInv()])

                        if DELETEITEM == None:
                            easygui.msgbox(msg='You cancelled the delete operation', title='Delete: Operation Cancelled')
                        else:
                            DITEM = P.deleteItem(DELETEITEM)

                            if DITEM == 1:
                                easygui.msgbox(msg='Item "%s" has been deleted' % DELETEITEM,
title='Operation(Delete): Success')
                            else:
                                easygui.msgbox(msg='Item "%s" could not be deleted' % DELETEITEM,
title='Operation(Delete): Failure')

                elif DECISION == 'Search Item (SP)':
                    if P.reviewInv() == 0:
                        easygui.msgbox(msg='Warning: The inventory is empty', title='Important Infomation')
                    else:
                        SEARCHITEM = easygui.choicebox(msg='''This is the current contents of the inventory.

Select an item to get more infomation on it --- !''',
title='(Search SP): Inventory Control -- %s item(s) in inventory' % len(P.reviewInv()),
choices=[g for g in P.reviewInv()])

                        if SEARCHITEM == None:
                            easygui.msgbox(msg='You cancelled the search operation', title='Search(SP): Operation Cancelled')
                        else:
                            #SDATA = P.searchInv(SEARCHITEM)
                            SDATA = P.searchInv(SEARCHITEM)

                            if SDATA != 0:
                                msg = '''Item Name: %s
Item Description: %s
Item Selling Price: R %.2f''' % (SDATA[0], SDATA[1], SDATA[3])
                                easygui.msgbox(msg, title = 'Operation(Search SP): Success')

                            else:
                                easygui.msgbox(msg='Item "%s" does not exist in Inventory' % SEARCHITEM,
                                title='Operation(Search SP): Failure')


                elif DECISION == 'Search Item (CP)':
                    if P.reviewInv() == 0:
                        easygui.msgbox(msg='Warning: The inventory is empty', title='Important Infomation')
                    else:
                        SEARCHITEMCP = easygui.choicebox(msg='''This is the current contents of the inventory.

Select an item to get more infomation on it --- !

NOTE: This gives the cost price of the item as well!''',
title='(Search CP): Inventory Control -- %s item(s) in inventory' % len(P.reviewInv()),
choices=[s for s in P.reviewInv()])

                        if SEARCHITEMCP == None:
                            easygui.msgbox(msg='You cancelled the search operation', title='Search(CP): Operation Cancelled')
                        else:
                            #SCDATA = P.searchInv(SEARCHITEMCP)
                            SCDATA = P.searchInv(SEARCHITEMCP)

                            if SCDATA != 0:
                                SCMSG = '''Item Name: %s
Item Description: %s
Item Cost Price: R %.2f
Item Selling Price: R %.2f''' % (SCDATA[0], SCDATA[1], SCDATA[2], SCDATA[3])
                                easygui.msgbox(msg=SCMSG, title = 'Operation(Search CP): Success')

                            else:
                                easygui.msgbox(msg='Item "%s" does not exist in Inventory' % SEARCHITEMCP,
                                title='Operation(Search CP): Failure')

                elif DECISION == 'About Program':
                    
                    PROGCREDITS = '''This was developed by "Pratish Surendra Neerputh"
also known as "kyroninja"
for Malume's Spaza Shop. Application was created with:

---|>Python 3.9
---|>EasyGUI 0.98 Tk Frontend
'''
                    easygui.msgbox(msg=PROGCREDITS, title='About the Program', image='logo.gif')

                else:
                    print("exiting now")
                    P.trunc_database()
                    P.update_database()
                    sys.exit(1)
            else:
                pass
        else:
            easygui.msgbox('Reading Inventory Failed.', title='Inventory Error!')

    elif L.verifyId(L_FIELDVALUES[0], L_FIELDVALUES[1]) == 2:
        easygui.msgbox(msg='Please generate a user account first', title='Operation(Logon): Failure')

    else:
        easygui.msgbox(msg='User: %s ---> Status: Unverified/Unknown' % L_FIELDVALUES[0], title='Operation(Logon): Failure')

else:
    sys.stdout.write('I am not being run directly instead I am being imported!')
