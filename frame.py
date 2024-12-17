import tkinter as tk
from tkinter import messagebox, simpledialog

from constants import MONTHS


class Window:

    def __init__(self, db):
        self.db = db
        self.root = tk.Tk()
        self.frame_principal = tk.Frame(self.root)
        self.combo_meses = tk.StringVar()
        self.combo = tk.OptionMenu(self.frame_principal, self.combo_meses, *MONTHS)
        self.listbox = tk.Listbox(self.frame_principal, width=50, height=10)
        self.label_total_mes = tk.Label(self.frame_principal, text="")
        self.label_total_geral = tk.Label(self.frame_principal, text="")
        self.frame_botoes = tk.Frame(self.frame_principal)

        self.btn_adicionar = tk.Button(self.frame_botoes, text="Adicionar Dívida", command=lambda: self.adicionar_divida(self.combo_meses.get()))
        self.btn_zerar = tk.Button(self.frame_botoes, text="Zerar Dívidas", command=lambda: self.zerar_dividas(self.combo_meses.get()))
        self.btn_paga = tk.Button(self.frame_botoes, text="Marcar como Paga", command=lambda: self.marcar_como_paga(self.combo_meses.get()))
        self.btn_historico = tk.Button(self.frame_botoes, text="Histórico", command=self.exibir_historico)

        self.dividas_por_mes = {m: [] for m in MONTHS}

    def setup(self):
        # configurando janela
        self.root.title("Gerenciamento de Dívidas")
        self.root.attributes('-zoomed', True)
        self.frame_principal.pack(fill=tk.BOTH, expand=True, padx=80, pady=80)
        self.combo.pack(fill=tk.X, pady=5)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.label_total_mes.pack(fill=tk.X, pady=5)
        self.label_total_geral.pack(fill=tk.X, pady=5)
        self.frame_botoes.pack(fill=tk.X, pady=5)
        self.btn_adicionar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.btn_zerar.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.btn_paga.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.btn_historico.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.combo_meses.set(MONTHS[0])
        self.combo_meses.trace_add("write", self.mudar_mes)
        self.root.mainloop()

    def adicionar_divida(self, mes):
        descricao = simpledialog.askstring("Descrição da Dívida", "Insira a descrição da dívida:")
        if descricao:
            self.root.update()  
            valor = simpledialog.askfloat("Valor da Dívida", "Insira o valor da dívida:")
            if valor is not None:
                self.dividas_por_mes[mes].append((descricao, valor))
                self.atualizar_lista_dividas(mes)

    def carregar_historico(self, listbox_historico):
        dividas_pagas = self.db.get_historico()
        for id_, descricao, valor, mes in dividas_pagas:
            listbox_historico.insert(tk.END, f"{id_}: {descricao}: R$ {valor:.2f} - {mes}")

    def exibir_historico(self):
        janela_historico = tk.Toplevel(self.root)
        janela_historico.title("Histórico de Dívidas Pagas")
        frame_historico = tk.Frame(janela_historico)
        frame_historico.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        listbox_historico = tk.Listbox(frame_historico, width=50, height=10)
        listbox_historico.pack(fill=tk.BOTH, expand=True, pady=5)
        btn_excluir = tk.Button(frame_historico, text="Excluir", command=lambda: self.excluir_divida_paga(listbox_historico))
        btn_excluir.pack(fill=tk.X, pady=5)
        self.carregar_historico(listbox_historico)
    
    def zerar_dividas(self, mes):
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja zerar as dívidas de {mes}?"):
            self.dividas_por_mes[mes] = []
            self.atualizar_lista_dividas(mes)

    def marcar_como_paga(self, mes):
        selecionado = self.listbox.curselection()
        if selecionado:
            index = selecionado[0]
            descricao, valor = self.dividas_por_mes[mes].pop(index)
            self.db.registrar_divida_paga(descricao, valor, mes)
            messagebox.showinfo("Dívida Paga", f"A dívida '{descricao}' de R$ {valor:.2f} foi paga.")
            self.atualizar_lista_dividas(mes)

    def excluir_divida_paga(self, listbox_historico):
        selecionado = listbox_historico.curselection()
        if selecionado:
            index = selecionado[0]
            item = listbox_historico.get(index)
            id_ = item.split(':')[0]
            self.db.delete_history(id_)
            self.carregar_historico(listbox_historico)
            messagebox.showinfo("Dívida Excluída", f"A dívida com ID {id_} foi excluída do histórico.")

    def atualizar_lista_dividas(self, mes):
        self.listbox.delete(0, tk.END)
        for descricao, valor in self.dividas_por_mes[mes]:
            self.listbox.insert(tk.END, f"{descricao}: R$ {valor:.2f}")
        total_mes = sum(valor for _, valor in self.dividas_por_mes[mes])
        self.label_total_mes.config(text=f"Total {mes}: R$ {total_mes:.2f}")

        total_geral = sum(sum(valor for _, valor in dividas) for dividas in self.dividas_por_mes.values())
        self.label_total_geral.config(text=f"Total Geral: R$ {total_geral:.2f}")

    def mudar_mes(self, *args):
        mes = self.combo_meses.get()
        self.atualizar_lista_dividas(mes)
