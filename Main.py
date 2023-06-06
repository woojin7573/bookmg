import sys
import mysql.connector
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QDialog, QFormLayout,
    QListWidgetItem, QHBoxLayout, QVBoxLayout, QMessageBox, QGridLayout, QTabWidget, QDialogButtonBox,
    QMainWindow, QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QCalendarWidget
)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import Qt
from AddMemberDialog import AddMemberDialog
from PyQt5.QtCore import QDate
from datetime import datetime








class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)  # UI 크기 조절
        # books 속성 초기화
        self.books = []
        # MySQL 연결 정보
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dhkdn~1324",
            database="bookinforo"
        )

        # 전체 책 목록을 표시할 테이블 위젯
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(6)  # 책 제목, 출판사, 대여 여부, 반납 예정일 열
        self.tableWidget.setHorizontalHeaderLabels(["ISBN", "책 제목", "저자", "출판사", "대여 여부", "반납 예정일"])
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 셀 편집 금지
        self.tableWidget.setColumnWidth(0, 200)  # 첫 번째 열의 너비를 200 픽셀로 설정


        # 검색 기능을 수행할 QLineEdit 위젯과 검색 버튼
        self.searchLineEdit = QLineEdit(self)
        self.searchButton = QPushButton("검색", self)
        self.searchResultListWidget = QListWidget(self)
        self.searchResultListWidget.setVisible(False)
        self.searchButton.clicked.connect(self.searchBooks)



        # 책 등록 버튼, 책 수정 버튼, 책 삭제 버튼, 회원 등록 버튼, 대여 버튼, 반납 버튼
        self.addBookButton = QPushButton("책 등록", self)
        self.addBookButton.clicked.connect(self.showAddBookDialog)
        self.editBookButton = QPushButton("책 수정", self)
        # 책 수정 다이얼로그 내부에서 사용할 변수
        self.selected_book_isbn = None
        self.selected_book_info = None
        self.editBookButton.clicked.connect(self.showEditBookDialog)
        self.deleteBookButton = QPushButton("책 삭제", self)
        self.deleteBookButton.clicked.connect(self.deleteBook)
        self.addMemberButton = QPushButton("회원 등록", self)
        self.addMemberButton.clicked.connect(self.showAddMemberDialog)
        self.rentButton = QPushButton("대여", self)
        self.rentButton.clicked.connect(self.rentBook)
        self.returnButton = QPushButton("반납", self)
        self.returnButton.clicked.connect(self.returnBook)


        # 레이아웃 구성
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.searchLineEdit)
        hbox1.addWidget(self.searchButton)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.addBookButton)
        hbox2.addWidget(self.editBookButton)
        hbox2.addWidget(self.deleteBookButton)
        hbox2.addWidget(self.addMemberButton)
        hbox2.addWidget(self.rentButton)
        hbox2.addWidget(self.returnButton)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addWidget(self.tableWidget)
        vbox.addLayout(hbox2)

        self.setLayout(vbox)

        # 전체 책 목록 로드
        self.loadAllBooks()

    def loadAllBooks(self):
        cursor = self.conn.cursor()

        # bookinformation 테이블과 rentinformation 테이블 조인하여 대여 여부와 반납 예정일 계산
        sql = "SELECT bi.isbn, bi.bookname, bi.writer, bi.publisher, " \
              "IF(ri.return_date IS NULL, '대여 가능', '대여 중') as status, " \
              "ri.return_date " \
              "FROM bookinformation AS bi LEFT OUTER JOIN rentinformation AS ri " \
              "ON bi.isbn = ri.isbn " \
              "GROUP BY bi.isbn"

        cursor.execute(sql)
        books = cursor.fetchall()

        self.tableWidget.setRowCount(len(books))

        for i, book in enumerate(books):
            for j in range(6):
                item = QTableWidgetItem(str(book[j]))
                self.tableWidget.setItem(i, j, item)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # 첫 번째 열은 남은 영역을 모두 채우도록 함
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 두 번째 열은 남은 영역을 모두 채우도록 함
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 세 번째 열은 셀의 내용에 맞게 크기를 조정함
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # 네 번째 열은 셀의 내용에 맞게 크기를 조정함
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # 다섯 번째 열은 셀의 내용에 맞게 크기를 조정함
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # 여섯 번째 열은 셀의 내용에 맞게 크기를 조정함

        cursor.close()


    def searchBooks(self):
        searchKeyword = self.searchLineEdit.text()

        cursor = self.conn.cursor()

        # bookinformation 테이블과 rentinformation 테이블 조인하여 대여 여부와 반납 예정일 계산
        sql = "SELECT bookinformation.isbn, bookinformation.bookname, bookinformation.writer, bookinformation.publisher, " \
              "IF(rentinformation.return_date IS NULL, '대여 가능', '대여 중'), rentinformation.return_date " \
              "FROM bookinformation LEFT OUTER JOIN rentinformation " \
              "ON bookinformation.isbn = rentinformation.isbn " \
              "WHERE bookinformation.isbn LIKE %s OR bookinformation.bookname LIKE %s OR bookinformation.writer LIKE %s OR bookinformation.publisher LIKE %s " \
              "GROUP BY bookinformation.isbn"

        cursor.execute(sql, ('%' + searchKeyword + '%', '%' + searchKeyword + '%', '%' + searchKeyword + '%', '%' + searchKeyword + '%'))

        books = cursor.fetchall()

        if not books:
            # 검색 결과가 없으면 메시지 박스를 표시함
            QMessageBox.information(self, "검색 결과", "검색 결과가 없습니다.")
        else:
            self.tableWidget.setRowCount(len(books))

            for i, book in enumerate(books):
                for j in range(6):
                    item = QTableWidgetItem(str(book[j]))
                    self.tableWidget.setItem(i, j, item)

            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # 첫 번째 열은 남은 영역을 모두 채우도록 함
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # 두 번째 열은 남은 영역을 모두 채우도록 함
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # 세 번째 열은 셀의 내용에 맞게 크기를 조정함
            header.setSectionResizeMode(3, QHeaderView.Stretch)  # 네 번째 열은 셀의 내용에 맞게 크기를 조정함
            header.setSectionResizeMode(4, QHeaderView.Stretch)  # 다섯 번째 열은 셀의 내용에 맞게 크기를 조정함
            header.setSectionResizeMode(5, QHeaderView.Stretch)  # 여섯 번째 열은 셀의 내용에 맞게 크기를 조정함

        cursor.close()

    def addBook(self):
        cursor = self.conn.cursor()
        sql = "INSERT INTO bookinformation (isbn, bookname, writer, publisher) VALUES (%s, %s, %s, %s)"
        data = (self.isbnLineEdit.text(), self.booknameLineEdit.text(), self.writerLineEdit.text(), self.publisherLineEdit.text())
        cursor.execute(sql, data)
        self.conn.commit()
        cursor.close()

        # Show a message box to indicate that the book has been added successfully
        QMessageBox.information(self, "책 등록", "책이 등록되었습니다.")

        # Close the add book dialog and return to the main screen
        self.addBookDialog.close()
        self.loadAllBooks()
        self.conn.close()

    def showAddBookDialog(self):
        self.addBookFormLayout = QFormLayout()
        self.isbnLineEdit = QLineEdit()
        self.addBookFormLayout.addRow(QLabel("ISBN"), self.isbnLineEdit)
        self.booknameLineEdit = QLineEdit()
        self.addBookFormLayout.addRow(QLabel("책 제목"), self.booknameLineEdit)
        self.writerLineEdit = QLineEdit()
        self.addBookFormLayout.addRow(QLabel("저자"), self.writerLineEdit)
        self.publisherLineEdit = QLineEdit()
        self.addBookFormLayout.addRow(QLabel("출판사"), self.publisherLineEdit)

        self.addButtonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.addButtonBox.accepted.connect(self.addBook)

        # Define addBookDialog as an instance variable
        self.addBookDialog = QDialog(self)
        self.addBookDialog.setLayout(self.addBookFormLayout)
        self.addBookDialog.setWindowTitle("책 등록")

        self.addButtonBox.rejected.connect(self.addBookDialog.reject)
        self.addBookFormLayout.addWidget(self.addButtonBox)

        self.addBookDialog.exec_()

    def showEditBookDialog(self):
        cursor = self.conn.cursor()

        # 책 선택 여부 확인
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if len(selected_rows) != 1:
            QMessageBox.warning(self, "경고", "책을 선택하세요.")
            return
        else:
            # 선택된 책 정보 저장
            selected_row = selected_rows[0].row()
            self.selected_book_isbn = self.tableWidget.item(selected_row, 0).text()
            self.selected_book_info = [
                self.tableWidget.item(selected_row, 1).text(),
                self.tableWidget.item(selected_row, 2).text(),
                self.tableWidget.item(selected_row, 3).text(),
            ]

        # 책 정보 수정 다이얼로그 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("책 수정")
        dialog.setModal(True)

        form_layout = QFormLayout()

        isbn_label = QLabel("ISBN")
        isbn_edit = QLineEdit(self.selected_book_isbn)
        isbn_edit.setReadOnly(True)

        bookname_label = QLabel("책 제목")
        bookname_edit = QLineEdit(self.selected_book_info[0])

        writer_label = QLabel("작가")
        writer_edit = QLineEdit(self.selected_book_info[1])

        publisher_label = QLabel("출판사")
        publisher_edit = QLineEdit(self.selected_book_info[2])

        form_layout.addRow(isbn_label, isbn_edit)
        form_layout.addRow(bookname_label, bookname_edit)
        form_layout.addRow(writer_label, writer_edit)
        form_layout.addRow(publisher_label, publisher_edit)

        # "저장" 버튼 추가
        saveButtonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        saveButtonBox.accepted.connect(lambda: self.saveChanges(dialog, bookname_edit, writer_edit, publisher_edit))
        saveButtonBox.rejected.connect(dialog.reject)
        form_layout.addRow(saveButtonBox)

        dialog.setLayout(form_layout)

        # 다이얼로그 표시
        dialog.exec()


    def saveChanges(self, dialog, bookname_edit, writer_edit, publisher_edit):
        # 수정된 정보를 가져옴
        bookname = bookname_edit.text().strip()
        writer = writer_edit.text().strip()
        publisher = publisher_edit.text().strip()

        # bookinformation 테이블에서 선택된 책의 정보를 업데이트
        cursor = self.conn.cursor()
        sql = "UPDATE bookinformation SET bookname=%s, writer=%s, publisher=%s WHERE isbn=%s"
        cursor.execute(sql, (bookname, writer, publisher, self.selected_book_isbn))
        self.conn.commit()

        # 다이얼로그 창 닫기
        dialog.accept()

        # 메인 화면의 테이블 업데이트
        self.loadAllBooks()

    def deleteBook(self):
        selected_cells = self.tableWidget.selectedItems()

        if len(selected_cells) == 0:
            QMessageBox.warning(self, "경고", "삭제할 책을 선택하세요.")
            return

        isbn = selected_cells[0].text()

        if QMessageBox.question(self, "삭제 확인", "선택한 책을 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            cursor = self.conn.cursor()
            sql = "DELETE FROM bookinformation WHERE isbn = %s"
            cursor.execute(sql, (isbn,))
            self.conn.commit()
            QMessageBox.information(self, "성공", "책 삭제에 성공했습니다.")
            self.loadAllBooks()

    def showAddMemberDialog(self):
        dialog = AddMemberDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            phone_number, name, home_address = dialog.getMemberInfo()

            cursor = self.conn.cursor()
            sql = "INSERT INTO member (phone_number, name, home_address) VALUES (%s, %s, %s)"
            cursor.execute(sql, (phone_number, name, home_address))
            self.conn.commit()

            # 성공적으로 등록되었음을 알리는 메시지를 표시
            QMessageBox.information(self, "회원 등록", "회원 등록이 완료되었습니다.")

            self.loadAllBooks()

        dialog.deleteLater()



    def rentBook(self):
        selected_books = self.tableWidget.selectedItems()
        if len(selected_books) == 0:
            QMessageBox.information(self, "대여 오류", "책을 선택해주세요.")
            return

        selected_book = selected_books[0]
        selected_book_isbn = selected_book.text()

        # 회원 전화번호 선택 다이얼로그
        memberDialog = QDialog(self)
        memberDialog.setWindowTitle("회원 전화번호 입력")

        phoneLabel = QLabel("전화번호", memberDialog)
        phoneEdit = QLineEdit(memberDialog)
        phoneEdit.setPlaceholderText("전화번호를 입력하세요")

        layout = QVBoxLayout()
        layout.addWidget(phoneLabel)
        layout.addWidget(phoneEdit)

        confirmButton = QPushButton("확인", memberDialog)
        confirmButton.clicked.connect(lambda: self.selectMember(phoneEdit.text(), memberDialog, selected_book_isbn))

        cancelButton = QPushButton("취소", memberDialog)
        cancelButton.clicked.connect(memberDialog.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(confirmButton)
        buttonLayout.addWidget(cancelButton)

        dialogLayout = QVBoxLayout()
        dialogLayout.addLayout(layout)
        dialogLayout.addLayout(buttonLayout)

        memberDialog.setLayout(dialogLayout)

        memberDialog.exec_()

    def selectMember(self, phone_number, dialog, selected_book_isbn):
        # 회원 정보 조회
        cursor = self.conn.cursor()
        sql = "SELECT * FROM member WHERE phone_number = %s"
        cursor.execute(sql, (phone_number,))
        result = cursor.fetchone()
        if result:
            self.selected_member_phone_number = phone_number
            dialog.accept()
            # 대여 다이얼로그 띄우기
            self.showRentDialog(selected_book_isbn)
        else:
            QMessageBox.warning(self, "회원 조회 오류", "해당 전화번호의 회원이 존재하지 않습니다.")
            dialog.reject()

    def showRentDialog(self, isbn):
        # 대여 다이얼로그 생성
        dialog = QDialog(self)
        dialog.setWindowTitle("책 대여")

        # 반납 예정일 선택 위젯
        returnDateLabel = QLabel("반납 예정일", dialog)
        returnDateEdit = QCalendarWidget(dialog)
        returnDateEdit.setMinimumDate(QDate.currentDate())
        layout = QVBoxLayout()
        layout.addWidget(returnDateLabel)
        layout.addWidget(returnDateEdit)

        # 대여 버튼, 취소 버튼
        rentButton = QPushButton("대여", dialog)
        cancelButton = QPushButton("취소", dialog)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(rentButton)
        buttonLayout.addWidget(cancelButton)

        # 전체 레이아웃
        dialogLayout = QVBoxLayout()
        dialogLayout.addLayout(layout)
        dialogLayout.addLayout(buttonLayout)
        dialog.setLayout(dialogLayout)

        # 대여 버튼과 취소 버튼에 함수 연결
        rentButton.clicked.connect(lambda: self.confirmRent(isbn, returnDateEdit.selectedDate().toString("yyyy-MM-dd"), dialog))
        cancelButton.clicked.connect(dialog.reject)

        dialog.exec_()

    def confirmRent(self, isbn, return_date, dialog):
        data = (self.selected_member_phone_number, isbn, return_date)
        cursor = self.conn.cursor()
        try:
            # 대여 정보 추가
            cursor.execute("INSERT INTO rentinformation (phone_number, isbn, return_date) VALUES (%s, %s, %s)", data)
            self.conn.commit()
            QMessageBox.information(dialog, "알림", "대여가 완료되었습니다.")
            self.updateBookStatus(isbn, "대여 중") # updateBookStatus 호출 수정
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(dialog, "에러", "대여를 완료하지 못했습니다.\n에러 메시지: " + str(e))
        finally:
            cursor.close()

        # 대여 정보 추가 후 새로고침
        self.loadAllBooks()







    def updateBookStatus(self, isbn):
        for book in self.books:
            if book.getISBN() == isbn:
                book.setStatus("대여 중")
                print(f"책 '{book.getTitle()}'의 상태가 '대여 중'으로 업데이트되었습니다.")
                break
        else:
            print(f"해당 ISBN을 가진 책이 없습니다: {isbn}")

    # 대여 버튼 연결 함수
    def rentButtonClicked(self, isbn, returnDate):
        self.confirmRent(isbn, returnDate)

    def returnBook(self):
        selected_books = self.tableWidget.selectedItems()
        if len(selected_books) == 0:
            QMessageBox.information(self, "반납 오류", "반납할 책을 선택해주세요.")
            return

        selected_book = selected_books[0]
        selected_book_isbn = selected_book.text()

        # 회원 전화번호 선택 다이얼로그
        memberDialog = QDialog(self)
        memberDialog.setWindowTitle("회원 전화번호 입력")

        phoneLabel = QLabel("전화번호", memberDialog)
        phoneEdit = QLineEdit(memberDialog)
        phoneEdit.setPlaceholderText("전화번호를 입력하세요")

        layout = QVBoxLayout()
        layout.addWidget(phoneLabel)
        layout.addWidget(phoneEdit)

        confirmButton = QPushButton("확인", memberDialog)
        confirmButton.clicked.connect(lambda: self.deleteRentInformation(phoneEdit.text(), memberDialog, selected_book_isbn))

        cancelButton = QPushButton("취소", memberDialog)
        cancelButton.clicked.connect(memberDialog.reject)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(confirmButton)
        buttonLayout.addWidget(cancelButton)

        dialogLayout = QVBoxLayout()
        dialogLayout.addLayout(layout)
        dialogLayout.addLayout(buttonLayout)

        memberDialog.setLayout(dialogLayout)

        memberDialog.exec_()

        # 메인 화면 다시 띄우기
        self.show()

    def deleteRentInformation(self, phone_number, dialog, selected_book_isbn):
        # 대여 정보 조회
        cursor = self.conn.cursor()
        sql = "SELECT * FROM rentinformation WHERE phone_number = %s AND isbn = %s"
        cursor.execute(sql, (phone_number, selected_book_isbn))
        result = cursor.fetchone()
        if result:
            # 대여 정보 삭제
            sql = "DELETE FROM rentinformation WHERE phone_number = %s AND isbn = %s"
            cursor.execute(sql, (phone_number, selected_book_isbn))
            self.conn.commit()

            # 책 상태 업데이트
            self.updateBookStatus(selected_book_isbn, "대여 가능")

            QMessageBox.information(self, "반납 완료", "책이 반납되었습니다.")
            dialog.accept()

            # 모델 업데이트
            for i in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(i, 0)
                if item.text() == selected_book_isbn:
                    status_item = self.tableWidget.item(i, 4)
                    status_item.setText("대여 가능")
                    return_date_item = self.tableWidget.item(i, 5)
                    return_date_item.setText("None")
                    break

        else:
            QMessageBox.warning(self, "대여 정보 조회 오류", "해당 전화번호와 ISBN을 가진 대여 정보가 없습니다.")

        dialog.reject()



    def updateBookStatus(self, isbn, new_status):
        with self.conn.cursor() as cursor:
            sql = "UPDATE bookinformation SET status = %s WHERE isbn = %s"
            cursor.execute(sql, (new_status, isbn))
        self.conn.commit()

        #self.conn.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())