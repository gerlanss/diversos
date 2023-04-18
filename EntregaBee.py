import os
import subprocess
import platform
import ctypes
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QFont, QImage, QClipboard, QIcon, QPixmap, QPainter, QTextDocument
from PyQt5.QtCore import Qt, QRect,QSizeF
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton, QTextEdit, QHBoxLayout, QWidget, QFileDialog, QVBoxLayout, QDesktopWidget
import sys

class EntregaBee(QMainWindow):
    def __init__(self):
        super().__init__()
        if os.name == 'nt':  # Verifica se o sistema operacional é Windows
            # Carrega o ícone para o aplicativo
            myappid = 'Entrega Bee 4.0'  # Um identificador arbitrário para o aplicativo
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.setWindowIcon(QIcon('favicon.ico'))
            self.centralizar()

# definir janela principal
        self.setWindowTitle("ENTREGA BEE")
        self.setGeometry(100, 100, 500, 400)
        # definir widgets
        self.loja_label = QLabel("LOJA:")
        self.loja_combo = QComboBox()
        self.loja_combo.addItems(["01", "02", "03", "04", "05"])
        self.cliente_label = QLabel("CLIENTE:")
        self.cliente_edit = QLineEdit()
        self.telefone_label = QLabel("TELEFONE:")
        self.telefone_edit = QLineEdit()
        self.telefone_edit.textChanged.connect(self.formatar_telefone)
        self.produto_label = QLabel("PRODUTO:")
        self.produto_edit = QLineEdit()
        self.valor_label = QLabel("VALOR:")
        self.valor_edit = QLineEdit()
        self.valor_edit = QLineEdit()
        self.valor_edit.installEventFilter(self)
        self.valor_edit.focusInEvent = self.valor_edit_focusInEvent
        self.valor_edit.editingFinished.connect(self.formatar_valor)
        self.valor_edit.setPlaceholderText("R$")
        self.endereco_label = QLabel("ENDEREÇO:")
        self.endereco_edit = QLineEdit()
        self.forma_pag_label = QLabel("PAGAMENTO:")
        self.forma_pag_edit = QLineEdit()
        self.obs_label = QLabel("OBSERVAÇÕES:")
        self.obs_edit = QTextEdit()
        # definir layout horizontal
        hbox = QHBoxLayout()

        # adicionar botões ao layout horizontal
        self.gravar_btn = QPushButton("GRAVAR/COPIAR")
        hbox.addWidget(self.gravar_btn)

        self.imprimir_btn = QPushButton("IMPRIMIR")
        hbox.addWidget(self.imprimir_btn)
        
        self.enviar_btn = QPushButton("ENVIAR")
        hbox.addWidget(self.enviar_btn)
        
        self.abrir_btn = QPushButton("ABRIR")
        hbox.addWidget(self.abrir_btn)

        self.limpar_btn = QPushButton("LIMPAR")
        hbox.addWidget(self.limpar_btn)
        
        self.carregar_btn = QPushButton("CARREGAR")
        hbox.addWidget(self.carregar_btn)
        # Adicione esta linha para criar a instância do clipboard
        self.clipboard = QApplication.clipboard()

        # definir layout vertical
        vbox = QVBoxLayout()

        # adicionar widgets ao layout vertical
        vbox.addWidget(self.loja_label)
        vbox.addWidget(self.loja_combo)
        vbox.addWidget(self.cliente_label)
        vbox.addWidget(self.cliente_edit)
        vbox.addWidget(self.telefone_label)
        vbox.addWidget(self.telefone_edit)
        vbox.addWidget(self.produto_label)
        vbox.addWidget(self.produto_edit)
        vbox.addWidget(self.endereco_label)
        vbox.addWidget(self.endereco_edit)
        vbox.addWidget(self.valor_label)
        vbox.addWidget(self.valor_edit)
        vbox.addWidget(self.forma_pag_label)
        vbox.addWidget(self.forma_pag_edit)
        vbox.addWidget(self.obs_label)
        vbox.addWidget(self.obs_edit)
        
        # definir widget principal
        widget = QWidget()
        widget.setLayout(vbox)
        widget.layout().addLayout(hbox)
        self.setCentralWidget(widget)
        
        # conectar sinais e slots
        self.gravar_btn.clicked.connect(self.gravar_copiar)
        self.imprimir_btn.clicked.connect(self.imprimir)
        self.enviar_btn.clicked.connect(self.abrir_whatsapp)
        self.abrir_btn.clicked.connect(self.abrir)      
        self.limpar_btn.clicked.connect(self.limpar)
        self.carregar_btn.clicked.connect(self.carregar_formulario)
    
    #Gravar e copiar dados do formulario    
    def gravar_copiar(self):
        # obter dados do formulário
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text().upper()
        telefone = self.telefone_edit.text().upper()
        produto = self.produto_edit.text().upper()
        endereco = self.endereco_edit.text().upper()
        valor = self.valor_edit.text().upper()
        forma_pag = self.forma_pag_edit.text().upper()
        obs = self.obs_edit.toPlainText().upper()

        # verificar se pasta de Entrega Bee existe
        if not os.path.exists(os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee")):
            os.makedirs(os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee"))

        # criar arquivo de texto
        filename = os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee", f"{cliente}_{telefone}.txt")
        with open(filename, "w") as f:
            f.write(f"ENTREGA BEE\n")
            f.write(f"LOJA: {loja}\n")  # Modifique esta linha
            f.write(f"CLIENTE: {cliente}\n")
            f.write(f"TELEFONE: {telefone}\n")
            f.write(f"PRODUTO: {produto}\n")
            f.write(f"ENDEREÇO: {endereco}\n")
            f.write(f"VALOR: {valor}\n")
            f.write(f"PAGAMENTO: {forma_pag}\n")
            f.write(f"OBSERVAÇÕES: {obs}\n")

        # copiar para a área de transferência
        mensagem_formatada = f"*ENTREGA BEE*\n\n*LOJA:* {loja}\n*CLIENTE:* {cliente}\n*TELEFONE:* {telefone}\n*PRODUTO:* {produto}\n*ENDEREÇO:* {endereco}\n*VALOR:* {valor}\n*PAGAMENTO:* {forma_pag}\n*OBSERVAÇÕES:* {obs}\n\n\n"
        self.clipboard.setText(mensagem_formatada)
        # exibir caixa de mensagem
        QMessageBox.information(self, "Gravado e Copiado", "Formulario Gravado e copiado com sucesso ^_^")

    #Usar codificadores para ler documentos com varios caracteres
    def read_file_with_multiple_encodings(self, file_path, encodings=("utf-8", "cp1252", "latin-1")):
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                return text
            except UnicodeDecodeError:
                pass
        raise UnicodeDecodeError("Nenhuma das codificações fornecidas funcionou.")

    #Selecionar impressora para imprimir
    def imprimir(self):
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text().upper()
        telefone = self.telefone_edit.text().upper()
        produto = self.produto_edit.text().upper()
        endereco = self.endereco_edit.text().upper()
        valor = self.valor_edit.text().upper()
        forma_pag = self.forma_pag_edit.text().upper()
        obs = self.obs_edit.toPlainText().upper()

        # Carregar logo como QImage
        logo = QImage("logo.png")

        # Ajustar a largura para 80 mm (aproximadamente 630 pixels) e altura para 1600
        image_width = 270
        image_height = 100000

        # Criar uma QImage com um fundo branco
        image = QImage(image_width, image_height, QImage.Format_RGB32)
        image.fill(Qt.white)

        # Criar um QPainter para desenhar na QImage
        painter = QPainter(image)
        painter.setPen(Qt.black)

        # Desenhar a logo na QImage
        logo_x = 10  # Ajustar a posição X da logo
        logo_y = 10  # Ajustar a posição Y da logo
        logo_width = 100  # Ajustar a largura da logo
        logo_height = 100  # Ajustar a altura da logo
        painter.drawImage(QRect(logo_x, logo_y, logo_width, logo_height), logo)

        # Definir o tamanho da fonte
        font = QFont()
        font.setPointSize(12)  # Aumentar o tamanho da fonte
        painter.setFont(font)

        # Desenhar o texto na QImage
        y = 120  # Ajustar a posição inicial do texto (abaixo da logo)
        line_height = 25  # Ajustar a altura da linha
        def draw_text_wrapped(text, max_width):
            nonlocal y
            words = text.split()
            line = ""
            for word in words:
                if painter.fontMetrics().horizontalAdvance(line + " " + word) < max_width:
                    line += " " + word
                else:
                    painter.drawText(QRect(20, y, max_width, line_height), Qt.AlignLeft, line)  # Ajustar a posição do texto
                    y += line_height
                    line = word
            painter.drawText(QRect(20, y, max_width, line_height), Qt.AlignLeft, line)  # Ajustar a posição do texto
            y += line_height

        draw_text_wrapped(f"CLIENTE: {cliente}", image_width - 20)
        draw_text_wrapped(f"TELEFONE: {telefone}", image_width - 20)
        draw_text_wrapped(f"PRODUTO: {produto}", image_width - 20)
        draw_text_wrapped(f"ENDEREÇO: {endereco}", image_width - 20)
        draw_text_wrapped(f"VALOR: {valor}", image_width - 20)
        draw_text_wrapped(f"PAGAMENTO: {forma_pag}", image_width - 20)
        draw_text_wrapped(f"OBSERVAÇÕES: {obs}", image_width - 20)

        # Finalizar a pintura
        painter.end()

        # Imprimir a QImage
        printer = QPrinter()
        printer.setPageSize(QPrinter.Custom)
        printer.setPaperSize(QSizeF(image.width() / 20, image.height() / 20), QPrinter.Inch)
        printer.setFullPage(True)
        printer.setResolution(600)  # Defina a resolução desejada aqui (ex: 300 DPI)

        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            painter.begin(printer)
            painter.drawImage(QRect(0, 0, image.width(), image.height()), image)
            painter.end()
                    
    #Abrir app do Whatsapp        
    def abrir_whatsapp(self):
        if platform.system() == "Windows":
            try:
                subprocess.Popen("explorer shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
            except FileNotFoundError:
                pass
            
    def abrir(self):
        # abrir arquivo para edição
        folder_path = os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee")
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo", folder_path, "Arquivos de texto (*.txt)")
        if filename:
            with open(filename, "r") as f:
                lines = f.readlines()
            if lines:
                loja = lines[1].split(":")[1].strip()
                cliente = lines[2].split(":")[1].strip()
                telefone = lines[3].split(":")[1].strip()
                produto = lines[4].split(":")[1].strip()
                endereco = lines[5].split(":")[1].strip()
                valor = lines[6].split(":")[1].strip()
                forma_pag = lines[7].split(":")[1].strip()
                obs = lines[8].split(":")[1].strip()

                # preencher formulário
                self.loja_combo.setCurrentText(loja)
                self.cliente_edit.setText(cliente)
                self.telefone_edit.setText(telefone)
                self.produto_edit.setText(produto)
                self.endereco_edit.setText(endereco)
                self.valor_edit.setText(valor)
                self.forma_pag_edit.setText(forma_pag)
                self.obs_edit.setPlainText(obs)
                
        #carregar formulario da area de transferencia            
    def carregar_formulario(self):
        # obter texto copiado
        clipboard_text = QApplication.clipboard().text()

        # verificar se o texto copiado contém os campos do formulário
        if not ("LOJA:" in clipboard_text and "CLIENTE:" in clipboard_text and "TELEFONE:" in clipboard_text and "PRODUTO:" in clipboard_text and "ENDEREÇO:" in clipboard_text and "VALOR:" in clipboard_text and "PAGAMENTO:" in clipboard_text and "OBSERVAÇÕES:" in clipboard_text):
            QMessageBox.warning(self, "Erro ao carregar formulário", "<center>Ei, isso não me pertence!<br>Copie o formulario do Whatsapp e tente novamente ;-)</center>")
            return

        # separar os campos do texto copiado
        loja = clipboard_text.split("LOJA:")[1].split("CLIENTE:")[0].strip()
        cliente = clipboard_text.split("CLIENTE:")[1].split("TELEFONE:")[0].strip()
        telefone = clipboard_text.split("TELEFONE:")[1].split("PRODUTO:")[0].strip()
        produto = clipboard_text.split("PRODUTO:")[1].split("ENDEREÇO:")[0].strip()
        endereco = clipboard_text.split("ENDEREÇO:")[1].split("VALOR:")[0].strip()
        valor = clipboard_text.split("VALOR:")[1].split("PAGAMENTO:")[0].strip()
        forma_pag = clipboard_text.split("PAGAMENTO:")[1].split("OBSERVAÇÕES:")[0].strip()
        obs_start = clipboard_text.find("OBSERVAÇÕES:") + len("OBSERVAÇÕES:")
        obs = clipboard_text[obs_start:]
        obs_end = obs.find("@")
        if obs_end != -1:
            obs = obs[:obs_end]
            self.obs_edit.setPlainText(obs)
        else:
            self.obs_edit.setPlainText("")


        # preencher widgets do formulário com os valores correspondentes
        self.loja_combo.setCurrentIndex(-1)
        self.cliente_edit.clear()
        self.telefone_edit.clear()
        self.produto_edit.clear()
        self.endereco_edit.clear()
        self.valor_edit.clear()
        self.forma_pag_edit.clear()
        self.obs_edit.clear()
        self.loja_combo.setCurrentText(loja)
        self.cliente_edit.setText(cliente)
        self.telefone_edit.setText(telefone)
        self.produto_edit.setText(produto)
        self.endereco_edit.setText(endereco)
        self.valor_edit.setText(valor)
        self.forma_pag_edit.setText(forma_pag)
        self.obs_edit.setPlainText(obs)


    # limpar formulário
    def limpar(self):
        self.loja_combo.setCurrentIndex(0)
        self.cliente_edit.clear()
        self.telefone_edit.clear()
        self.produto_edit.clear()
        self.endereco_edit.clear()
        self.valor_edit.clear()
        self.forma_pag_edit.clear()
        self.obs_edit.clear()
        
        #formatar telefone 
    def formatar_telefone(self):
        telefone = self.telefone_edit.text()
        if len(telefone) == 11 and not telefone.startswith("("):
            telefone_formatado = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
            self.telefone_edit.setText(telefone_formatado)

        #Formatar valor
    def formatar_valor(self):
        valor = self.valor_edit.text().replace(',', '.').replace('R$', '').strip()
        if not valor:
            return
        try:
            valor_float = float(valor)
            valor_formatado = f"R$ {valor_float:,.2f}".replace(",", "x").replace(".", ",").replace("x", ".")
            self.valor_edit.setText(valor_formatado)
        except ValueError:
            pass
        #verificar se campo valor está vazio
    def valor_edit_focusInEvent(self, event):
        valor = self.valor_edit.text()
        if valor == 'R$ 0,00':
            self.valor_edit.clear()
            self.valor_edit.setPlaceholderText("R$")
        elif not valor.startswith("R$"):
            self.valor_edit.setText(f"R$ {valor}")
        super(QLineEdit, self.valor_edit).focusInEvent(event)
        
        #Centralizar Janela
    def centralizar(self):
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())
    

# definir janela principal
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EntregaBee()
    window.show()
    sys.exit(app.exec_())
