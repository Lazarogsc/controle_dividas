import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import sqlite3

def carregar_dividas(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, 'r') as f:
            return json.load(f)
    return {}

def salvar_dividas(arquivo, dividas):
    with open(arquivo, 'w') as f:
        json.dump(dividas, f, indent=4)

def adicionar_divida(mes):
    descricao = simpledialog.askstring("Descrição da Dívida", "Insira a descrição da dívida:")
    if descricao:
        root.update()  
        valor = simpledialog.askfloat("Valor da Dívida", "Insira o valor da dívida:")
        if valor is not None:
            dividas_por_mes[mes].append((descricao, valor))
            salvar_dividas(arquivo_dividas, dividas_por_mes)
            atualizar_lista_dividas(mes)

def atualizar_lista_dividas(mes):
    listbox.delete(0, tk.END)
    for descricao, valor in dividas_por_mes[mes]:
        listbox.insert(tk.END, f"{descricao}: R$ {valor:.2f}")
    total_mes = sum(valor for _, valor in dividas_por_mes[mes])
    label_total_mes.config(text=f"Total {mes}: R$ {total_mes:.2f}")

    total_geral = sum(sum(valor for _, valor in dividas) for dividas in dividas_por_mes.values())
    label_total_geral.config(text=f"Total Geral: R$ {total_geral:.2f}")

def mudar_mes(*args):
    mes = combo_meses.get()
    atualizar_lista_dividas(mes)

def zerar_dividas(mes):
    if messagebox.askyesno("Confirmação", f"Tem certeza que deseja zerar as dívidas de {mes}?"):
        dividas_por_mes[mes] = []
        salvar_dividas(arquivo_dividas, dividas_por_mes)
        atualizar_lista_dividas(mes)

def marcar_como_paga(mes):
    selecionado = listbox.curselection()
    if selecionado:
        index = selecionado[0]
        descricao, valor = dividas_por_mes[mes].pop(index)
        registrar_divida_paga(descricao, valor, mes)
        messagebox.showinfo("Dívida Paga", f"A dívida '{descricao}' de R$ {valor:.2f} foi paga.")
        salvar_dividas(arquivo_dividas, dividas_por_mes)
        atualizar_lista_dividas(mes)

def registrar_divida_paga(descricao, valor, mes):
    conn = sqlite3.connect('dividas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historico (descricao, valor, mes) VALUES (?, ?, ?)
    ''', (descricao, valor, mes))
    conn.commit()
    conn.close()

def exibir_historico():
    janela_historico = tk.Toplevel(root)
    janela_historico.title("Histórico de Dívidas Pagas")
    frame_historico = tk.Frame(janela_historico)
    frame_historico.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    listbox_historico = tk.Listbox(frame_historico, width=50, height=10)
    listbox_historico.pack(fill=tk.BOTH, expand=True, pady=5)
    btn_excluir = tk.Button(frame_historico, text="Excluir", command=lambda: excluir_divida_paga(listbox_historico))
    btn_excluir.pack(fill=tk.X, pady=5)
    carregar_historico(listbox_historico)

def carregar_historico(listbox_historico):
    listbox_historico.delete(0, tk.END)
    conn = sqlite3.connect('dividas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, descricao, valor, mes FROM historico')
    dividas_pagas = cursor.fetchall()
    conn.close()

    for id_, descricao, valor, mes in dividas_pagas:
        listbox_historico.insert(tk.END, f"{id_}: {descricao}: R$ {valor:.2f} - {mes}")

def excluir_divida_paga(listbox_historico):
    selecionado = listbox_historico.curselection()
    if selecionado:
        index = selecionado[0]
        item = listbox_historico.get(index)
        id_ = item.split(':')[0]
        conn = sqlite3.connect('dividas.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM historico WHERE id = ?', (id_,))
        conn.commit()
        conn.close()
        carregar_historico(listbox_historico)
        messagebox.showinfo("Dívida Excluída", f"A dívida com ID {id_} foi excluída do histórico.")

def configurar_banco():
    conn = sqlite3.connect('dividas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY,
            descricao TEXT,
            valor REAL,
            mes TEXT
        )
    ''')
    conn.commit()
    conn.close()

arquivo_dividas = 'dividas.json'
dividas_por_mes = carregar_dividas(arquivo_dividas)
meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

for mes in meses:
    if mes not in dividas_por_mes:
        dividas_por_mes[mes] = []
configurar_banco()

root = tk.Tk()
root.title("Gerenciamento de Dívidas")
root.state('zoomed')

frame_principal = tk.Frame(root)
frame_principal.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

combo_meses = tk.StringVar()
combo = tk.OptionMenu(frame_principal, combo_meses, *meses)
combo.pack(fill=tk.X, pady=5)

listbox = tk.Listbox(frame_principal, width=50, height=10)
listbox.pack(fill=tk.BOTH, expand=True, pady=5)

label_total_mes = tk.Label(frame_principal, text="")
label_total_mes.pack(fill=tk.X, pady=5)

label_total_geral = tk.Label(frame_principal, text="")
label_total_geral.pack(fill=tk.X, pady=5)

frame_botoes = tk.Frame(frame_principal)
frame_botoes.pack(fill=tk.X, pady=5)

btn_adicionar = tk.Button(frame_botoes, text="Adicionar Dívida", command=lambda: adicionar_divida(combo_meses.get()))
btn_adicionar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_zerar = tk.Button(frame_botoes, text="Zerar Dívidas", command=lambda: zerar_dividas(combo_meses.get()))
btn_zerar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_paga = tk.Button(frame_botoes, text="Marcar como Paga", command=lambda: marcar_como_paga(combo_meses.get()))
btn_paga.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_historico = tk.Button(frame_botoes, text="Histórico", command=exibir_historico)
btn_historico.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

combo_meses.set(meses[0])
combo_meses.trace("w", mudar_mes)
mudar_mes()
root.mainloop()
