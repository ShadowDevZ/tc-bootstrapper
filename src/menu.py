l = ["menu.com/f1.a", "menu.com/f2.b", "menu.com/f3.c"]
#
#lst -> list of links
# -> list of extension which are permitted to be displayed


def DisplayMenu(title, lst, filter):
    print(">>> Setting up " + title)
    for i in range(len(lst)):
        print("[{0}] ({1})".format(str(i), lst[i]))
    inp = ""
    while (True):
        try:
            inp = int(input("Choice: "))
            if (inp >= 0 and inp <= i):
                break
        except ValueError:
            continue
    
#
# str text
# return: bool (yes/no)
def ConfDialog(stri):
    
    inp = ""
    while (inp.lower() != 'y' and inp.lower() != 'n'):
        inp = input(stri + " [y/n] ")
        

    

