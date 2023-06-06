import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QDialog, QFormLayout,
    QListWidgetItem, QHBoxLayout, QVBoxLayout, QMessageBox, QGridLayout, QTabWidget, QDialogButtonBox, QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView
)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt


class AddMemberDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("회원 등록")
        self.setFixedSize(300, 200)

        self.phoneLineEdit = QLineEdit()
        self.nameLineEdit = QLineEdit()
        self.homeLineEdit = QLineEdit()

        formLayout = QFormLayout()
        formLayout.addRow(QLabel("전화번호"), self.phoneLineEdit)
        formLayout.addRow(QLabel("이름"), self.nameLineEdit)
        formLayout.addRow(QLabel("주소"), self.homeLineEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(formLayout)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def getMemberInfo(self):
        phone_number = self.phoneLineEdit.text().strip()
        name = self.nameLineEdit.text().strip()
        home_address = self.homeLineEdit.text().strip()
        return phone_number, name, home_address
