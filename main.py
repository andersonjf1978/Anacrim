import flet as ft
from auth import login_google
from sheet_service import ler_ultimos_cadastros, escrever_planilha_dict, pegar_maior_id
from drive_service import upload_drive
from ui_components import (
    criar_campos, criar_dropdowns, criar_checkboxes, criar_lista_cadastros, criar_snackbar
)
from helpers import calcular_idade
from datetime import datetime

def main(page: ft.Page):
    creds = None
    photo_url = ""

    # Campos da interface
    (
        txt_nome, txt_apelido, txt_mae, txt_nascimento, txt_uf, txt_naturalidade,
        txt_rg, txt_cpf, txt_infopen, txt_tatuagem, txt_comparsa, txt_endereco_referencia,
        txt_rua_residencia, txt_nr_residencia, txt_compl_residencia, txt_bairro_residencia,
        txt_municipio_residencia, txt_demais_info
    ) = criar_campos()

    dropdown_sexo, dropdown_top10, dropdown_cutis, dropdown_sit_rua, dropdown_faccao = criar_dropdowns()
    checkboxes_crimes, checkboxes_atuacao, checkbox_crimes_env, checkbox_atuacao = criar_checkboxes()

    upload_file = ft.FilePicker()
    page.overlay.append(upload_file)
    img_preview = ft.Image(width=150, height=150)
    lista_cadastros = criar_lista_cadastros()

    def carregar_ultimos():
        if creds:
            registros = ler_ultimos_cadastros(creds)
            lista_cadastros.controls.clear()
            for r in registros:
                linha = ft.Row(wrap=True, controls=[
                    ft.Text(r[i]) if i < len(r) and i != 8 else
                    ft.Image(src=r[8], width=50, height=50) if i == 8 and len(r) > 8 and r[8] else ft.Text("-")
                    for i in range(9)
                ])
                lista_cadastros.controls.append(linha)
            page.update()

    def login_click(e):
        nonlocal creds
        creds = login_google()
        btn_login.text = "Logado com Google"
        btn_login.disabled = True
        page.update()
        carregar_ultimos()

    def salvar_click(e):
        nonlocal photo_url
        if not creds:
            criar_snackbar(page, "Faça login primeiro!")
            return

        top10 = dropdown_top10.value.upper() if dropdown_top10.value else "N"
        nome = txt_nome.value
        mae = txt_mae.value
        rg = txt_rg.value
        sexo = dropdown_sexo.value

        if not nome or not mae or not rg or not sexo:
            criar_snackbar(page, "Preencha todos os campos obrigatórios!")
            return

        if upload_file.result:
            file_path = upload_file.result.files[0].path
            file_id = upload_drive(creds, file_path)
            photo_url = f"https://drive.google.com/uc?id={file_id}"
            img_preview.src = photo_url
            img_preview.update()
        else:
            photo_url = ""

        nascimento = txt_nascimento.value
        idade = calcular_idade(nascimento)

        maior_id = pegar_maior_id(creds)
        novo_id = maior_id + 1
        now = datetime.now()
        usuario_logado = "ANDERSON"

        dados = {
            "id_": str(novo_id),
            "top10": top10,
            "nome": nome,
            "mae": mae,
            "rg": rg,
            "sexo": sexo,
            "nascimento": nascimento,
            "idade": idade,
            "foto": photo_url,
            "criadopor": usuario_logado,
            "criadoem": now.strftime("%Y-%m-%d %H:%M:%S"),
            "mês": now.strftime("%m"),
            "ano": now.strftime("%Y"),
            # Adicione os demais campos se quiser
        }

        escrever_planilha_dict(creds, dados, e.page)
        carregar_ultimos()

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            img_preview.src = file_path
            img_preview.update()

    btn_login = ft.ElevatedButton("Entrar com Google", on_click=login_click)
    btn_salvar = ft.ElevatedButton("Salvar Cadastro", on_click=salvar_click)
    btn_upload = ft.ElevatedButton("Selecionar Foto", on_click=lambda _: upload_file.pick_files())

    page.add(
         
        ft.Column(
            [
                btn_login,
                txt_nome, txt_apelido, txt_mae, txt_nascimento, txt_uf, txt_naturalidade,
                txt_rg, txt_cpf, txt_infopen,
                ft.Row([dropdown_sexo, dropdown_top10]),
                ft.Row([dropdown_cutis, dropdown_sit_rua]),
                txt_tatuagem, txt_comparsa, dropdown_faccao,
                checkbox_crimes_env, checkbox_atuacao,
                txt_endereco_referencia, txt_rua_residencia, txt_nr_residencia,
                txt_compl_residencia, txt_bairro_residencia, txt_municipio_residencia,
                txt_demais_info, btn_upload, img_preview, btn_salvar,
                ft.Text("Últimos cadastros:"), lista_cadastros,
            ],
            expand=True,
            spacing= 10,
        ),
        expand=True,
        scroll="auto",
        )
    


    upload_file.on_result = pick_files_result

if __name__ == "__main__":
    ft.app(target=main)
