l = ["menu.com/f1.a", "menu.com/f2.b", "menu.com/f3.c"]
#
import pathlib
#lst -> list of links
# -> list of extension which are permitted to be displayed


def DisplayMenu(title, lst, filter=None):
    print(">>> Setting up " + title)
    for i in range(len(lst)):
        if filter == None or len(filter) == 0:
           print("[{0}] ({1})".format(str(i), lst[i]))
           
        elif (pathlib.Path(lst[i]).suffix) in filter:
            
           print("[{0}] ({1})".format(str(i), lst[i]))
    inp = ""
    while (True):
        try:
            inp = int(input("Choice: "))
            if (inp >= 0 and inp <= i):
                break
        except ValueError:
            continue
    return lst[inp]
    
#
# str text
# return: bool (yes/no)
def ConfDialog(stri):
    
    inp = ""
    while (inp.lower() != 'y' and inp.lower() != 'n'):
        inp = input(stri + " [y/n] ")
    
    if (inp.lower() == "y"):
        return True
    d
    return False
        

    

