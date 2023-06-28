import os
import subprocess
import platform
import ctypes
import qrcode
from PIL import Image, ImageDraw, ImageOps
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QFont, QImage, QPixmap, QIcon, QPainter, QTextDocument, QFontMetrics, QAbstractTextDocumentLayout, QTextOption, QPageSize
from PyQt5.QtCore import Qt, QRect, QSizeF, QEvent, QRectF
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, QMainWindow, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton, QTextEdit, QHBoxLayout, QWidget, QFileDialog, QVBoxLayout, QDesktopWidget
import sys


class CustomPlainTextEdit(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.parent().focusNextChild()
            return True
        return super().eventFilter(obj, event)

    
class Entregas(QMainWindow):
    def __init__(self):
        super().__init__()
        if os.name == 'nt':  # Verifica se o sistema operacional é Windows
            # Carrega o ícone para o aplicativo
            myappid = 'Entregas 7.1'  # Um identificador arbitrário para o aplicativo
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.setWindowIcon(QIcon('favicon.ico'))
            self.centralizar()

# definir janela principal
        self.setWindowTitle("ENTREGAS")
        self.setGeometry(100, 100, 500, 400)
        
        self.loja_info = {
            "01": {"TELEFONE": "Telefone: (95) 3623-7063", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "02": {"TELEFONE": "Telefone: (95) 3627-1053", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "03": {"TELEFONE": "Telefone: (95) 3623-0207", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "04": {"TELEFONE": "Telefone: (95) 3623-7303", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "05": {"TELEFONE": "Telefone: (95) 3224-6545", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
        }
        self.telefone_loja = ""
        self.whatsapp_loja = ""
        self.loja_selecionada("01")
        # definir widgets
        self.tipo_entrega_label = QLabel("TIPO DE ENTREGA:")
        self.tipo_entrega_combo = QComboBox()
        self.tipo_entrega_combo.addItems(["ENTREGA BEE", "ENTREGA ROTA", "RETIRADA EM LOJA"])
        self.tipo_entrega_combo.currentTextChanged.connect(self.tipo_entrega_selecionada)
        self.loja_label = QLabel("LOJA:")
        self.loja_combo = QComboBox()
        self.loja_combo.addItems(["01", "02", "03", "04", "05"])
        self.loja_combo.currentTextChanged.connect(self.loja_selecionada)
        self.cliente_label = QLabel("CLIENTE:")
        self.cliente_edit = QLineEdit()
        self.telefone_label = QLabel("TELEFONE:")
        self.telefone_edit = QLineEdit()
        self.telefone_edit.textChanged.connect(self.formatar_telefone)
        self.produto_label = QLabel("PRODUTO:")
        self.produto_edit = CustomPlainTextEdit()
        self.produto_edit.setFixedHeight(self.calcular_altura_campo_texto(self.produto_edit, 5))
        self.valor_label = QLabel("VALOR:")
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
        
        self.qrcode_btn = QPushButton("QRCODE")
        hbox.addWidget(self.qrcode_btn)
        
        self.imprimir_btn = QPushButton("IMPRIMIR")
        hbox.addWidget(self.imprimir_btn)
        
        self.agendar_btn = QPushButton("AGENDAR")
        hbox.addWidget(self.agendar_btn)
        
        self.editar_btn = QPushButton("EDITAR")
        hbox.addWidget(self.editar_btn)
        
        self.limpar_btn = QPushButton("LIMPAR")
        hbox.addWidget(self.limpar_btn)
        
        self.carregar_btn = QPushButton("CARREGAR")
        hbox.addWidget(self.carregar_btn)
        # Adicione esta linha para criar a instância do clipboard
        self.clipboard = QApplication.clipboard()

        # definir layout vertical
        vbox = QVBoxLayout()

        # adicionar widgets ao layout vertical
        vbox.addWidget(self.tipo_entrega_label)
        vbox.addWidget(self.tipo_entrega_combo)
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
        self.tipo_entrega_selecionada(self.tipo_entrega_combo.currentText())
        self.gravar_btn.clicked.connect(self.gravar_copiar)
        self.qrcode_btn.clicked.connect(self.gerar_qrcode)
        self.imprimir_btn.clicked.connect(self.imprimir)
        self.agendar_btn.clicked.connect(self.abrir_link_no_firefox)
        self.editar_btn.clicked.connect(self.editar)  
        self.limpar_btn.clicked.connect(self.limpar)
        self.carregar_btn.clicked.connect(self.carregar_formulario)
        
    def tipo_entrega_selecionada(self, tipo_entrega):
        if tipo_entrega == "ENTREGA ROTA":
            self.agendar_btn.show()
        else:
            self.agendar_btn.hide()

        if tipo_entrega == "RETIRADA EM LOJA":
            self.endereco_label.hide()
            self.endereco_edit.hide()
            self.telefone_label.hide()
            self.telefone_edit.hide()
        else:
            self.endereco_label.show()
            self.endereco_edit.show()
            self.telefone_label.show()
            self.telefone_edit.show()

    def calcular_altura_campo_texto(self, campo, num_linhas):
        metricas_fonte = QFontMetrics(campo.font())
        altura = (metricas_fonte.lineSpacing() * num_linhas) + (campo.contentsMargins().top() + campo.contentsMargins().bottom())
        return altura        
        
    def loja_selecionada(self, loja=None):
        if loja is None:
            loja = self.loja_combo.currentText()

        if loja in self.loja_info:
            self.telefone_loja = self.loja_info[loja]["TELEFONE"]
            self.whatsapp_loja = self.loja_info[loja]["WHATSAPP"]
        else:
            self.telefone_loja = None
            self.whatsapp_loja = None
                    
    def gravar_copiar(self):
        # obter dados do formulário
        tipo_entrega = self.tipo_entrega_combo.currentText()
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text().upper()
        telefone = self.telefone_edit.text().upper()
        produto = self.produto_edit.toPlainText().upper()
        endereco = self.endereco_edit.text().upper()
        valor = self.valor_edit.text().upper()
        forma_pag = self.forma_pag_edit.text().upper()
        obs = self.obs_edit.toPlainText().upper()

        if not forma_pag:
            forma_pag = "PAGO"

        if not valor:
            valor = "PAGO"

        # verificar se pasta de Entregas existe
        if not os.path.exists(os.path.join(os.path.expanduser('~'), "Documents", "Entregas")):
            os.makedirs(os.path.join(os.path.expanduser('~'), "Documents", "Entregas"))

        # criar arquivo de texto
        filename = os.path.join(os.path.expanduser('~'), "Documents", "Entregas", f"{cliente}_{telefone}.txt")
        with open(filename, "w") as f:
            f.write(f"ENTREGAS\n")
            f.write(f"TIPO DE ENTREGA: {tipo_entrega}\n")
            f.write(f"LOJA: {loja}\n")
            f.write(f"CLIENTE: {cliente}\n")
            f.write(f"TELEFONE: {telefone}\n")
            f.write(f"PRODUTO: {produto}\n")
            f.write(f"ENDEREÇO: {endereco}\n")
            f.write(f"VALOR: {valor}\n")
            f.write(f"PAGAMENTO: {forma_pag}\n")
            f.write(f"OBSERVAÇÕES: {obs}\n")

        # copiar para a área de transferência
        campos = [
            (tipo_entrega,"\n"),
            ("LOJA:", loja),
            ("CLIENTE:", cliente),
            ("TELEFONE:", telefone),
            ("PRODUTO:", produto),
            ("ENDEREÇO:", endereco),
            ("VALOR:", valor),
            ("PAGAMENTO:", forma_pag),
            ("OBSERVAÇÕES:", obs)
        ]

        mensagem_formatada = ''

        for campo, valor in campos:
            if valor:
                mensagem_formatada += f"*{campo}* {valor}\n"

        mensagem_formatada += "\n"

        self.clipboard.setText(mensagem_formatada)

        # exibir caixa de mensagem
        QMessageBox.information(self, "Gravado e Copiado", "Formulario Gravado e copiado com sucesso ^_^")

    def gerar_qrcode(self):
        # Obter os valores dos campos
        tipo_entrega = self.tipo_entrega_combo.currentText()
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text()
        telefone = self.telefone_edit.text()
        produto = self.produto_edit.toPlainText()
        endereco = self.endereco_edit.text()
        valor = self.valor_edit.text()
        forma_pag = self.forma_pag_edit.text() if self.forma_pag_edit.text() else "PAGO"
        obs = self.obs_edit.toPlainText()

        # Criar uma string com os títulos e os valores dos campos
        dados = ""
        if tipo_entrega:
            dados += f"*{tipo_entrega}*\n\n"
        if loja:
            dados += f"*LOJA:* {loja}\n"
        if cliente:
            dados += f"*CLIENTE:* {cliente}\n"
        if telefone:
            dados += f"*TELEFONE:* {telefone}\n"
        if produto:
            dados += f"*PRODUTO:* {produto}\n"
        if endereco:
            dados += f"*ENDEREÇO:* {endereco}\n"
        dados += f"*VALOR:* {valor}\n"
        dados += f"*PAGAMENTO:* {forma_pag}\n"
        if obs:
            dados += f"*OBSERVAÇÕES:* {obs}\n\n"

        # Gerar o QRCode com os dados
        qr = qrcode.QRCode(
            version=4,  # Aumentar a versão do QRCode
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=1
        )
        qr.add_data(dados)
        qr.make(fit=True)
        qrcode_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Redimensionar o QR Code para 250x250
        qrcode_img = qrcode_img.resize((250, 250), Image.NEAREST)

        # Salvar a imagem como PNG
        png_file_path = "qrcode.png"
        qrcode_img.save(png_file_path)

        # Exibir o QRCode
        qrcode_img.show()

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

    def imprimir(self):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageMargins(2, 2, 2, 2, QPrinter.Millimeter)
        printer.setOutputFormat(QPrinter.NativeFormat)

        dialog = QPrintDialog(printer, self)

        if dialog.exec_() == QDialog.Accepted:
            dpi = printer.resolution()
            font_size = round(16 * dpi / 96)  # Ajusta o tamanho da fonte com base na resolução da impressora
            line_spacing = font_size * 0.5

            painter = QPainter()
            painter.begin(printer)
            font = QFont("Arial", font_size)
            painter.setFont(font)

            # Ajusta a largura do documento para 80mm
            mm_width = 80
            doc_width = int(mm_width / 25.4 * dpi)

            total_height = 0

            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            logo = QImage(logo_path)
            scaled_logo = logo.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_rect = QRect(0, 0, scaled_logo.width(), scaled_logo.height())
            painter.drawImage(logo_rect, scaled_logo)
            total_height += scaled_logo.height()

            loja_id = self.loja_combo.currentText().split(" - ")[0]
            loja_info = self.loja_info.get(loja_id, {"TELEFONE": "", "WHATSAPP": ""})
            phone_text = loja_info["TELEFONE"]
            whatsapp_text = loja_info["WHATSAPP"]

            phone_font = QFont("Arial", font_size)  # Ajusta o tamanho da fonte com base na resolução da impressora
            painter.setFont(phone_font)
            painter.translate(scaled_logo.width(), 0)

            phone_doc = QTextDocument()
            phone_doc.setDefaultFont(phone_font)
            phone_doc.setPlainText(phone_text)
            phone_doc.setTextWidth(doc_width / 2)

            phone_ctx = QAbstractTextDocumentLayout.PaintContext()
            phone_layout = phone_doc.documentLayout()
            phone_layout.draw(painter, phone_ctx)

            painter.translate(0, phone_doc.size().height() + line_spacing) # Adicione a altura do telefone à altura total

            whatsapp_font = QFont("Arial", font_size)  # Ajusta o tamanho da fonte com base na resolução da impressora
            painter.translate(0, phone_doc.size().height + line_spacing)
            whatsapp_doc = QTextDocument()
            whatsapp_doc.setDefaultFont(whatsapp_font)
            whatsapp_doc.setPlainText(whatsapp_text)
            whatsapp_doc.setTextWidth(doc_width / 2)

            whatsapp_ctx = QAbstractTextDocumentLayout.PaintContext()
            whatsapp_layout = whatsapp_doc.documentLayout()
            whatsapp_layout.draw(painter, whatsapp_ctx)

            total_height += whatsapp_doc.size().height() + line_spacing  # Adicione a altura do whatsapp à altura total

            painter.setFont(font)
            painter.translate(-scaled_logo.width(), total_height)

            campos = [
                ("LOJA: ", self.loja_combo.currentText().upper().splitlines()),
                ("CLIENTE: ", self.cliente_edit.text().upper().splitlines()),
                ("TELEFONE: ", self.telefone_edit.text().upper().splitlines()),
                ("PRODUTO: ", self.produto_edit.toPlainText().upper().splitlines()),
                ("ENDEREÇO: ", self.endereco_edit.text().upper().splitlines()),
                ("VALOR: ", self.valor_edit.text().upper().splitlines()),
                ("FORMA DE PAGAMENTO: ", self.forma_pag_edit.text().upper().splitlines()),
                ("OBSERVAÇÕES: ", self.obs_edit.toPlainText().upper().splitlines()),
            ]

            for titulo, texto in campos:
                if not texto:
                    continue

                if isinstance(texto, list):  # Verifique se é uma lista, o que significa que temos várias linhas
                    first_line = True
                    for line in texto:
                        if first_line:
                            full_text = f'<b>{titulo}</b>{line}'
                            first_line = False
                        else:
                            full_text = line

                        doc = QTextDocument()
                        doc.setDefaultFont(font)
                        doc.setHtml(full_text)
                        doc.setTextWidth(doc_width)
                        option = QTextOption()
                        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
                        doc.setDefaultTextOption(option)

                        ctx = QAbstractTextDocumentLayout.PaintContext()
                        layout = doc.documentLayout()
                        layout.draw(painter, ctx)
                        painter.translate(0, doc.size().height() + line_spacing)
                else:
                    full_text = f'<b>{titulo}</b>{texto}'
                    doc = QTextDocument()
                    doc.setDefaultFont(font)
                    doc.setHtml(full_text)
                    doc.setTextWidth(doc_width)
                    option = QTextOption()
                    option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
                    doc.setDefaultTextOption(option)

                    ctx = QAbstractTextDocumentLayout.PaintContext()
                    layout = doc.documentLayout()
                    layout.draw(painter, ctx)
                    painter.translate(0, doc.size().height() + line_spacing)

            if painter.isActive():  # Verifique se o pintor está ativo antes de finalizá-lo
                painter.end()

                   
    # Adicionar função para abrir o link no Firefox
    def abrir_link_no_firefox(self):
        firefox_path = None

        if platform.system() == "Windows":
            firefox_path = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
            if not os.path.exists(firefox_path):
                firefox_path = "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
        elif platform.system() == "Linux":
            firefox_path = "/usr/bin/firefox"
        elif platform.system() == "Darwin":
            firefox_path = "/Applications/Firefox.app/Contents/MacOS/firefox"

        if firefox_path and os.path.exists(firefox_path):
            link = "http://192.168.3.23:8080/Easytech/sg0026.do?method=gotoComando&comando=atd0102.do?method=prepTela"
            subprocess.Popen([firefox_path, link])
        else:
            QMessageBox.warning(self, "Erro", "O Firefox não foi encontrado no sistema. Por favor, instale o Firefox e tente novamente.")               
            
    def editar(self):
        folder_path = os.path.join(os.path.expanduser('~'), "Documents", "Entregas")
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo", folder_path, "Arquivos de texto (*.txt)")
        if filename:
            with open(filename, "r") as f:
                lines = f.readlines()

            campos = {
                "TIPO DE ENTREGA": "",
                "LOJA": "",
                "CLIENTE": "",
                "TELEFONE": "",
                "PRODUTO": "",
                "ENDEREÇO": "",
                "VALOR": "",
                "PAGAMENTO": "",
                "OBSERVAÇÕES": ""
            }

            for line in lines:
                for campo in campos:
                    if line.startswith(campo):
                        campos[campo] = line.split(":")[1].strip()
                        break

            self.tipo_entrega_combo.setCurrentText(campos["TIPO DE ENTREGA"])
            self.loja_combo.setCurrentText(campos["LOJA"])
            self.cliente_edit.setText(campos["CLIENTE"])
            self.telefone_edit.setText(campos["TELEFONE"])
            self.produto_edit.setPlainText(campos["PRODUTO"])
            self.endereco_edit.setText(campos["ENDEREÇO"])
            
            if campos["VALOR"] != "PAGO":
                self.valor_edit.setText(campos["VALOR"])
            
            if campos["PAGAMENTO"] != "PAGO":
                self.forma_pag_edit.setText(campos["PAGAMENTO"])
            
            self.obs_edit.setPlainText(campos["OBSERVAÇÕES"])
        else:
            QMessageBox.warning(self, "Arquivo incompatível", "Esse arquivo não foi feito por mim, parça!") 
                     
    def get_field_value(self, field_name, text):
        start_index = text.find(field_name)
        if start_index == -1:
            return ""

        start_index += len(field_name)
        end_index = text.find("\n", start_index)
        if end_index == -1:
            return text[start_index:].strip()

        return text[start_index:end_index].strip()

    def carregar_formulario(self):
        # obter texto copiado
        clipboard_text = QApplication.clipboard().text()

        # obter valores dos campos usando a função get_field_value
        tipo_entrega = ""
        if "ENTREGA BEE" in clipboard_text:
            tipo_entrega = "ENTREGA BEE"
        elif "ENTREGA ROTA" in clipboard_text:
            tipo_entrega = "ENTREGA ROTA"
        elif "RETIRADA EM LOJA" in clipboard_text:
            tipo_entrega = "RETIRADA EM LOJA"

        loja = self.get_field_value("LOJA:", clipboard_text)
        cliente = self.get_field_value("CLIENTE:", clipboard_text)
        telefone = self.get_field_value("TELEFONE:", clipboard_text)
        produto = self.get_field_value("PRODUTO:", clipboard_text)
        endereco = self.get_field_value("ENDEREÇO:", clipboard_text)
        valor = self.get_field_value("VALOR:", clipboard_text)
        forma_pag = self.get_field_value("PAGAMENTO:", clipboard_text)
        obs = self.get_field_value("OBSERVAÇÕES:", clipboard_text)

        # preencher widgets do formulário com os valores correspondentes
        self.tipo_entrega_combo.setCurrentIndex(self.tipo_entrega_combo.findText(tipo_entrega))
        self.loja_combo.setCurrentText(loja)
        self.cliente_edit.setText(cliente)
        self.telefone_edit.setText(telefone)
        self.produto_edit.setPlainText(produto)
        self.endereco_edit.setText(endereco)
        
        if valor != "PAGO":
            self.valor_edit.setText(valor)
        
        if forma_pag != "PAGO":
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
    window = Entregas()
    window.show()
    sys.exit(app.exec_())
