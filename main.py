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

def processar_texto(texto):
    """
    Processa o texto cru e retorna o output formatado.
    """
    numero_processo = re.search(r"Processo:\s*(\d+-\d+\.\d+\.\d+\.\d+\.\d+)", texto)
    if not numero_processo:
        return "Número do processo não encontrado."
    numero_processo = numero_processo.group(1)

    comarca = re.search(r"Foro:\s*(.*?)\n", texto)
    if not comarca:
        return "Comarca não encontrada."
    comarca = comarca.group(1).strip().upper()

    juiz = re.search(r"Juiz prolator:\s*(.*?)\n", texto, re.IGNORECASE)
    juiz = juiz.group(1).strip() if juiz else None

    return f"Processo Nº: {numero_processo}\nComarca: {comarca}\nJuiz(a): {juiz or 'Não informado'}"

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
