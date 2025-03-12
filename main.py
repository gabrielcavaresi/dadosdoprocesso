import re
import pyperclip
import tkinter as tk
from tkinter import scrolledtext, messagebox, PhotoImage, Toplevel, Label, Frame
import os
import sys

def caminho_absoluto(relativo):
    """ Retorna o caminho absoluto, compatível com execução via PyInstaller """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relativo)
    return relativo

def formatar_comarca(foro):
    foro = foro.strip()
    if "foro regional" in foro.lower():
        bairro = foro.split("-")[-1].strip()
        return f"CAPITAL ({bairro.upper()})"
    elif "foro de" in foro.lower():
        cidade = foro.split("de")[-1].strip().split("Nº na origem")[0].strip()
        return cidade.upper()
    elif "foro central" in foro.lower():
        return "CAPITAL (CENTRAL)"
    return foro.upper()

def extrair_partes(texto, tipo_processo):
    partes = {}

    # Mapeamento de variantes para nomes únicos
    mapeamento_papeis = {
        "APELAÇÃO": {
            r"Apelante": "APELANTE",
            r"Apelantes?": "APELANTE",
            r"Apelado": "APELADO",
            r"Apelados?": "APELADO",
            r"Apelada": "APELADA",
            r"Apeladas?": "APELADA",
            r"Apelado\(as\)": "APELADO",
            r"Apte/Apdo": "APTE/APDO",
            r"Aptes/Apdos": "APTE/APDO",
            r"Apte/Apda": "APTE/APDA",
            r"Aptes/Apdas": "APTE/APDA",
            r"Apdo/Apte": "APDO/APTE",
            r"Apdos/Aptes": "APDO/APTE",
            r"Apda/Apte": "APDA/APTE",
            r"Apdas/Aptes": "APDA/APTE",
            r"Interessado": "INTERESSADO",
            r"Interessados?": "INTERESSADO",
            r"Interessada": "INTERESSADA",
            r"Interessadas?": "INTERESSADA",
            r"Interessado\(as\)": "INTERESSADO"
        },
        "AGRAVO": {
            r"Agravante": "AGRAVANTE",
            r"Agravantes?": "AGRAVANTE",
            r"Agravado": "AGRAVADO",
            r"Agravados?": "AGRAVADO",
            r"Agravada": "AGRAVADA",
            r"Agravadas?": "AGRAVADA",
            r"Agravado\(as\)": "AGRAVADO",
            r"Interessado": "INTERESSADO",
            r"Interessados?": "INTERESSADO",
            r"Interessada": "INTERESSADA",
            r"Interessadas?": "INTERESSADA",
            r"Interessado\(as\)": "INTERESSADO"
        },
        "EMBARGOS": {
            r"Embargante": "EMBARGANTE",
            r"Embargantes?": "EMBARGANTE",
            r"Embargte": "EMBARGANTE",
            r"Embargtes?": "EMBARGANTE",
            r"Embargdo": "EMBARGADO",
            r"Embargdos?": "EMBARGADO",
            r"Embargda": "EMBARGADA",
            r"Embargdas?": "EMBARGADA",
            r"Embargdo\(as\)": "EMBARGADO",
            r"Embargado": "EMBARGADO",
            r"Embargados?": "EMBARGADO",
            r"Embargada": "EMBARGADA",
            r"Embargadas?": "EMBARGADA",
            r"Embargado\(as\)": "EMBARGADO",
            r"Interessado": "INTERESSADO",
            r"Interessados?": "INTERESSADO",
            r"Interessada": "INTERESSADA",
            r"Interessadas?": "INTERESSADA",
            r"Interessado\(as\)": "INTERESSADO"
        },
        "AÇÃO RESCISÓRIA": {
            r"Autor": "AUTOR",
            r"Autores?": "AUTOR",
            r"Autor\(es\)": "AUTOR",
            r"Autora": "AUTORA",
            r"Autoras?": "AUTORA",
            r"Autora\(s\)": "AUTORA",
            r"Autor\(as\)": "AUTOR",
            r"Autor\(es/as\)": "AUTOR",
            r"Autor\(a\)\(es/as\)": "AUTOR",
            r"Réu": "RÉU",
            r"Réus": "RÉU",
            r"Ré": "RÉU",
            r"Rés": "RÉU",
            r"Interessado": "INTERESSADO",
            r"Interessados?": "INTERESSADO",
            r"Interessada": "INTERESSADA",
            r"Interessadas?": "INTERESSADA",
            r"Interessado\(as\)": "INTERESSADO"
        }
    }

    if tipo_processo in mapeamento_papeis:
        for padrao, papel_normalizado in mapeamento_papeis[tipo_processo].items():
            # Captura todas as ocorrências do padrão
            matches = re.findall(rf"{padrao}:\s*(.*?)\n", texto, re.IGNORECASE)
            if matches:
                if papel_normalizado not in partes:
                    partes[papel_normalizado] = set()  # Usa um conjunto para evitar duplicidades
                for match in matches:
                    # Remove "Justiça Gratuita" e espaços extras
                    nome_limpo = re.sub(r"\(Justiça Gratuita\)", "", match, flags=re.IGNORECASE).strip()
                    partes[papel_normalizado].add(nome_limpo)  # Adiciona o nome limpo ao conjunto

    return partes

def formatar_output(tipo_processo, numero_processo, comarca, partes, juiz):
    output = []

    # Formata o tipo de processo com a tabulação correta
    if tipo_processo in ["APELAÇÃO"]:
        output.append(f"{tipo_processo} Nº\t: {numero_processo}")
    elif tipo_processo in ["AGRAVO", "EDCL"]:
        output.append(f"{tipo_processo} Nº\t\t: {numero_processo}")
    else:
        output.append(f"{tipo_processo} Nº\t: {numero_processo}")

    # Formata a comarca com 2 tabs
    output.append(f"COMARCA\t\t: {comarca}")

    # Formata as partes com a tabulação correta
    for papel, nomes in partes.items():
        # Define o número de tabs com base no papel
        if papel in [
            "APELANTE", "APELANTES", "APELADO", "APELADOS", "APELADA", "APELADAS",
            "APTE/APDO", "APTE/APDA", "APDO/APTE", "APDA/APTE", "AGRAVADA", "AGRAVADO",
        ]:
            tabs = "\t\t"  # 2 tabs
        elif papel in [
            "AGRAVANTE", "AGRAVANTES", "AGRAVADOS", "AGRAVADAS",
            "APTES/APDOS", "APTES/APDAS", "APDOS/APTES", "APDAS/APTES"
        ]:
            tabs = "\t"  # 1 tab
        else:
            tabs = "\t"  # Padrão: 1 tab

        for nome in nomes:
            output.append(f"{papel}{tabs}: {nome.upper()}")

    # Formata o juiz com 2 tabs
    if juiz:
        output.append(f"JUIZ(A)\t\t: {juiz.upper()}")

    return "\n".join(output)

def processar_texto(texto):
    # Extrai o número do processo
    numero_processo = re.search(r"Processo:\s*(\d+-\d+\.\d+\.\d+\.\d+\.\d+)", texto)
    if not numero_processo:
        return "Número do processo não encontrado."
    numero_processo = numero_processo.group(1)

    # Extrai a comarca (captura apenas o nome, excluindo o número do processo)
    comarca = re.search(r"Foro:\s*(.*?)(?:\s*Nº na origem|\n)", texto)
    if not comarca:
        return "Comarca não encontrada."
    comarca = formatar_comarca(comarca.group(1).strip())

    # Extrai o juiz
    juiz = re.search(r"Juiz prolator:\s*(.*?)\n", texto, re.IGNORECASE)
    juiz = juiz.group(1).strip() if juiz else None

    # Extrai a classe do processo
    classe = re.search(r"Classe:\s*(.*?)\n", texto)
    if not classe:
        return "Classe do processo não encontrada."
    classe = classe.group(1).upper()

    # Determina o tipo de processo com base na classe
    tipos_processo = ["APELAÇÃO", "AGRAVO", "EMBARGOS", "AÇÃO RESCISÓRIA"]
    tipo_processo = next((tp for tp in tipos_processo if tp in classe), "Tipo de processo não suportado")
    if tipo_processo == "Tipo de processo não suportado":
        return tipo_processo

    # Extrai as partes do processo
    partes = extrair_partes(texto, tipo_processo)
    return formatar_output(tipo_processo, numero_processo, comarca, partes, juiz)

def processar_e_exibir():
    """
    Obtém o texto de entrada, processa e exibe o resultado.
    """
    try:
        texto = input_text.get("1.0", tk.END)
        output = processar_texto(texto)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, output)
        pyperclip.copy(output)
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao processar o texto: {e}")

def exibir_instrucoes():
    """
    Exibe uma caixa de diálogo com as instruções e a imagem de exemplo.
    """
    instrucao_janela = Toplevel(root)
    instrucao_janela.title("Instruções")
    
    label_instrucao = Label(instrucao_janela, text='''Vá até a aba "Dados do Processo" e selecione todo o texto entre "Processo" (à direita do desenho de uma estrela) e até o símbolo "DJE" do último advogado cadastrado.''', wraplength=1200, justify="left", font=("Times New Roman", 12))
    label_instrucao.pack(pady=10)

    try:
        img = PhotoImage(file=caminho_absoluto("instruções.png"))
        img_label = Label(instrucao_janela, image=img)
        img_label.image = img  # Mantém a referência da imagem para evitar descarte pelo garbage collector
        img_label.pack(pady=5)
    except:
        Label(instrucao_janela, text="(Imagem 'instruções.png' não encontrada)", font=("Times New Roman", 10)).pack()

def copiar_output():
    """
    Copia o conteúdo do output para a área de transferência.
    """
    texto = output_text.get("1.0", tk.END).strip()
    if texto:
        pyperclip.copy(texto)

def limpar_campos():
    """
    Limpa os campos de entrada e saída.
    """
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)

root = tk.Tk()
root.title("Gerador de Cabeçalhos - SAJ SG5/Word")
root.configure(bg="#003366")

# Instruções antes da caixa de entrada
frame_instrucao = tk.Frame(root, bg="#003366")
frame_instrucao.pack(pady=5)

instrucao_label = tk.Label(frame_instrucao, text="Insira os dados do processo conforme as instruções.", fg="white", bg="#003366", font=("Times New Roman", 14, "bold"))
instrucao_label.pack(side="left")

icone_ajuda = tk.Button(frame_instrucao, text="?", command=exibir_instrucoes, font=("Times New Roman", 12), width=2, height=1, bg="#000080", fg="white", relief="raised", bd=2)
icone_ajuda.pack(side="left", padx=5)

input_text = scrolledtext.ScrolledText(root, width=80, height=10, wrap=tk.WORD, bg="#002244", fg="white", font=("Times New Roman", 12))
input_text.pack(pady=5)

# Frame para os botões lado a lado
frame_botoes = Frame(root, bg="#003366")
frame_botoes.pack(pady=5)

processar_btn = tk.Button(frame_botoes, text="Formatar", command=processar_e_exibir, bg="#00509e", fg="white", font=("Times New Roman", 12))
processar_btn.pack(side="left", padx=5)

copiar_btn = tk.Button(frame_botoes, text="Copiar", command=copiar_output, bg="#00509e", fg="white", font=("Times New Roman", 12))
copiar_btn.pack(side="left", padx=5)

limpar_btn = tk.Button(frame_botoes, text="Limpar", command=limpar_campos, bg="#00509e", fg="white", font=("Times New Roman", 12))
limpar_btn.pack(side="left", padx=5)

# Título antes do output
output_label = tk.Label(root, text="Cabeçalho formatado", fg="white", bg="#003366", font=("Times New Roman", 14, "bold"))
output_label.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, width=80, height=10, wrap=tk.WORD, bg="#002244", fg="white", font=("Times New Roman", 12))
output_text.pack(pady=5)

# Aviso final
aviso_label = tk.Label(
    root,
    text="ATENÇÃO: este programa foi desenvolvido de maneira independente e não é afiliado ou vinculado ao Tribunal de Justiça de São Paulo, à Softplan ou ao SAJ. Caso tenha dúvidas ou queira apontar erros ou fazer sugestões, não hesite em enviar um e-mail para gcavaresi@tjsp.jus.br. Se quiser contribuir, acesse https://github.com/gabrielcavaresi",
    bg="#003366",
    fg="white",
    font=("Times New Roman", 11),
    wraplength=600,
    justify=tk.LEFT
)
aviso_label.pack(pady=5)  # Reduzi o espaço aqui também

# Versão
versao_label = tk.Label(root, text="Versão 1.001", bg="#003366", fg="white", font=("Times New Roman", 12))
versao_label.pack(pady=2)  # Reduzi o espaço entre "Versão" e "Atenção"

root.mainloop()