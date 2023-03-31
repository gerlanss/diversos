import os
import subprocess
import platform
import ctypes
import sys
import fitz
import pdfplumber
from PyQt5.QtPrintSupport import QPageSetupDialog
from PyQt5.QtGui import QPdfWriter
from PyPDF2 import PdfReader
from PyQt5.QtWidgets import QVBoxLayout, QDesktopWidget, QSizePolicy, QSpacerItem, QVBoxLayout, QAction, QToolBar, QApplication, QMainWindow, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton, QTextEdit, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QIcon, QClipboard, QFont, QPainter, QImage, QPixmap, QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QMessageBox, QLineEdit, QLabel, QPushButton, QTextEdit, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from fpdf import FPDF


class EntregaBee(QMainWindow):
    def __init__(self):
        super().__init__()
        if os.name == 'nt':  # Verifica se o sistema operacional é Windows
            # Carrega o ícone para o aplicativo
            myappid = 'Entrega Bee 4.0'  # Um identificador arbitrário para o aplicativo
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.setWindowIcon(QIcon('favicon.ico'))
            self.clipboard = QApplication.clipboard()
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
        
    def formatar_telefone(self):
        telefone = self.telefone_edit.text()
        telefone = telefone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if len(telefone) == 11:
            telefone = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:
            telefone = f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        self.telefone_edit.setText(telefone)
        
    def valor_edit_focusInEvent(self, event):
        if self.valor_edit.text() == "":
            self.valor_edit.setText("R$")
            
    def formatar_valor(self):
        valor = self.valor_edit.text().replace("R$", "").replace(",", ".").strip()
        if valor:
            try:
                valor = float(valor)
                self.valor_edit.setText(f"R$ {valor:.2f}")
            except ValueError:
                QMessageBox.warning(self, "Valor inválido", "O valor informado não é válido. Por favor, corrija-o.")
                self.valor_edit.setText("R$")
    
    def gravar_copiar(self):
        loja = self.loja_combo.currentText()
        cliente = self.cliente_edit.text().upper()
        telefone = self.telefone_edit.text().upper()
        produto = self.produto_edit.text().upper()
        endereco = self.endereco_edit.text().upper()
        valor = self.valor_edit.text().upper()
        forma_pag = self.forma_pag_edit.text().upper()
        obs = self.obs_edit.toPlainText().upper()

        # Verificar se pasta de Entrega Bee existe
        if not os.path.exists(os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee")):
            os.makedirs(os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee"))

        # Criar arquivo PDF
        filename = os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee", f"{cliente}_{telefone}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)

        pdf.cell(200, 10, txt=f"LOJA: {loja}", ln=1)
        pdf.cell(200, 10, txt=f"CLIENTE: {cliente}", ln=1)
        pdf.cell(200, 10, txt=f"TELEFONE: {telefone}", ln=1)
        pdf.cell(200, 10, txt=f"PRODUTO: {produto}", ln=1)
        pdf.cell(200, 10, txt=f"ENDEREÇO: {endereco}", ln=1)
        pdf.cell(200, 10, txt=f"VALOR: {valor}", ln=1)
        pdf.cell(200, 10, txt=f"PAGAMENTO: {forma_pag}", ln=1)
        pdf.cell(200, 10, txt=f"OBSERVAÇÕES: {obs}", ln=1)

        pdf.output(name=filename)

        # Copiar para a área de transferência
        mensagem_formatada = f"*ENTREGA BEE*\n\n*LOJA:* {loja}\n*CLIENTE:* {cliente}\n*TELEFONE:* {telefone}\n*PRODUTO:* {produto}\n*ENDEREÇO:* {endereco}\n*VALOR:* {valor}\n*PAGAMENTO:* {forma_pag}\n*OBSERVAÇÕES:* {obs}"
        self.clipboard.setText(mensagem_formatada)

        QMessageBox.information(self, "Gravado e Copiado", "Os dados foram gravados e copiados para a área de transferência.")
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
    
    
    def get_last_saved_file(self):
        folder_path = os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee")
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file
        
    def render_pdf(self, printer, painter):
        with painter:
            loja = self.loja_combo.currentText()
            cliente = self.cliente_edit.text().upper()
            telefone = self.telefone_edit.text().upper()
            produto = self.produto_edit.text().upper()
            endereco = self.endereco_edit.text().upper()
            valor = self.valor_edit.text().upper()
            forma_pag = self.forma_pag_edit.text().upper()
            obs = self.obs_edit.toPlainText().upper()

            printer.setPageSize(QPrinter.Letter)
            printer.setFullPage(True)
            painter.setFont(QFont("Arial", 12))
            yOffset = 40
            painter.drawText(40, yOffset, f"LOJA: {loja}")
            yOffset += 20
            painter.drawText(40, yOffset, f"CLIENTE: {cliente}")
            yOffset += 20
            painter.drawText(40, yOffset, f"TELEFONE: {telefone}")
            yOffset += 20
            painter.drawText(40, yOffset, f"PRODUTO: {produto}")
            yOffset += 20
            painter.drawText(40, yOffset, f"ENDEREÇO: {endereco}")
            yOffset += 20
            painter.drawText(40, yOffset, f"VALOR: {valor}")
            yOffset += 20
            painter.drawText(40, yOffset, f"PAGAMENTO: {forma_pag}")
            yOffset += 20
            painter.drawText(40, yOffset, f"OBSERVAÇÕES: {obs}")
        
    def imprimir(self):
        fileName = os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee", f"{self.cliente_edit.text()}_{self.telefone_edit.text()}.pdf")

        # Verificar se o arquivo existe
        if os.path.exists(fileName):
            # Abrir o arquivo PDF no visualizador
            doc = fitz.open(fileName)
            pdf_viewer = PdfViewerWindow(self)
            pdf_viewer.view_pdf(doc)
            pdf_viewer.show()
            doc.close()
        else:
            QMessageBox.warning(self, "Arquivo não encontrado", "O arquivo PDF não foi encontrado. Por favor, certifique-se de que o arquivo foi criado.")
        
    def abrir_whatsapp(self):
        if platform.system() == "Windows":
            try:
                subprocess.Popen("explorer shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App")
            except FileNotFoundError:
                pass

    def extract_text_from_pdf(self, file_path):
        with pdfplumber.open(file_path) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text

           
    def abrir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Abrir arquivo PDF", os.path.join(os.path.expanduser('~'), "Documents", "Entrega Bee"), "PDF Files (*.pdf)", options=options)
        if fileName:
            # Extrair o texto do arquivo PDF
            text = self.extract_text_from_pdf(fileName)

            # Função para preencher o formulário com base no texto extraído
            self.fill_form_from_pdf_text(text)

    def fill_form_from_pdf_text(self, text):
        lines = text.split('\n')

        for line in lines:
            if line.startswith("LOJA:"):
                loja = line.replace("LOJA:", "").strip()
                index = self.loja_combo.findText(loja)
                if index != -1:
                    self.loja_combo.setCurrentIndex(index)
            elif line.startswith("CLIENTE:"):
                cliente = line.replace("CLIENTE:", "").strip()
                self.cliente_edit.setText(cliente)
            elif line.startswith("TELEFONE:"):
                telefone = line.replace("TELEFONE:", "").strip()
                self.telefone_edit.setText(telefone)
            elif line.startswith("PRODUTO:"):
                produto = line.replace("PRODUTO:", "").strip()
                self.produto_edit.setText(produto)
            elif line.startswith("ENDEREÇO:"):
                endereco = line.replace("ENDEREÇO:", "").strip()
                self.endereco_edit.setText(endereco)
            elif line.startswith("VALOR:"):
                valor = line.replace("VALOR:", "").strip()
                self.valor_edit.setText(valor)
            elif line.startswith("PAGAMENTO:"):
                forma_pag = line.replace("PAGAMENTO:", "").strip()
                self.forma_pag_edit.setText(forma_pag)
            elif line.startswith("OBSERVAÇÕES:"):
                obs = line.replace("OBSERVAÇÕES:", "").strip()
                self.obs_edit.setPlainText(obs)


    def limpar(self):
        self.cliente_edit.clear()
        self.telefone_edit.clear()
        self.produto_edit.clear()
        self.endereco_edit.clear()
        self.valor_edit.setText("R$")
        self.forma_pag_edit.clear()
        self.obs_edit.clear()

class PdfViewerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ENTREGA BEE")
        self.label = QLabel(self)

        # Adicionar botão de imprimir a uma barra de ferramentas
        self.print_button = QPushButton("Imprimir")
        self.print_button.clicked.connect(self.print_pdf)
        self.print_button.setShortcut('Ctrl+P')
        self.toolbar = self.addToolBar("Imprimir")
        self.toolbar.addWidget(self.print_button)

        self.setCentralWidget(self.label)

        # Centralizar janela na tela
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(int(screen.width() / 2 - 250), int(screen.height() / 2 - 250), 400, 600)
        
    #Cortar imagem antes de colocar no visualizador PDF
    def crop_image(self, image):
        # Converta QImage para QPixmap
        pixmap = QPixmap.fromImage(image)

        # Obtenha a cor de fundo do canto superior esquerdo
        background_color = QColor(image.pixel(0, 0))

        # Encontre os limites da área de conteúdo
        left, top, right, bottom = 0, 0, pixmap.width(), pixmap.height()

        for x in range(pixmap.width()):
            for y in range(pixmap.height()):
                if QColor(pixmap.toImage().pixel(x, y)) != background_color:
                    left = x
                    break
            if left > 0:
                break

        for x in range(pixmap.width() - 1, -1, -1):
            for y in range(pixmap.height()):
                if QColor(pixmap.toImage().pixel(x, y)) != background_color:
                    right = x + 1
                    break
            if right < pixmap.width():
                break

        for y in range(pixmap.height() - 1, -1, -1):
            for x in range(pixmap.width()):
                if QColor(pixmap.toImage().pixel(x, y)) != background_color:
                    bottom = y + 1
                    break
            if bottom < pixmap.height():
                break

        # Corte a imagem
        cropped_pixmap = pixmap.copy(left, top, right - left, bottom - top)
        return cropped_pixmap

    #Visualizador PDF    
    def view_pdf(self, doc):
        page = doc.load_page(0)  # Carregar a primeira página do documento
        zoom = 1  # Aumentar o fator de zoom para melhorar a qualidade da imagem
        matrix = fitz.Matrix(zoom, zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)

        image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # Cortar a imagem para remover o fundo em branco
        cropped_pixmap = self.crop_image(image)

        # Redimensionar a imagem proporcionalmente para caber na janela
        max_width = self.width() - 20
        max_height = self.height() - 20 - self.toolbar.height()
        scaled_pixmap = cropped_pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Ajustar o tamanho da janela ao novo tamanho da imagem
        new_window_width = scaled_pixmap.width() + 20
        new_window_height = scaled_pixmap.height() + 20 + self.toolbar.height()
        self.resize(new_window_width, new_window_height)

        self.label.setPixmap(scaled_pixmap)
        self.label.resize(scaled_pixmap.width(), scaled_pixmap.height())

        self.pdf_doc = doc
      
    def print_pdf(self):
        if not hasattr(self, 'pdf_doc'):
            return

        printer = QPrinter()
        printer.setPageSize(QPrinter.Letter)
        printer.setOutputFormat(QPrinter.NativeFormat)

        print_dialog = QPrintDialog(printer, self)
        if print_dialog.exec_() == QPrintDialog.Accepted:
            # Defina o número total de páginas a serem impressas
            printer.setFromTo(1, self.pdf_doc.page_count)

            # Prepare o documento para a impressão
            for i in range(self.pdf_doc.page_count):
                page = self.pdf_doc.load_page(i)
                zoom = 1
                matrix = fitz.Matrix(zoom, zoom)
                pixmap = page.get_pixmap(matrix=matrix, alpha=False)
                image = QImage(pixmap.samples, pixmap.width, pixmap.height, pixmap.stride, QImage.Format_RGB888)
                qpixmap = QPixmap.fromImage(image)
                printer.newPage()
                painter = QPainter(printer)
                painter.drawPixmap(0, 0, qpixmap)
                painter.end()

            self.pdf_doc.close()
            self.hide()  # Esconda a janela do visualizador de PDF

              
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    main = EntregaBee()
    main.show()
    sys.exit(app.exec_())
