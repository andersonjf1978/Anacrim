# Importações necessárias
import flet as ft  # Framework para criar interfaces gráficas
import os
import requests
import uuid
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopos de acesso para autenticação com a conta Google
SCOPES = [
    "openid",  # Identidade
    "https://www.googleapis.com/auth/userinfo.profile",  # Perfil do usuário
    "https://www.googleapis.com/auth/userinfo.email",    # E-mail do usuário
    "https://www.googleapis.com/auth/spreadsheets",      # Acesso ao Google Sheets
    "https://www.googleapis.com/auth/drive.file"         # Acesso a arquivos do Google Drive
]

# IDs fixos (da planilha e da pasta de imagens no Google Drive)
SPREADSHEET_ID = "1kYRh_0OQIln8TWWbvk7XS7PmUx1Qqx0oVUr_3XH4U2k"
DRIVE_FOLDER_ID = "1kjg5BfGqTKaqrOWQwinRBawdMmlsWA5r"

# Lista de campos que serão exibidos no resumo dos cadastros
CAMPOS_EXIBIR = ["ID", "TOP10", "NOME", "MAE", "RG", "SEXO", "CUTIS", "SIT_RUA", "FOTO"]

# Função de login com Google
def login_google():
    creds = None
    # Se já existe o token de autenticação salvo localmente, reutiliza
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # Se não for válido ou não existir, abre fluxo de autenticação
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret.json',  # Arquivo com credenciais da API
            SCOPES,
            redirect_uri='http://localhost:8550/oauth2callback'
        )
        creds = flow.run_local_server(port=8550, access_type='offline', prompt='consent')
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Obtém e imprime e-mail do usuário autenticado
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            headers={'Authorization': f'Bearer {creds.token}'}
        )
        user_info = response.json()
        print(f"✅ Usuário logado com: {user_info['email']}")
    except Exception as e:
        print(f"Erro ao obter informações do usuário: {e}")
    return creds

# Lê a planilha e retorna o maior valor da coluna de ID
def pegar_maior_id(creds):
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CADASTRO!B2:B"  # Coluna B = ID
    ).execute()
    valores = result.get('values', [])
    ids = []
    for v in valores:
        try:
            ids.append(int(v[0]))  # Converte para inteiro
        except:
            pass
    return max(ids) if ids else 0

# Escreve um novo registro na planilha
def escrever_planilha(creds, id_, top10, nome, apelido, nascimento, idade, uf, naturalidade, sexo, estadocivil, cutis, profissao, mae, nm_pai, rg, cpf, escolaridade, rua_residencia,
                       nr_residencia, compl_residencia, bairro_residencia, municipio_residencia, dados_p2, sit_rua, infopen, tatuagem, rua_trabalho, nr_trabalho, bairro_trabalho, 
                       municipio_trabalho, faccao, crimes_env, atuação, comparsa, veículos, situacao_prisional, possui_inquerito, possui_processo_crime, demais_info, foto,
                         endereco_referencia, criadopor, criadoem, mês, ano):
    
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # Ordem dos campos deve respeitar a mesma sequência da planilha.
    values = [[id_, top10, nome, apelido, nascimento, idade, uf, naturalidade, sexo, estadocivil, cutis, profissao, mae, nm_pai, rg, cpf, escolaridade, rua_residencia,
                nr_residencia, compl_residencia, bairro_residencia, municipio_residencia, dados_p2, sit_rua, infopen, tatuagem, rua_trabalho, nr_trabalho, bairro_trabalho, 
                municipio_trabalho, faccao, crimes_env, atuação, comparsa, veículos, situacao_prisional, possui_inquerito, possui_processo_crime, demais_info, foto,
                endereco_referencia, criadopor, criadoem, mês, ano]]
    
    body = {'values': values}
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="CADASTRO!B2",  # A partir da célula B2
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body=body
    ).execute()
    return result

def escrever_planilha_dict(creds, dados, page):
    page.snack_bar = ft.SnackBar(ft.Text("✅ Cadastro salvo com sucesso!"))
    page.snack_bar.open = True
    page.update()
    campos_ordenados = [
        "id_", "top10", "nome", "apelido", "nascimento", "idade", "uf", "naturalidade", "sexo", "estadocivil", "cutis", "profissao", "mae", "nm_pai", "rg", "cpf", "escolaridade",
        "rua_residencia", "nr_residencia", "compl_residencia", "bairro_residencia", "municipio_residencia", "dados_p2", "sit_rua", "infopen", "tatuagem", "rua_trabalho", "nr_trabalho",
        "bairro_trabalho", "municipio_trabalho", "faccao", "crimes_env", "atuação", "comparsa", "veículos", "situacao_prisional", "possui_inquerito", "possui_processo_crime",
        "demais_info", "foto", "endereco_referencia", "criadopor", "criadoem", "mês", "ano"
    ]

    # Garante que todos os campos existam, com valor ou vazioV
    valores = [dados.get(campo, "") for campo in campos_ordenados]

    # Chamada da função principal
    escrever_planilha(creds, *valores)


# Envia imagem para o Google Drive
def upload_drive(creds, file_path):
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {
        'name': os.path.basename(file_path),   # Nome do arquivo
        'parents': [DRIVE_FOLDER_ID]           # Pasta onde será salvo
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('id')

# Lê os últimos cadastros da planilha
def ler_ultimos_cadastros(creds, max_rows=5):
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="CADASTRO!B2:BG50000"  # Intervalo amplo da aba CADASTRO
    ).execute()
    values = result.get('values', [])
    return values[-max_rows:]  # Retorna apenas os últimos N registros

# Função principal da interface
def main(page: ft.Page):
    page.title = "Anacrim"
    page.scroll = ft.ScrollMode.ADAPTIVE  # Isso ativa o scroll da página, se necessário

    creds = None
    photo_url = ""

    # Campos do formulário.Independe de ordem
   
    txt_nome = ft.TextField(label="Nome", autofocus=True)
    txt_apelido = ft.TextField(label="Apelido", autofocus=True)
    txt_mae = ft.TextField(label="Mãe")
    txt_nascimento = ft.TextField(label="Nascimento")
    txt_uf = ft.TextField(label="UF")
    txt_naturalidade = ft.TextField(label="Naturalidade")
    txt_rg = ft.TextField(label="RG")
    txt_cpf = ft.TextField(label="CPF")
    txt_endereco_referencia = ft.TextField(label="Possui endereço de referência?")
    txt_rua_residencia = ft.TextField(label="Endereço")
    txt_nr_residencia = ft.TextField(label="Nr.")
    txt_compl_residencia = ft.TextField(label="Complemento")
    txt_bairro_residencia = ft.TextField(label="Bairro")
    txt_municipio_residencia = ft.TextField(label="Município")
    txt_infopen = ft.TextField(label="INFOPEN")
    txt_tatuagem = ft.TextField(label="Tatuagem")
    txt_demais_info = ft.TextField(label="Demais informações importantes")  # Pessoa em situação de rua   
    txt_comparsa = ft.TextField(label="Comparsa")  # Pessoa em situação de rua

    dropdown_sexo = ft.Dropdown(label="Sexo", options=[
        ft.dropdown.Option("Masculino"),
        ft.dropdown.Option("Feminino"),
        ft.dropdown.Option("Outro")
    ])
    dropdown_cutis = ft.Dropdown(label="Cutis", options=[
        ft.dropdown.Option("Preto"),
        ft.dropdown.Option("Pardo"),
        ft.dropdown.Option("Branco")
    ])

    dropdown_sit_rua = ft.Dropdown(label="Situação de Rua?", options=[
        ft.dropdown.Option("Sim"),
        ft.dropdown.Option("Não")    
    ])

    dropdown_top10 = ft.Dropdown(label="TOP10", width=150, options=[
        ft.dropdown.Option("Sim"),
        ft.dropdown.Option("Não")
    ])

    dropdown_faccao = ft.Dropdown(label="Faccionado?", options=[
        ft.dropdown.Option("SEM INFORMAÇÃO"),
        ft.dropdown.Option("NÃO"),
        ft.dropdown.Option("CV"),
        ft.dropdown.Option("TCP"),
        ft.dropdown.Option("PCC"),
        ft.dropdown.Option("5M"),
        ft.dropdown.Option("ADA"),
        ft.dropdown.Option("OUTRO")
    ])

    # Lista dos crimes
    crimes_labels = [
        "HOMICÍDIO",
        "ROUBO",
        "FURTO",
        "LESÃO CORPORAL",
        "AMEAÇA",
        "TRÁFICO DE DROGAS",
        "RECEPTAÇÃO",
        "AGRESSÃO",
        "VIAS DE FATO"
    ]

    # Criar dicionário de checkboxes
    checkboxes_crimes = {label: ft.Checkbox(label=label) for label in crimes_labels}

    # Colocar todos os checkboxes na coluna
    checkbox_crimes_env = ft.Column(
        [ft.Text("Crimes?")] + list(checkboxes_crimes.values())
    )
    
   # Lista das companhias
    atuacao_labels = [
        "30ª Cia",
        "31ª Cia",
        "70ª Cia",
        "135ª Cia",
        "136ª Cia"
    ]

    # Criar dicionário de checkboxes
    checkboxes_atuacao = {label: ft.Checkbox(label=label) for label in atuacao_labels}

    # Colocar todos os checkboxes na coluna
    checkbox_atuacao = ft.Column(
        [ft.Text("Atuação?")] + list(checkboxes_atuacao.values())
    )




    # Selecionador de arquivos (imagem)
    upload_file = ft.FilePicker()
    page.overlay.append(upload_file)

    img_preview = ft.Image(width=150, height=150)  # Imagem de visualização

    lista_cadastros = ft.ListView(expand=True, spacing=10, auto_scroll=True)  # Lista com últimos cadastros

    # Botão de login
    def login_click(e):
        nonlocal creds
        creds = login_google()
        btn_login.text = "Logado com Google"
        btn_login.disabled = True
        page.update()
        carregar_ultimos()  # Após login, carrega últimos cadastros

    # Atualiza visualização dos últimos cadastros
    def carregar_ultimos():
        if creds:
            registros = ler_ultimos_cadastros(creds)
            lista_cadastros.controls.clear()
            for r in registros:
                linha = ft.Row(wrap=True, controls=[
                    ft.Text(r[i]) if i < len(r) and i != 8 else  # Campos de texto
                    ft.Image(src=r[8], width=50, height=50) if i == 8 and len(r) > 8 and r[8] else ft.Text("-")
                    for i in range(len(CAMPOS_EXIBIR))
                ])
                lista_cadastros.controls.append(linha)
            page.update()

    # Quando o usuário clicar em salvar
    def salvar_click(e):
        nonlocal photo_url

        if not creds:
            e.page.snack_bar = ft.SnackBar(ft.Text("Faça login primeiro!"))
            e.page.snack_bar.open = True
            e.page.update()
            return

        # Coleta dados do formulário
        top10 = dropdown_top10.value.upper() if dropdown_top10.value else "N"
        nome = txt_nome.value
        apelido = txt_apelido.value
        nascimento = txt_nascimento.value
        uf = txt_uf.value
        naturalidade = txt_naturalidade.value
        cpf = txt_cpf.value
        endereco_referencia = txt_endereco_referencia.value
        rua_residencia = txt_rua_residencia.value
        nr_residencia = txt_nr_residencia.value
        compl_residencia = txt_compl_residencia.value
        bairro_residencia = txt_bairro_residencia.value
        municipio_residencia = txt_municipio_residencia.value
        infopen = txt_infopen.value
        tatuagem = txt_tatuagem.value
        faccao = dropdown_faccao.value
        mae = txt_mae.value
        rg = txt_rg.value
        sexo = dropdown_sexo.value
        cutis = dropdown_cutis.value
        sit_rua = dropdown_sit_rua.value
        comparsa = txt_comparsa.value
        demais_info = txt_demais_info.value

        crimes_env = [label for label, checkbox in checkboxes_crimes.items() if checkbox.value]
        crimes_env_str = ", ".join(crimes_env)

        atuacao_selecionada = [label for label, checkbox in checkboxes_atuacao.items() if checkbox.value]
        atuacao_str = ", ".join(atuacao_selecionada)

        # Valida campos obrigatórios
        if not nome or not mae or not rg or not sexo:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os campos obrigatórios!"))
            page.snack_bar.open = True
            page.update()
            return

        # Upload da imagem, se houver
        if upload_file.result:
            file_path = upload_file.result.files[0].path
            file_id = upload_drive(creds, file_path)
            photo_url = f"https://drive.google.com/uc?id={file_id}"
            img_preview.src = photo_url
            img_preview.update()
        else:
            photo_url = ""

        # Gera novo ID sequencial
        maior_id = pegar_maior_id(creds)
        novo_id = maior_id + 1

        # Monta dicionário com todos os dados para salvar
        from datetime import datetime
        now = datetime.now()
        usuario_logado = "ANDERSON"  # Pode tornar dinâmico depois

        # Cálculo da idade
        idade = ""
        try:
            nascimento_dt = datetime.strptime(nascimento, "%d/%m/%Y")
            hoje = datetime.today()
            idade = hoje.year - nascimento_dt.year - ((hoje.month, hoje.day) < (nascimento_dt.month, nascimento_dt.day))
        except:
            idade = ""

        mes = datetime.now().strftime("%m")
        ano = datetime.now().strftime("%Y")


        dados = {
            "id_": str(novo_id),
            "top10": top10,
            "nome": nome,
            "apelido": apelido,
            "nascimento": nascimento,
            "idade": idade,  # Pode ser calculada depois
            "uf": uf,
            "naturalidade": naturalidade,
            "sexo": sexo,
            "estadocivil": "",  # Ainda não pego
            "cutis": cutis,
            "profissao": "",  # Ainda não pego
            "mae": mae,
            "nm_pai": "",  # Ainda não pego
            "rg": rg,
            "cpf": cpf,
            "escolaridade": "",  # Ainda não pego
            "rua_residencia": rua_residencia,
            "nr_residencia": nr_residencia,
            "compl_residencia": compl_residencia,
            "bairro_residencia": bairro_residencia,
            "municipio_residencia": municipio_residencia,
            "dados_p2": "",  # Ainda não pego
            "sit_rua": sit_rua,
            "infopen": infopen,
            "tatuagem": tatuagem,
            "rua_trabalho": "",  # Ainda não pego
            "nr_trabalho": "",   # Ainda não pego
            "bairro_trabalho": "",  # Ainda não pego
            "municipio_trabalho": "",  # Ainda não pego
            "faccao": faccao,
            "crimes_env": crimes_env_str,
            "atuação": atuacao_str,
            "comparsa": comparsa,
            "veículos": "",  # Ainda não pego
            "situacao_prisional": "",  # Ainda não pego
            "possui_inquerito": "",  # Ainda não pego
            "possui_processo_crime": "",  # Ainda não pego
            "demais_info": demais_info,
            "foto": photo_url,
            "endereco_referencia": endereco_referencia,
            "criadopor": usuario_logado,
            "criadoem": now.strftime("%Y-%m-%d %H:%M:%S"),
            "mês": now.strftime("%m"),
            "ano": now.strftime("%Y"),
        }

        # Salva os dados na planilha
        escrever_planilha_dict(creds, dados, e.page)

        carregar_ultimos()  # Atualiza a lista com o novo cadastro

    # Mostra imagem local ao selecionar arquivo
    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            img_preview.src = file_path
            img_preview.update()

    # Botões e elementos da interface
    btn_login = ft.ElevatedButton("Entrar com Google", on_click=login_click)
    btn_salvar = ft.ElevatedButton("Salvar Cadastro", on_click=salvar_click)
    btn_upload = ft.ElevatedButton("Selecionar Foto", on_click=lambda _: upload_file.pick_files())

    # Adiciona todos os componentes à tela. ORDEM NA TELA.
    page.add(
        btn_login,
        txt_nome,
        txt_apelido,
        txt_mae,
        txt_nascimento,
        txt_uf,
        txt_naturalidade,
        txt_rg,
        txt_cpf,
        txt_infopen,
        ft.Row([dropdown_sexo, dropdown_top10], spacing=20),
        ft.Row([dropdown_cutis, dropdown_sit_rua], spacing=20),
        txt_tatuagem,
        txt_comparsa,
        dropdown_faccao,
        checkbox_crimes_env,
        checkbox_atuacao,
        txt_endereco_referencia,
        txt_rua_residencia,
        txt_nr_residencia,
        txt_compl_residencia,
        txt_bairro_residencia,
        txt_municipio_residencia,
        txt_demais_info,
        btn_upload,
        img_preview,
        btn_salvar,
        ft.Text("Últimos cadastros: (ID, TOP10, Nome, Mãe, RG, Sexo, Cutis, Situação de Rua, Foto)"),
        lista_cadastros,
        
    )

    # Vincula função ao resultado do seletor de arquivo
    upload_file.on_result = pick_files_result

# Roda o app Flet
if __name__ == "__main__":
    ft.app(target=main)
