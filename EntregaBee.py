import os
import subprocess
import platform
import ctypes
import qrcode
import re
from PyQt5.QtCore import QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from PIL import Image, ImageDraw, ImageOps
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QFont, QImage, QPixmap, QIcon, QPainter, QTextDocument, QFontMetrics, QAbstractTextDocumentLayout, QTextOption, QPageSize
from PyQt5.QtCore import Qt, QRect, QSizeF, QEvent, QRectF
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, QMainWindow, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton, QTextEdit, QHBoxLayout, QWidget, QFileDialog, QVBoxLayout, QDesktopWidget, QProgressBar
import sys


class CustomPlainTextEdit(QPlainTextEdit):
    # Essa é uma subclasse do QPlainTextEdit que nos permite
    # fazer um tratamento especial para a tecla Tab, fazendo-a
    # mover o foco para o próximo widget em vez de inserir um caractere de tabulação.
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
            myappid = 'Entregas 8.6'  # Um identificador arbitrário para o aplicativo
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.setWindowIcon(QIcon('favicon.ico'))
            self.centralizar()

        # definir janela principal
        self.setWindowTitle("ENTREGAS")
        self.setGeometry(100, 100, 500, 400)
        
        # Informações sobre cada loja
        self.loja_info = {
            "01": {"TELEFONE": "Telefone: (95) 3623-7063", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "02": {"TELEFONE": "Telefone: (95) 3627-1053", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "03": {"TELEFONE": "Telefone: (95) 3623-0207", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "04": {"TELEFONE": "Telefone: (95) 3623-7303", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "05": {"TELEFONE": "Telefone: (95) 3224-6545", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
            "06": {"TELEFONE": "Telefone: (95) 0000-0000", "WHATSAPP": "Whatsapp: (95) 3623-7063"},
        }
        self.telefone_loja = ""
        self.whatsapp_loja = ""
        self.loja_selecionada("01")
        
        # Criação dos widgets (campos de entrada e rótulos)
        self.tipo_entrega_label = QLabel("TIPO DE ENTREGA:")
        self.tipo_entrega_combo = QComboBox()
        self.tipo_entrega_combo.addItems(["ENTREGA BEE", "ENTREGA ROTA", "RETIRADA EM LOJA"])
        self.tipo_entrega_combo.currentTextChanged.connect(self.tipo_entrega_selecionada)
        self.loja_label = QLabel("LOJA:")
        self.loja_combo = QComboBox()
        self.loja_combo.addItems(["01", "02", "03", "04", "05", "06"])
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
        
    # Esta função é chamada quando a seleção no combo box de tipo de entrega muda.
    # Ela mostra ou oculta os botões e campos de entrada apropriados com base no tipo de entrega selecionado.
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

    # Esta função é usada para calcular a altura de um campo de entrada de texto com base em um número de linhas.
    def calcular_altura_campo_texto(self, campo, num_linhas):
        metricas_fonte = QFontMetrics(campo.font())
        altura = (metricas_fonte.lineSpacing() * num_linhas) + (campo.contentsMargins().top() + campo.contentsMargins().bottom())
        return altura        
        
    # Esta função é chamada quando a seleção no combo box de loja muda.
    # Ela atualiza os campos de telefone e whatsapp com base na loja selecionada.
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
        # Obtenha os dados do formulário
        tipo_entrega = self.tipo_entrega_combo.currentText()
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text().upper()
        telefone = self.telefone_edit.text().upper()
        produto = self.produto_edit.toPlainText().upper()
        endereco = self.endereco_edit.text().upper()
        valor = self.valor_edit.text().upper()
        forma_pag = self.forma_pag_edit.text().upper()
        obs = self.obs_edit.toPlainText().upper()

        # Se o campo forma_pag está vazio, preencha com "PAGO"
        if not forma_pag:
            forma_pag = "PAGO, SOMENTE ENTREGAR"

        # Se o campo valor é igual a "R$", então esvazie o campo
        if valor == "R$":
            valor = ""

        # Verifique se a pasta "Entregas" existe, caso contrário, crie-a
        if not os.path.exists(os.path.join(os.path.expanduser('~'), "Documents", "Entregas")):
            os.makedirs(os.path.join(os.path.expanduser('~'), "Documents", "Entregas"))

        # Crie um arquivo de texto com os dados do formulário
        filename = os.path.join(os.path.expanduser('~'), "Documents", "Entregas", f"{cliente}_{telefone}.txt")
        with open(filename, "w") as f:
            f.write(f"ENTREGAS\n")
            f.write(f"TIPO DE ENTREGA: {tipo_entrega}\n")
            f.write(f"LOJA: {loja}\n")
            f.write(f"CLIENTE: {cliente}\n")
            f.write(f"TELEFONE: {telefone}\n")
            f.write(f"PRODUTO: {produto}\n")
            f.write(f"ENDEREÇO: {endereco}\n")
            if valor != "":
                f.write(f"VALOR: {valor}\n")
            f.write(f"PAGAMENTO: {forma_pag}\n")
            f.write(f"OBSERVAÇÕES: {obs}\n")

        # Prepare os dados para copiar para a área de transferência
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
            if valor and valor.strip() != "R$":
                mensagem_formatada += f"*{campo}* {valor}\n"

        mensagem_formatada += "\n"

        # Copie a mensagem formatada para a área de transferência
        self.clipboard.setText(mensagem_formatada)

        # Mostre uma caixa de mensagem informando que o formulário foi gravado e copiado
        QMessageBox.information(self, "Gravado e Copiado", "Formulario Gravado e copiado com sucesso ^_^")

    def gerar_qrcode(self):
        # Obtenha os valores dos campos
        tipo_entrega = self.tipo_entrega_combo.currentText()
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text()
        
        # Obtenha o valor do campo de telefone e remova parênteses e hífens
        telefone = self.telefone_edit.text()
        telefone = telefone.replace('(', '').replace(')', '').replace(' ', '').replace('-', '')

        # Formate o número de telefone
        telefone = re.sub(r'(\d{2})(\d{4,5})(\d{4})', r'\1.\2-\3', telefone)
        
        produto = self.produto_edit.toPlainText()
        
        # Obtenha o valor do campo de endereço e divida no primeiro número encontrado
        endereco = self.endereco_edit.text()
        partes = re.split(r'(\d+)', endereco, maxsplit=1)

        try:
            # Remova qualquer espaço ou hífen imediatamente após o número e junte todas as partes de volta
            partes[2] = partes[2].lstrip(' -')
            endereco = "".join(partes[0:2]) + "_" + partes[2]

            # Divida o endereço no primeiro número encontrado e junte com um underscore
            partes = re.split(r'(\d+)', endereco, maxsplit=1)
            endereco = "_".join(partes)
        except IndexError:
            pass  # Ignore o erro e continue com o endereço original se não puder ser dividido
        
        valor = self.valor_edit.text()
        forma_pag = self.forma_pag_edit.text() if self.forma_pag_edit.text() else "PAGO, SOMENTE ENTREGAR"
        obs = self.obs_edit.toPlainText()

        # Crie uma string com os títulos e os valores dos campos
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
        if valor and valor.strip() != "R$":
            dados += f"*VALOR:* {valor}\n"
        dados += f"*PAGAMENTO:* {forma_pag}\n"
        if obs:
            dados += f"*OBSERVAÇÕES:* {obs}\n\n"
        
        dados += "\n\n"
        
        # Gere um QRCode com os dados
        qr = qrcode.QRCode(
            version=1,  # Aumente a versão do QRCode
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=1
        )
        qr.add_data(dados)
        qr.make(fit=True)
        qrcode_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Redimensione o QRCode para 250x250
        qrcode_img = qrcode_img.resize((250, 250), Image.NEAREST)

        # Salve a imagem como PNG
        png_file_path = "qrcode.png"
        qrcode_img.save(png_file_path)

        # Exiba o QRCode
        qrcode_img.show()

    # Use codificadores para ler documentos com vários caracteres
    def read_file_with_multiple_encodings(self, file_path, encodings=("utf-8", "cp1252", "latin-1")):
        for encoding in encodings:
            try:
                # Tente abrir e ler o arquivo com o codificador atual
                with open(file_path, "r", encoding=encoding) as f:
                    text = f.read()
                return text
            except UnicodeDecodeError:
                pass
        # Se nenhum dos codificadores funcionou, levante um erro
        raise UnicodeDecodeError("Nenhuma das codificações fornecidas funcionou.")

    def imprimir(self):
        # Configura uma impressora com alta resolução e margens definidas
        printer = QPrinter(QPrinter.HighResolution)
        printer.setPageMargins(2, 2, 2, 2, QPrinter.Millimeter)
        printer.setOutputFormat(QPrinter.NativeFormat)

        # Cria um diálogo de impressão
        dialog = QPrintDialog(printer, self)

        # Se o diálogo de impressão for aceito, continua com o processo de impressão
        if dialog.exec_() == QDialog.Accepted:
            dpi = printer.resolution()
            font_size = round(12 * dpi / 150)  # Ajusta o tamanho da fonte com base na resolução da impressora
            line_spacing = font_size * 0.5

            painter = QPainter()
            painter.begin(printer)
            font = QFont("Arial", font_size)
            painter.setFont(font)

            # Ajusta a largura do documento para 80mm
            mm_width = 80
            doc_width = int(mm_width / 30 * dpi)

            total_height = 0

            # Carrega o logo
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
            logo = QImage(logo_path)

            # Redimensiona o logo
            scaled_logo = logo.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_rect = QRect(0, 0, scaled_logo.width(), scaled_logo.height())
            painter.drawImage(logo_rect, scaled_logo)
            total_height += scaled_logo.height()

            # Ajusta a posição do painter
            painter.translate(20, 0)

            # Obtém as informações da loja
            loja_id = self.loja_combo.currentText().split(" - ")[0]
            loja_info = self.loja_info.get(loja_id, {"TELEFONE": "", "WHATSAPP": ""})
            phone_text = loja_info["TELEFONE"]
            whatsapp_text = loja_info["WHATSAPP"]

            # Configura a fonte para o telefone
            phone_font = QFont("Arial", font_size)
            painter.setFont(phone_font)
            painter.translate(scaled_logo.width(), 0)

            # Configura o documento para o telefone
            phone_doc = QTextDocument()
            phone_doc.setDefaultFont(phone_font)
            phone_doc.setPlainText(phone_text)
            phone_doc.setTextWidth(doc_width / 2)

            # Desenha o texto do telefone
            phone_ctx = QAbstractTextDocumentLayout.PaintContext()
            phone_layout = phone_doc.documentLayout()
            phone_layout.draw(painter, phone_ctx)

            # Move o "pincel" para baixo pela altura do texto do telefone
            painter.translate(0, phone_doc.size().height() + line_spacing)

            # Configura a fonte para o WhatsApp
            whatsapp_font = QFont("Arial", font_size)
            whatsapp_doc = QTextDocument()
            whatsapp_doc.setDefaultFont(whatsapp_font)
            whatsapp_doc.setPlainText(whatsapp_text)
            whatsapp_doc.setTextWidth(doc_width / 2)

            # Desenha o texto do WhatsApp
            whatsapp_ctx = QAbstractTextDocumentLayout.PaintContext()
            whatsapp_layout = whatsapp_doc.documentLayout()
            whatsapp_layout.draw(painter, whatsapp_ctx)

            # Move o "pincel" para baixo pela altura do texto do WhatsApp
            painter.translate(0, whatsapp_doc.size().height() + line_spacing)

            # Retoma a fonte original
            painter.setFont(font)
            painter.translate(-scaled_logo.width(), total_height)

            # Define os campos para impressão
            campos = [
                ("LOJA: ", self.loja_combo.currentText().upper().splitlines()),
                ("CLIENTE: ", self.cliente_edit.text().upper().splitlines()),
                ("TELEFONE: ", self.telefone_edit.text().upper().splitlines()),
                ("PRODUTO: ", self.produto_edit.toPlainText().upper().splitlines()),
                ("ENDEREÇO: ", self.endereco_edit.text().upper().splitlines()),
                ("VALOR: ", self.valor_edit.text().upper().splitlines() if self.valor_edit.text().strip() != "R$" else []),
                ("PAGAMENTO: ", self.forma_pag_edit.text().upper().splitlines() if self.forma_pag_edit.text().strip() else ["PAGO, SOMENTE ENTREGAR"]),
                ("OBSERVAÇÕES: ", self.obs_edit.toPlainText().upper().splitlines()),
            ]

            # Imprime cada campo
            for titulo, texto in campos:
                if not texto:
                    continue

                # Trata o caso em que o texto é uma lista
                if isinstance(texto, list):
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
                    # Caso o texto não seja uma lista
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

            # Finaliza o pintor, se ainda estiver ativo
            if painter.isActive():
                painter.end()

    # Adiciona função para abrir o link no Firefox
    def abrir_link_no_firefox(self):
        # Cria uma caixa de mensagem para a escolha do link
        msg = QMessageBox()
        msg.setWindowTitle("Escolha o link")
        msg.setText("Escolha o link que deseja abrir:")
        interno = msg.addButton('INTERNO', QMessageBox.YesRole)
        externo = msg.addButton('EXTERNO', QMessageBox.NoRole)
        msg.exec_()

        # Decide o link final com base na escolha do usuário
        if msg.clickedButton() == interno:
            self.final_link = "http://192.168.3.23:8080/Easytech/sg0026.do?method=gotoComando&comando=atd0102.do?method=prepTela"
            login_link = "http://192.168.3.23:8080/Easytech//sgw0001.do?method=login"
        else:
            self.final_link = "http://192.140.42.140:8080/Easytech/sg0026.do?method=gotoComando&comando=atd0102.do?method=prepTela"
            login_link = "http://192.140.42.140:8080/Easytech//sgw0001.do?method=login"

        # Configura a view do navegador web
        self.webView = QWebEngineView()

        # Cria uma barra de progresso
        self.progress = QProgressBar(self.webView)
        self.progress.resize(400, 20)
        self.progress.move(0, self.webView.height() - self.progress.height())
        self.progress.show()

        # Conecta os sinais à barra de progresso
        self.webView.loadStarted.connect(self.inicio_carregamento)
        self.webView.loadProgress.connect(self.progress.setValue)
        self.webView.loadFinished.connect(self.fim_carregamento)

        # Carrega o link de login
        self.webView.load(QUrl(login_link))
        self.webView.show()
        self.webView.urlChanged.connect(self.manipulaMudancaUrl)

    # Método para o início do carregamento da página
    def inicio_carregamento(self):
        self.progress.setValue(0)  # Valor mínimo quando o carregamento começar

    # Método para o fim do carregamento da página
    def fim_carregamento(self):
        self.progress.setValue(100)  # Valor máximo quando o carregamento terminar
        QTimer.singleShot(5000, self.progress.hide)  # Esconder a barra de progresso 5 segundos após o carregamento terminar

    # Método para tratar a mudança de URL
    def manipulaMudancaUrl(self, url):
        # Se a URL contém "buscarEmpresa", carrega o link final
        if "buscarEmpresa" in url.toString():
            self.webView.load(QUrl(self.final_link))
        # Se a URL contém "method=gravar", fecha a janela após 5 segundos
        elif "method=gravar" in url.toString():
            QTimer.singleShot(5000, self.webView.close)
                
    def editar(self):
        # Define o caminho para a pasta de entregas
        folder_path = os.path.join(os.path.expanduser('~'), "Documents", "Entregas")

        # Cria um diálogo para abrir um arquivo no diretório de entregas
        filename, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo", folder_path, "Arquivos de texto (*.txt)")

        # Se um arquivo for selecionado, o conteúdo do arquivo é lido e os campos do formulário são preenchidos
        if filename:
            with open(filename, "r") as f:
                lines = f.readlines()

            # Dicionário para armazenar os valores dos campos
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

            # Para cada linha no arquivo, procura por cada campo e salva o valor correspondente
            for line in lines:
                for campo in campos:
                    if line.startswith(campo):
                        campos[campo] = line.split(":")[1].strip()
                        break

            # Define os valores dos campos do formulário
            self.tipo_entrega_combo.setCurrentText(campos["TIPO DE ENTREGA"])
            self.loja_combo.setCurrentText(campos["LOJA"])
            self.cliente_edit.setText(campos["CLIENTE"])
            self.telefone_edit.setText(campos["TELEFONE"])
            self.produto_edit.setPlainText(campos["PRODUTO"])
            self.endereco_edit.setText(campos["ENDEREÇO"])
            
            if campos["VALOR"] != "PAGO, SOMENTE ENTREGAR":
                self.valor_edit.setText(campos["VALOR"])
            
            if campos["PAGAMENTO"] != "PAGO, SOMENTE ENTREGAR":
                self.forma_pag_edit.setText(campos["PAGAMENTO"])
            
            self.obs_edit.setPlainText(campos["OBSERVAÇÕES"])
        else:
            # Se o arquivo não foi gerado pelo programa, exibe uma mensagem de aviso
            QMessageBox.warning(self, "Arquivo incompatível", "Esse arquivo não foi feito por mim, parça!") 

    # Método para obter o valor de um campo específico em um texto
    def get_field_value(self, field_name, text):
        start_index = text.find(field_name)
        if start_index == -1:
            return ""

        start_index += len(field_name)
        end_index = text.find("\n", start_index)
        if end_index == -1:
            return text[start_index:].strip()

        return text[start_index:end_index].strip()

    # Método para carregar o formulário com os valores dos campos copiados
    def carregar_formulario(self):
        # Obtem o texto copiado
        clipboard_text = QApplication.clipboard().text()

        # Obtem valores dos campos usando a função get_field_value
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

        # Preenche os widgets do formulário com os valores correspondentes
        self.tipo_entrega_combo.setCurrentIndex(self.tipo_entrega_combo.findText(tipo_entrega))
        self.loja_combo.setCurrentText(loja)
        self.cliente_edit.setText(cliente)
        self.telefone_edit.setText(telefone)
        self.produto_edit.setPlainText(produto)
        self.endereco_edit.setText(endereco)
        
        if valor != "PAGO, SOMENTE ENTREGAR":
            self.valor_edit.setText(valor)
        
        if forma_pag != "PAGO, SOMENTE ENTREGAR":
            self.forma_pag_edit.setText(forma_pag)
        
        self.obs_edit.setPlainText(obs)

    # Método para limpar todos os campos do formulário
    def limpar(self):
        self.loja_combo.setCurrentIndex(0)
        self.cliente_edit.clear()
        self.telefone_edit.clear()
        self.produto_edit.clear()
        self.endereco_edit.clear()
        self.valor_edit.clear()
        self.forma_pag_edit.clear()
        self.obs_edit.clear()

    # Método para formatar o telefone
    def formatar_telefone(self):
        telefone = self.telefone_edit.text()
        if len(telefone) == 11 and not telefone.startswith("("):
            telefone_formatado = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
            self.telefone_edit.setText(telefone_formatado)

    # Método para formatar o valor
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

    # Método para verificar se o campo de valor está vazio
    def valor_edit_focusInEvent(self, event):
        valor = self.valor_edit.text()
        if valor == 'R$ 0,00':
            self.valor_edit.clear()
            self.valor_edit.setPlaceholderText("R$")
        elif not valor.startswith("R$"):
            self.valor_edit.setText(f"R$ {valor}")
        super(QLineEdit, self.valor_edit).focusInEvent(event)

    # Método para centralizar a janela
    def centralizar(self):
        frame = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center_point)
        self.move(frame.topLeft())
        

# Definição da janela principal
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Entregas()
    window.show()
    sys.exit(app.exec_())
