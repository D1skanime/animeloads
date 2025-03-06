def compare(inputstring, validlist):
    """
    Überprüft, ob ein Wert aus einer Liste im Eingabestring enthalten ist.
    :param inputstring: Der zu überprüfende String.
    :param validlist: Eine Liste von gültigen Werten.
    :return: True, wenn ein Element aus validlist im inputstring enthalten ist, sonst False.
    """
    for v in validlist:
        if v.lower() in inputstring.lower():
            return True
    return False

if __name__ == "__main__":
    print("Teste Utils-Modul...")
    test_string = "Ja, ich möchte fortfahren"
    valid_words = {"j", "ja", "yes", "y"}
    print(f"Test: {compare(test_string, valid_words)}")  # Sollte True ausgeben