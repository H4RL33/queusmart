import pyinputplus as pyip
import bcrypt as bc

def createPass():
    ogPass = pyip.inputStr("Create Password:\n")
    bytes = ogPass.encode("utf-8")
    salt = bc.gensalt()

    return bc.hashpw(bytes, salt)

def usePass(hashPass):
    userPass = pyip.inputStr("Enter Password:\n")

    userBytes = userPass.encode("utf-8")

    result = bc.checkpw(userBytes, hashPass)

    if result == True:
        print("correct password!")
    elif result == False:
        print("incorrect. sod off")
    else:
        print("what")

hashPass = createPass()
usePass(hashPass)
