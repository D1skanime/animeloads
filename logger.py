import sys

def log(message, pushbullet=None):
    """
    Gibt eine Nachricht aus und sendet sie optional per Pushbullet.
    :param message: Die auszugebende Nachricht.
    :param pushbullet: Pushbullet-Objekt, falls eine Benachrichtigung gesendet werden soll.
    """
    try:
        if pushbullet:
            pushbullet.push_note("anibot", message)
    except Exception:
        pass  # Falls Pushbullet fehlschlägt, einfach ignorieren
    print(message)

if __name__ == "__main__":
    print("Teste Logging-Modul...")
    log("Das ist eine Testnachricht")