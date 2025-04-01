from giaodien import GiaoDien
from De import De

class UngDung:
    def __init__(self):
        self.giao_dien = GiaoDien()
        self.de = De()

    def chay(self):
        self.giao_dien.run()
        self.de.run()

ung_dung = UngDung()
ung_dung.chay()