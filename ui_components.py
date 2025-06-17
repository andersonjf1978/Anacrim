import flet as ft

def criar_campos():
    return (
        ft.TextField(label="Nome"),
        ft.TextField(label="Apelido"),
        ft.TextField(label="Mãe"),
        ft.TextField(label="Nascimento"),
        ft.TextField(label="UF"),
        ft.TextField(label="Naturalidade"),
        ft.TextField(label="RG"),
        ft.TextField(label="CPF"),
        ft.TextField(label="Infopen"),
        ft.TextField(label="Tatuagem"),
        ft.TextField(label="Comparsa"),
        ft.TextField(label="Endereço de Referência"),
        ft.TextField(label="Rua Residência"),
        ft.TextField(label="Nº Residência"),
        ft.TextField(label="Complemento"),
        ft.TextField(label="Bairro"),
        ft.TextField(label="Município"),
        ft.TextField(label="Demais Informações"),
    )

def criar_dropdowns():
    return (
        ft.Dropdown(label="Sexo", options=[ft.dropdown.Option("M"), ft.dropdown.Option("F")]),
        ft.Dropdown(label="Top10", options=[ft.dropdown.Option("S"), ft.dropdown.Option("N")]),
        ft.Dropdown(label="Cutis", options=[]),
        ft.Dropdown(label="Situação de Rua", options=[]),
        ft.Dropdown(label="Facção", options=[]),
    )

def criar_checkboxes():
    crimes_env = {}
    atuacao = {}
    checkbox_crimes_env = ft.Column()
    checkbox_atuacao = ft.Column()
    return crimes_env, atuacao, checkbox_crimes_env, checkbox_atuacao

def criar_lista_cadastros():
    return ft.ListView(expand=True, spacing=10, auto_scroll=True)

def criar_snackbar(page, texto):
    page.snack_bar = ft.SnackBar(ft.Text(texto))
    page.snack_bar.open = True
    page.update()
