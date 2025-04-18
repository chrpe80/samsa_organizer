from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGroupBox,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStackedWidget
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
import sys
import re
from db_handler import DatabaseOperations

# Creating instance of the class DatabaseOperations
dbo = DatabaseOperations()


class Table(QTableWidget):
    """This class inherits the QTableWidget for convenience"""

    __slots__ = "data"

    def __init__(self, data: list):
        super().__init__()
        self.data = data
        self.setRowCount(len(self.data))
        self.setColumnCount(5)
        self.setFixedWidth(750)
        self.setFixedHeight(500)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setAlternatingRowColors(True)
        self.setStyleSheet("QTableWidget {background-color: white; alternate-background-color: #FAFA94;}")
        self.populate()

    def populate(self):
        for row_idx, row_data in enumerate(self.data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row_idx, col_idx, item)


class MainWindow(QMainWindow):
    """The app"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Verktyg")
        self.setGeometry(0, 0, 800, 700)
        self.setStyleSheet("background-color: rgb(250, 250, 250);")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.page_add = self.create_add_page()
        self.page_delete = self.create_delete_page()
        self.page_update = self.create_update_page()
        self.page_read = self.create_display_page()
        self.stack.addWidget(self.page_add)
        self.stack.addWidget(self.page_delete)
        self.stack.addWidget(self.page_update)
        self.stack.addWidget(self.page_read)
        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("background-color: rgb(240, 240, 240); color: black;")
        file_menu = menu_bar.addMenu("Meny")
        add_action = QAction("Lägg till", self)
        add_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_add))
        file_menu.addAction(add_action)
        delete_action = QAction("Ta bort", self)
        delete_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_delete))
        file_menu.addAction(delete_action)
        update_action = QAction("Uppdatera", self)
        update_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_update))
        file_menu.addAction(update_action)
        read_action = QAction("Läs", self)
        read_action.triggered.connect(lambda: self.stack.setCurrentWidget(self.page_read))
        file_menu.addAction(read_action)
        fullscreen_action = QAction("Helskärm", self)
        fullscreen_action.triggered.connect(self.showFullScreen)
        file_menu.addAction(fullscreen_action)
        normal_action = QAction("Återställ", self)
        normal_action.triggered.connect(self.showNormal)
        file_menu.addAction(normal_action)
        quit_action = QAction("Avsluta", self)
        quit_action.triggered.connect(QApplication.quit)
        file_menu.addAction(quit_action)
        file_menu.setStyleSheet("""
            QMenu {background-color: rgb(240, 240, 240); color: rgb(40, 40, 40);}
            QMenu::item {background-color: transparent;}
            QMenu::item:selected {background-color: gray; color: white;}
        """)

    def create_add_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox("Lägg till")
        group_box.setFixedSize(500, 600)
        group_box.setStyleSheet("QGroupBox {background-color: #FAFA94; border: none;}")
        group_layout = QVBoxLayout()
        first = QLineEdit(placeholderText="Förnamn")
        last = QLineEdit(placeholderText="Efternamn")
        personal_nr = QLineEdit(placeholderText="Personnummer (ååmmdd-xxxx)")
        belonging_to = QLineEdit(placeholderText="Tillhör (Inte inskriven, Aggis, Maggis, Centrum, Norrmalm)")
        comment = QLineEdit(placeholderText="Kommentar")
        comment.setMaxLength(20)
        to_be_cleared = (first, last, personal_nr, belonging_to, comment)
        button = QPushButton("Spara")
        button.clicked.connect(lambda: self.add_button_pressed((
            first.text(),
            last.text(),
            personal_nr.text(),
            belonging_to.text(),
            comment.text()
        ), to_be_cleared))
        inputs = (first, last, personal_nr, belonging_to, comment, button)
        for i in inputs:
            i.setFixedHeight(40)
            group_layout.addWidget(i)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        page.setLayout(layout)
        return page

    def create_delete_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox("Ta bort")
        group_box.setFixedSize(500, 200)
        group_box.setStyleSheet("QGroupBox {background-color: #FAFA94; border: none;}")
        group_layout = QVBoxLayout()
        personal_nr = QLineEdit(placeholderText="Personnummer (ååmmdd-xxxx)")
        button = QPushButton("Spara")
        button.clicked.connect(lambda: self.del_button_pressed(personal_nr.text(), personal_nr))
        inputs = (personal_nr, button)
        for i in inputs:
            i.setFixedHeight(40)
            group_layout.addWidget(i)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        page.setLayout(layout)
        return page

    def create_update_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox("Uppdatera")
        group_box.setFixedSize(500, 400)
        group_box.setStyleSheet("QGroupBox { background-color: #FAFA94; border: none;}")
        group_layout = QVBoxLayout()
        target_col = QLineEdit(placeholderText="Kolumn (Förnamn, Efternamn, Personnummer, Tillhörighet, Kommentar)")
        new_value = QLineEdit(placeholderText="Nytt värde")
        new_value.setMaxLength(20)
        personal_nr = QLineEdit(placeholderText="Personnummer (ååmmdd-xxxx)")
        to_be_cleared = (target_col, new_value, personal_nr)
        button = QPushButton("Spara")
        button.clicked.connect(lambda: self.update_button_pressed((
            target_col.text(),
            new_value.text(),
            personal_nr.text(),
        ), to_be_cleared))
        inputs = (target_col, new_value, personal_nr, button)
        for i in inputs:
            i.setFixedHeight(40)
            group_layout.addWidget(i)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box, alignment=Qt.AlignCenter)
        page.setLayout(layout)
        return page

    def create_display_page(self):
        result = dbo.get_all_from_table()
        table = Table(result)
        page = QWidget()
        layout = QVBoxLayout()
        button = QPushButton("Uppdatera")
        button.clicked.connect(lambda: self.update_table(table))
        button.setFixedWidth(500)
        button.setFixedHeight(50)
        button.setStyleSheet("QPushButton {background-color: #FAFA94;}")
        layout.addWidget(table, alignment=Qt.AlignCenter)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        page.setLayout(layout)
        return page

    @staticmethod
    def add_button_pressed(data: tuple, to_be_cleared: tuple):
        personal_nr = data[2]
        belonging_to = data[3]
        personal_nr_column = dbo.get_personal_numbers()
        personal_nrs = [item[0] for item in personal_nr_column]
        personal_nr_pattern = r'^\d{6}-\d{4}$'
        approved = ("inte inskriven", "aggis", "maggis", "centrum", "norrmalm")
        cond1 = personal_nr not in personal_nrs
        cond2 = re.match(personal_nr_pattern, personal_nr)
        cond3 = belonging_to.lower() in approved
        if all((cond1, cond2, cond3)):
            data = [item.upper() for item in data]
            dbo.new_record(tuple(data))
        else:
            print("error")
        for item in to_be_cleared:
            item.clear()

    @staticmethod
    def del_button_pressed(data: str, widget):
        personal_nr_column = dbo.get_personal_numbers()
        personal_nrs = [item[0] for item in personal_nr_column]
        condition = data in personal_nrs
        match condition:
            case True:
                dbo.delete_record(data)
            case False:
                print("error")
        widget.clear()

    @staticmethod
    def update_button_pressed(data: tuple, to_be_cleared: tuple):
        target_col, new_value, personal_nr = data
        personal_nr_column = dbo.get_personal_numbers()
        personal_nrs = [item[0] for item in personal_nr_column]
        approved = ("inte inskriven", "aggis", "maggis", "centrum", "norrmalm")
        if target_col.lower() == "tillhörighet" and new_value.lower() in approved and personal_nr in personal_nrs:
            dbo.update_record(target_col.lower(), new_value.upper(), personal_nr)
        elif target_col.lower() in ("förnamn", "efternamn", "kommentar") and personal_nr in personal_nrs:
            dbo.update_record(target_col.lower(), new_value.upper(), personal_nr)
        else:
            print("error")
        for item in to_be_cleared:
            item.clear()

    @staticmethod
    def update_table(table):
        data = dbo.get_all_from_table()
        rows = len(data)
        columns = 5
        table.clear()
        table.setRowCount(rows)
        table.setColumnCount(columns)
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row_idx, col_idx, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
