import antlr4
import re


# Define a custom error listener
class CustomErrorListener(antlr4.error.ErrorListener.ErrorListener):
    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # error en español
        translations = {
            r"missing (.+) at (.+)": r"falta \1 en \2",
            r"mismatched input (.+) expecting (.+)": r"entrada no coincidente \1, se esperaba \2",
            r"extraneous input '(.+)' expecting (.+)": r"entrada innecesaria '\1', se esperaba \2",
            # Agrega más traducciones aquí si lo deseas
        }

        # Buscar coincidencias con las expresiones regulares y traducir el mensaje
        for pattern, translation in translations.items():
            msg = re.sub(pattern, translation, msg)

        # Personalizar el mensaje de error aquí
        custom_msg = f"Error en la línea {line}, columna {column}, mensaje: {msg}"
        self.errors.append(custom_msg)

    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass

    def get_errors(self):
        return self.errors
