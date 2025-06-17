def ler_ultimos_cadastros(creds):
    # Faz leitura na planilha Google Sheets
    print("Lendo últimos cadastros da planilha...")
    return [
        ["1", "N", "João", "Maria", "123", "M", "Branca", "Não", ""],
        ["2", "N", "Ana", "Josefa", "456", "F", "Parda", "Sim", ""],
    ]

def escrever_planilha_dict(creds, dados, page):
    print(f"Gravando no Google Sheets: {dados}")

def pegar_maior_id(creds):
    # Simulação de pegar maior ID
    return 2
