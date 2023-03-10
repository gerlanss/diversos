import wx
import os

class EntregaBee(wx.Frame):
    def __init__(self, *args, **kw):
        super(EntregaBee, self).__init__(*args, **kw)
        self.InitUI()
        

    def InitUI(self):
        # Cria o painel
        painel = wx.Panel(self)

        # Cria os campos de texto e os botões
        lojas = ["01", "02", "03", "04", "05"]
        loja_lbl = wx.StaticText(painel, label="LOJA:")
        self.loja_cmb = wx.ComboBox(painel, choices=lojas)
        cliente_lbl = wx.StaticText(painel, label="CLIENTE:")
        self.cliente_txt = wx.TextCtrl(painel)
        telefone_lbl = wx.StaticText(painel, label="TELEFONE:")
        self.telefone_txt = wx.TextCtrl(painel)
        produto_lbl = wx.StaticText(painel, label="PRODUTO:")
        self.produto_txt = wx.TextCtrl(painel)
        endereco_lbl = wx.StaticText(painel, label="ENDERECO:")
        self.endereco_txt = wx.TextCtrl(painel)
        complemento_lbl = wx.StaticText(painel, label="COMPLEMENTO:")
        self.complemento_txt = wx.TextCtrl(painel)
        valor_lbl = wx.StaticText(painel, label="VALOR:")
        self.valor_txt = wx.TextCtrl(painel)
        pagamento_lbl = wx.StaticText(painel, label="PAGAMENTO:")
        self.pagamento_cmb = wx.ComboBox(painel, choices=["DINHEIRO", "CARTAO"])
        self.obs_lbl = wx.StaticText(painel, label="OBS:")
        self.obs_txt = wx.TextCtrl(painel, style=wx.TE_MULTILINE)

        btn_gravar_copiar = wx.Button(painel, label="GRAVAR/COPIAR")
        btn_imprimir = wx.Button(painel, label="IMPRIMIR")
        btn_carregar = wx.Button(painel, label="CARREGAR")

        # Adiciona os campos e botões ao layout
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(loja_lbl, 0, wx.ALL, 5)
        layout.Add(self.loja_cmb, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(cliente_lbl, 0, wx.ALL, 5)
        layout.Add(self.cliente_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(telefone_lbl, 0, wx.ALL, 5)
        layout.Add(self.telefone_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(produto_lbl, 0, wx.ALL, 5)
        layout.Add(self.produto_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(endereco_lbl, 0, wx.ALL, 5)
        layout.Add(self.endereco_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(complemento_lbl, 0, wx.ALL, 5)
        layout.Add(self.complemento_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(valor_lbl, 0, wx.ALL, 5)
        layout.Add(self.valor_txt, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(pagamento_lbl, 0, wx.ALL, 5)
        layout.Add(self.pagamento_cmb, 0, wx.EXPAND|wx.ALL, 5)
        layout.Add(self.obs_lbl, 0, wx.ALL, 5)
        layout.Add(self.obs_txt, 0, wx.EXPAND|wx.ALL, 5)

        # Adiciona os botões ao layout
        horizontal_box = wx.BoxSizer(wx.HORIZONTAL)
        horizontal_box.Add(btn_gravar_copiar, 0, wx.ALL, 5)
        horizontal_box.Add(btn_imprimir, 0, wx.ALL, 5)
        horizontal_box.Add(btn_carregar, 0, wx.ALL, 5)
        layout.Add(horizontal_box, 0, wx.ALIGN_CENTER)

        painel.SetSizer(layout)

        # Define o comportamento dos botões
        btn_gravar_copiar.Bind(wx.EVT_BUTTON, self.OnGravarCopiar)
        btn_imprimir.Bind(wx.EVT_BUTTON, self.OnImprimir)
        btn_carregar.Bind(wx.EVT_BUTTON, self.OnCarregar)
        
    def formatar_nome_arquivo(self, cliente, telefone):
            return f"{cliente}_{telefone}.txt"

    def OnGravarCopiar(self, e):
            # Define o nome do arquivo formatado
            nome_arquivo = self.formatar_nome_arquivo(self.cliente_txt.GetValue(), self.telefone_txt.GetValue())


            # Cria o diretório se ele não existir
            if not os.path.exists("Entregas Bee"):
                os.makedirs("Entregas Bee")

            # Define o caminho completo do arquivo
            caminho_arquivo = os.path.join("Entregas Bee", nome_arquivo)

            # Cria o arquivo ou sobrescreve se já existir
            with open(caminho_arquivo, "w") as arquivo:
                # Escreve os dados no arquivo em maiúsculas
                arquivo.write(f"LOJA: {self.loja_cmb.GetValue().upper()}\n")
                arquivo.write(f"CLIENTE: {self.cliente_txt.GetValue().upper()}\n")
                arquivo.write(f"TELEFONE: {self.telefone_txt.GetValue().upper()}\n")
                arquivo.write(f"PRODUTO: {self.produto_txt.GetValue().upper()}\n")
                arquivo.write(f"ENDERECO: {self.endereco_txt.GetValue().upper()}\n")
                arquivo.write(f"COMPLEMENTO: {self.complemento_txt.GetValue().upper()}\n")
                arquivo.write(f"VALOR: {self.valor_txt.GetValue().upper()}\n")
                arquivo.write(f"PAGAMENTO: {self.pagamento_cmb.GetValue().upper()}\n")
                arquivo.write(f"OBS: {self.obs_txt.GetValue().upper()}")

            # Copia o arquivo para a área de transferência
            with open(caminho_arquivo, "r") as arquivo:
                conteudo = arquivo.read()
                wx.TheClipboard.Open()
                wx.TheClipboard.SetData(wx.TextDataObject(conteudo))
                wx.TheClipboard.Close()

            # Exibe mensagem de sucesso
            wx.MessageBox("Arquivo gravado com sucesso!", "Sucesso", wx.OK | wx.ICON_INFORMATION)


    def OnImprimir(self, e):
        # Seleciona a impressora
        dlg = wx.PrintDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            printer = dlg.GetPrintDialogData().GetPrinter()
            print_data = wx.PrintData(printer)
            # Imprime o conteúdo do painel
            self.GetParent().GetParent().GetHandle().PrintWindow(printer.GetHDC(), flags=wx.PW_CLIENT_ONLY)
            printer.Print(print_data, self.GetParent().GetParent().GetTitle())
            printer.GetHDC().DeleteDC()
            dlg.Destroy()

    def OnCarregar(self, e):
        # Exibe a caixa de diálogo para selecionar o arquivo
        dlg = wx.FileDialog(self, "Escolha um arquivo", os.path.join(os.getcwd(), "Entrega Bee"), "", "*.txt", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            # Define o diretório de trabalho como "Entrega Bee"
            os.chdir(os.path.join(os.getcwd(), "Entrega Bee"))
            # Lê o conteúdo do arquivo e preenche os campos
            with open(dlg.GetPath(), "r") as arquivo:
                linhas = arquivo.readlines()
                self.loja_cmb.SetValue(linhas[0].split(":")[1].strip())
                self.cliente_txt.SetValue(linhas[1].split(":")[1].strip())
                self.telefone_txt.SetValue(linhas[2].split(":")[1].strip())
                self.produto_txt.SetValue(linhas[3].split(":")[1].strip())
                self.endereco_txt.SetValue(linhas[4].split(":")[1].strip())
                self.complemento_txt.SetValue(linhas[5].split(":")[1].strip())
                self.valor_txt.SetValue(linhas[6].split(":")[1].strip())
                self.pagamento_cmb.SetValue(linhas[7].split(":")[1].strip())
                self.obs_txt.SetValue(linhas[8].split(":")[1].strip())


    def OnClose(self, e):
        self.Destroy()

if __name__ == '__main__':
    app = wx.App()
    janela = EntregaBee(None, title="ENTREGA BEE", size=(850, 650))
    janela.Show()
    app.MainLoop()
