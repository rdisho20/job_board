def validate_new_password(password):
    '''
    Password must be at least 8 characters long
    Must include at least 1 number
    Must include upper and lowercase letters
    Must include at least 1 symbol
    d- leave as string, checking against valid characters
    '''
    numbers = '1234567890'
    letters = 'abcdefghijklmnopqrstuvwxyz'
    symbols = '_!@#$%^&*;:,.<>?`~ '
    number_count = 0
    symbol_count = 0
    lower_count = 0
    upper_count = 0

    if len(password) < 8:
        return False

    for char in password:
        if (char not in numbers and
            char not in letters and
            char not in letters.upper() and
            char not in symbols):
            return False
        
        elif char in letters:
            lower_count += 1
        
        elif char in letters.upper():
            upper_count += 1

        elif char in numbers:
            number_count += 1
        
        elif char in symbols:
            symbol_count += 1
    
    if (number_count > 0 and symbol_count > 0 and
        lower_count > 0 and upper_count > 0):
        return True
    
    return False

