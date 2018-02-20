# -*- coding: utf8 -*-
def remove_dangerous_symbols_exec(str_for_eval):
    print ("str before cleaning |" + str_for_eval + "|")
    str_for_eval = str.replace(str_for_eval, "_", "")
    str_for_eval = str.replace(str_for_eval, "\"", "")
    str_for_eval = str.replace(str_for_eval, "'", "")
    str_for_eval = str.replace(str_for_eval, "`", "")
    str_for_eval = str.replace(str_for_eval, "’", "")
    str_for_eval = str.replace(str_for_eval, "‘", "")
    str_for_eval = str.replace(str_for_eval, "os.", "")
    str_for_eval = str_for_eval[:30]
    print ("clean str |" + str_for_eval + "|")

    return str_for_eval

if __name__ == '__main__':
    str_for_eval = "os.system(‘rm -rf /’)"
    print ("----Dangerous code for eval -----")
    print ("1. |" + str_for_eval + "| ")
    print ("\t -> |" + remove_dangerous_symbols_exec(str_for_eval) + "|")

