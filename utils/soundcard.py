import alsaaudio

def find_card_by_name(name:str) -> int :
    for i in alsaaudio.card_indexes():
        if alsaaudio.card_name(i)[0] == name:
            return i
    return -1
