import sys
import os

def printException(e):
    """
    Gibt detaillierte Informationen zu einer Exception aus.
    :param e: Die aufgetretene Exception.
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print("Error:")
    print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == "__main__":
    print("Teste Fehlerbehandlungsmodul...")
    try:
        1 / 0  # Erzeugt absichtlich einen Fehler zum Testen
    except Exception as e:
        printException(e)