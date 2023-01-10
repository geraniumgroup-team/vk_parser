from config import credentials, public_token, log_parser

attemp = 0

def alala():
    global attemp

    attemp += 1

    if attemp > len(credentials) - 1:
        attemp = 0

    print(credentials[attemp]['login'], credentials[attemp]['password'])

for i in range(10):
    alala()