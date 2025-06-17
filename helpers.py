from datetime import datetime

def calcular_idade(nascimento_str):
    try:
        nascimento_dt = datetime.strptime(nascimento_str, "%d/%m/%Y")
        hoje = datetime.today()
        return hoje.year - nascimento_dt.year - ((hoje.month, hoje.day) < (nascimento_dt.month, nascimento_dt.day))
    except:
        return ""
