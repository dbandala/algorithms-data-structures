# Hay tres tipos de ediciones que se pueden hacer en un string: insertar un caracter, borrar un caracter o reemplazar un caracter. 
# Dados dos strings, escriba una función que revise si hay cero o una edición y devuelva TRUE en ese caso. De lo contrario devuelve FALSE

# EJEMPLOS: 
# pale, ple -> true
# pales, pale -> true
# pale, bale -> true
# pale, bae -> false
# abc, acb -> false

def is_edited(str1, str2):
    # base scenarios
    n1 = len(str1)
    n2 = len(str2)

    # at least two chars have been deleted/inserted
    if abs(n1-n2)>2:
        return False
    
    # completely equal
    if str1==str2: return True
    
    # count differences between strings
    pointer1 = 0
    pointer2 = 0
    differences = 0
    while pointer1<n1 and pointer2<n2:
        if str1[pointer1]==str2[pointer2]:
            pointer1 += 1
            pointer2 += 1
        else:
            differences += 1
            if n1==n2:
                pointer1 += 1
                pointer2 += 1
            elif n1<n2:
                pointer2 += 1
            else:
                pointer1 += 1

        if differences>1:
            return False
    return True



print(is_edited("pale", "ple"))
print(is_edited("pales", "pale"))
print(is_edited("abc", "acb"))
print(is_edited("pale", "bae"))

    

