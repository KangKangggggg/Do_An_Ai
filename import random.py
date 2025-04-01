import pygame
import sys
import random
import copy
import time
import math

# Khởi tạo pygame
pygame.init()

# Các hằng số
KICH_THUOC_O = 60
KICH_THUOC_LUOI = 8
CHIEU_RONG = KICH_THUOC_LUOI * KICH_THUOC_O + 300  # Thêm không gian cho menu
CHIEU_CAO = KICH_THUOC_LUOI * KICH_THUOC_O + 100
TRONG = None

# Màu sắc
TRANG = (255, 255, 255)
DEN = (0, 0, 0)
XAM = (200, 200, 200)
XAM_DAM = (100, 100, 100)
DO = (255, 50, 50)
XANH_LA = (50, 255, 50)
XANH_DUONG = (50, 50, 255)
CAM = (255, 165, 0)
TIM = (128, 0, 128)
VANG = (255, 255, 0)
HONG = (255, 105, 180)

# Màu sắc kẹo
MAU_KEO = [DO, CAM, VANG, XANH_LA, XANH_DUONG, TIM]

# Các loại kẹo đặc biệt
KEO_THUONG = 0
KEO_SOC_NGANG = 1
KEO_SOC_DOC = 2
KEO_GOI = 3
KEO_CAU_VONG = 4

# Thiết lập Level 1
DIEM_MUC_TIEU = 3000
SO_NUOC_DI_TOI_DA = 20

class KeoCandy:
    def __init__(self, loai, dac_biet=KEO_THUONG):
        self.loai = loai  # Màu sắc của kẹo (0-5)
        self.dac_biet = dac_biet  # Loại kẹo đặc biệt
        self.dang_xoa = False  # Đánh dấu kẹo đang bị xóa (để hiệu ứng)
        self.hieu_ung_dem = 0  # Bộ đếm cho hiệu ứng

class BangCandyCrush:
    def __init__(self):
        self.luoi = self.tao_luoi_ngau_nhien()
        self.diem = 0
        self.nuoc_di_con_lai = SO_NUOC_DI_TOI_DA
        self.keo_da_chon = None
        self.dang_hoat_dong = False  # Trạng thái hoạt động (đang xử lý kết hợp, rơi kẹo, v.v.)
        self.goi_y = None  # Lưu trữ gợi ý nước đi
        self.hoan_thanh = False  # Đánh dấu level đã hoàn thành
        self.dang_tam_dung = False  # Trạng thái tạm dừng
        self.keo_dac_biet_san_sang = None  # Lưu trữ loại kẹo đặc biệt đang sẵn sàng sử dụng
    
    def tao_luoi_ngau_nhien(self):
        """Tạo một lưới ngẫu nhiên không có kết hợp ban đầu"""
        luoi = []
        for _ in range(KICH_THUOC_LUOI):
            hang = []
            for _ in range(KICH_THUOC_LUOI):
                hang.append(KeoCandy(random.randint(0, len(MAU_KEO) - 1)))
            luoi.append(hang)
        
        # Loại bỏ các kết hợp ban đầu
        while self.tim_ket_hop(luoi):
            self.ap_dung_trong_luc(luoi)
        
        return luoi
    
    def tim_ket_hop(self, luoi):
        """Tìm tất cả các kết hợp trong lưới và đánh dấu chúng để xóa"""
        tim_thay_ket_hop = False
        ket_hop_ngang = {}  # Lưu trữ các kết hợp ngang {(hang, cot): độ dài}
        ket_hop_doc = {}    # Lưu trữ các kết hợp dọc {(hang, cot): độ dài}
        
        # Kiểm tra kết hợp ngang
        for hang in range(KICH_THUOC_LUOI):
            cot = 0
            while cot < KICH_THUOC_LUOI - 2:
                if (luoi[hang][cot] is not TRONG and 
                    luoi[hang][cot+1] is not TRONG and 
                    luoi[hang][cot+2] is not TRONG and
                    luoi[hang][cot].loai == luoi[hang][cot+1].loai == luoi[hang][cot+2].loai):
                    
                    # Tìm độ dài của kết hợp
                    do_dai = 3
                    while cot + do_dai < KICH_THUOC_LUOI and luoi[hang][cot].loai == luoi[hang][cot+do_dai].loai:
                        do_dai += 1
                    
                    # Lưu kết hợp
                    for i in range(do_dai):
                        ket_hop_ngang[(hang, cot+i)] = do_dai
                    
                    tim_thay_ket_hop = True
                    cot += do_dai
                else:
                    cot += 1
        
        # Kiểm tra kết hợp dọc
        for cot in range(KICH_THUOC_LUOI):
            hang = 0
            while hang < KICH_THUOC_LUOI - 2:
                if (luoi[hang][cot] is not TRONG and 
                    luoi[hang+1][cot] is not TRONG and 
                    luoi[hang+2][cot] is not TRONG and
                    luoi[hang][cot].loai == luoi[hang+1][cot].loai == luoi[hang+2][cot].loai):
                    
                    # Tìm độ dài của kết hợp
                    do_dai = 3
                    while hang + do_dai < KICH_THUOC_LUOI and luoi[hang][cot].loai == luoi[hang+do_dai][cot].loai:
                        do_dai += 1
                    
                    # Lưu kết hợp
                    for i in range(do_dai):
                        ket_hop_doc[(hang+i, cot)] = do_dai
                    
                    tim_thay_ket_hop = True
                    hang += do_dai
                else:
                    hang += 1
        
        # Xử lý các kết hợp và tạo kẹo đặc biệt
        if tim_thay_ket_hop:
            # Tạo kẹo đặc biệt cho kết hợp 4 hoặc 5
            for hang in range(KICH_THUOC_LUOI):
                for cot in range(KICH_THUOC_LUOI):
                    vi_tri = (hang, cot)
                    
                    # Ưu tiên kết hợp dài hơn
                    if vi_tri in ket_hop_ngang and ket_hop_ngang[vi_tri] >= 4:
                        do_dai = ket_hop_ngang[vi_tri]
                        if do_dai == 5:  # Kết hợp 5 tạo kẹo cầu vồng
                            loai_keo = luoi[hang][cot].loai
                            for i in range(5):
                                luoi[hang][cot+i].dang_xoa = True
                            # Tạo kẹo cầu vồng ở vị trí giữa
                            luoi[hang][cot+2] = KeoCandy(loai_keo, KEO_CAU_VONG)
                            luoi[hang][cot+2].dang_xoa = False
                        elif do_dai == 4:  # Kết hợp 4 tạo kẹo sọc
                            loai_keo = luoi[hang][cot].loai
                            for i in range(4):
                                luoi[hang][cot+i].dang_xoa = True
                            # Tạo kẹo sọc ngang ở vị trí đầu tiên
                            luoi[hang][cot] = KeoCandy(loai_keo, KEO_SOC_NGANG)
                            luoi[hang][cot].dang_xoa = False
                    elif vi_tri in ket_hop_doc and ket_hop_doc[vi_tri] >= 4:
                        do_dai = ket_hop_doc[vi_tri]
                        if do_dai == 5:  # Kết hợp 5 tạo kẹo cầu vồng
                            loai_keo = luoi[hang][cot].loai
                            for i in range(5):
                                luoi[hang+i][cot].dang_xoa = True
                            # Tạo kẹo cầu vồng ở vị trí giữa
                            luoi[hang+2][cot] = KeoCandy(loai_keo, KEO_CAU_VONG)
                            luoi[hang+2][cot].dang_xoa = False
                        elif do_dai == 4:  # Kết hợp 4 tạo kẹo sọc
                            loai_keo = luoi[hang][cot].loai
                            for i in range(4):
                                luoi[hang+i][cot].dang_xoa = True
                            # Tạo kẹo sọc dọc ở vị trí đầu tiên
                            luoi[hang][cot] = KeoCandy(loai_keo, KEO_SOC_DOC)
                            luoi[hang][cot].dang_xoa = False
                    # Kết hợp chữ T hoặc L (3x3) tạo kẹo gói
                    elif (vi_tri in ket_hop_ngang and vi_tri in ket_hop_doc):
                        loai_keo = luoi[hang][cot].loai
                        # Đánh dấu tất cả kẹo trong kết hợp để xóa
                        for i in range(ket_hop_ngang[vi_tri]):
                            luoi[hang][cot+i].dang_xoa = True
                        for i in range(ket_hop_doc[vi_tri]):
                            luoi[hang+i][cot].dang_xoa = True
                        # Tạo kẹo gói ở vị trí giao nhau
                        luoi[hang][cot] = KeoCandy(loai_keo, KEO_GOI)
                        luoi[hang][cot].dang_xoa = False
                    # Kết hợp thông thường 3 kẹo
                    elif vi_tri in ket_hop_ngang or vi_tri in ket_hop_doc:
                        if not luoi[hang][cot].dang_xoa:  # Chỉ đánh dấu nếu chưa bị đánh dấu
                            luoi[hang][cot].dang_xoa = True
            
            # Tính điểm và xóa các kẹo đã đánh dấu
            keo_da_xoa = 0
            for hang in range(KICH_THUOC_LUOI):
                for cot in range(KICH_THUOC_LUOI):
                    if luoi[hang][cot] is not TRONG and luoi[hang][cot].dang_xoa:
                        keo_da_xoa += 1
                        luoi[hang][cot] = TRONG
            
            return keo_da_xoa
        
        return 0
    
    def ap_dung_trong_luc(self, luoi):
        """Áp dụng trọng lực vào lưới, lấp đầy khoảng trống"""
        for cot in range(KICH_THUOC_LUOI):
            # Thu thập tất cả kẹo không trống trong cột này
            keo = []
            for hang in range(KICH_THUOC_LUOI):
                if luoi[hang][cot] is not TRONG:
                    keo.append(luoi[hang][cot])
            
            # Lấp đầy từ dưới lên với kẹo hiện có
            for hang in range(KICH_THUOC_LUOI - 1, KICH_THUOC_LUOI - len(keo) - 1, -1):
                luoi[hang][cot] = keo[KICH_THUOC_LUOI - 1 - hang]
            
            # Lấp đầy khoảng trống còn lại ở trên cùng với kẹo mới
            for hang in range(KICH_THUOC_LUOI - len(keo) - 1, -1, -1):
                luoi[hang][cot] = KeoCandy(random.randint(0, len(MAU_KEO) - 1))
    
    def thuc_hien_nuoc_di(self, hang1, cot1, hang2, cot2):
        """Thực hiện một nước đi và kiểm tra xem nó có tạo ra kết hợp không"""
        # Kiểm tra xem vị trí có hợp lệ không
        if not (0 <= hang1 < KICH_THUOC_LUOI and 0 <= cot1 < KICH_THUOC_LUOI and 
                0 <= hang2 < KICH_THUOC_LUOI and 0 <= cot2 < KICH_THUOC_LUOI):
            return False
        
        # Kiểm tra xem vị trí có liền kề không
        if not ((abs(hang1 - hang2) == 1 and cot1 == cot2) or 
                (abs(cot1 - cot2) == 1 and hang1 == hang2)):
            return False
        
        # Hoán đổi kẹo
        self.luoi[hang1][cot1], self.luoi[hang2][cot2] = self.luoi[hang2][cot2], self.luoi[hang1][cot1]
        
        # Kiểm tra các kẹo đặc biệt
        keo1 = self.luoi[hang1][cot1]
        keo2 = self.luoi[hang2][cot2]
        
        # Xử lý kẹo cầu vồng kết hợp với kẹo thường
        if keo1.dac_biet == KEO_CAU_VONG and keo2.dac_biet == KEO_THUONG:
            # Xóa tất cả kẹo cùng màu với keo2
            for h in range(KICH_THUOC_LUOI):
                for c in range(KICH_THUOC_LUOI):
                    if self.luoi[h][c] is not TRONG and self.luoi[h][c].loai == keo2.loai:
                        self.luoi[h][c] = TRONG
                        self.diem += 20
            self.luoi[hang1][cot1] = TRONG  # Xóa kẹo cầu vồng
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        elif keo2.dac_biet == KEO_CAU_VONG and keo1.dac_biet == KEO_THUONG:
            # Xóa tất cả kẹo cùng màu với keo1
            for h in range(KICH_THUOC_LUOI):
                for c in range(KICH_THUOC_LUOI):
                    if self.luoi[h][c] is not TRONG and self.luoi[h][c].loai == keo1.loai:
                        self.luoi[h][c] = TRONG
                        self.diem += 20
            self.luoi[hang2][cot2] = TRONG  # Xóa kẹo cầu vồng
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        # Xử lý kẹo sọc ngang
        elif keo1.dac_biet == KEO_SOC_NGANG:
            # Xóa toàn bộ hàng
            for c in range(KICH_THUOC_LUOI):
                if self.luoi[hang1][c] is not TRONG:
                    self.luoi[hang1][c] = TRONG
                    self.diem += 15
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        elif keo2.dac_biet == KEO_SOC_NGANG:
            # Xóa toàn bộ hàng
            for c in range(KICH_THUOC_LUOI):
                if self.luoi[hang2][c] is not TRONG:
                    self.luoi[hang2][c] = TRONG
                    self.diem += 15
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        # Xử lý kẹo sọc dọc
        elif keo1.dac_biet == KEO_SOC_DOC:
            # Xóa toàn bộ cột
            for h in range(KICH_THUOC_LUOI):
                if self.luoi[h][cot1] is not TRONG:
                    self.luoi[h][cot1] = TRONG
                    self.diem += 15
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        elif keo2.dac_biet == KEO_SOC_DOC:
            # Xóa toàn bộ cột
            for h in range(KICH_THUOC_LUOI):
                if self.luoi[h][cot2] is not TRONG:
                    self.luoi[h][cot2] = TRONG
                    self.diem += 15
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        # Xử lý kẹo gói
        elif keo1.dac_biet == KEO_GOI or keo2.dac_biet == KEO_GOI:
            # Xóa kẹo trong vùng 3x3
            hang_goi = hang1 if keo1.dac_biet == KEO_GOI else hang2
            cot_goi = cot1 if keo1.dac_biet == KEO_GOI else cot2
            
            for h in range(max(0, hang_goi-1), min(KICH_THUOC_LUOI, hang_goi+2)):
                for c in range(max(0, cot_goi-1), min(KICH_THUOC_LUOI, cot_goi+2)):
                    if self.luoi[h][c] is not TRONG:
                        self.luoi[h][c] = TRONG
                        self.diem += 15
            
            self.ap_dung_trong_luc(self.luoi)
            return True
        
        # Kiểm tra xem nước đi có tạo ra kết hợp không
        keo_da_xoa = self.tim_ket_hop(self.luoi)
        if keo_da_xoa == 0:
            # Nếu không có kết hợp, hoán đổi lại
            self.luoi[hang1][cot1], self.luoi[hang2][cot2] = self.luoi[hang2][cot2], self.luoi[hang1][cot1]
            return False
        
        # Tính điểm cho các kẹo đã xóa
        self.diem += keo_da_xoa * 10
        
        # Áp dụng trọng lực và giải quyết các kết hợp tiếp theo
        self.ap_dung_trong_luc(self.luoi)
        while True:
            keo_da_xoa = self.tim_ket_hop(self.luoi)
            if keo_da_xoa == 0:
                break
            
            # Tính điểm cho các kẹo đã xóa
            self.diem += keo_da_xoa * 10
            self.ap_dung_trong_luc(self.luoi)
        
        # Giảm số nước đi còn lại
        self.nuoc_di_con_lai -= 1
        
        # Kiểm tra xem đã hoàn thành level chưa
        if self.diem >= DIEM_MUC_TIEU:
            self.hoan_thanh = True
        
        return True
    
    def xu_ly_click(self, hang, cot):
        """Xử lý khi người dùng nhấp vào một ô"""
        if self.dang_hoat_dong or self.dang_tam_dung or self.hoan_thanh or self.nuoc_di_con_lai <= 0:
            return
        
        # Nếu đang sử dụng kẹo đặc biệt (búa)
        if self.keo_dac_biet_san_sang == "bua":
            if 0 <= hang < KICH_THUOC_LUOI and 0 <= cot < KICH_THUOC_LUOI:
                # Xóa kẹo được chọn
                self.luoi[hang][cot] = TRONG
                self.diem += 10
                self.ap_dung_trong_luc(self.luoi)
                
                # Kiểm tra các kết hợp mới
                while True:
                    keo_da_xoa = self.tim_ket_hop(self.luoi)
                    if keo_da_xoa == 0:
                        break
                    
                    self.diem += keo_da_xoa * 10
                    self.ap_dung_trong_luc(self.luoi)
                
                # Đặt lại trạng thái
                self.keo_dac_biet_san_sang = None
                self.nuoc_di_con_lai -= 1
                
                # Kiểm tra xem đã hoàn thành level chưa
                if self.diem >= DIEM_MUC_TIEU:
                    self.hoan_thanh = True
                
                return
        
        if self.keo_da_chon is None:
            # Chọn kẹo đầu tiên
            self.keo_da_chon = (hang, cot)
            # Xóa gợi ý khi người chơi đã chọn kẹo
            self.goi_y = None
        else:
            # Chọn kẹo thứ hai và thử thực hiện nước đi
            hang1, cot1 = self.keo_da_chon
            hang2, cot2 = hang, cot
            
            # Kiểm tra xem hai kẹo có liền kề không
            if ((abs(hang1 - hang2) == 1 and cot1 == cot2) or 
                (abs(cot1 - cot2) == 1 and hang1 == hang2)):
                # Thực hiện nước đi
                self.dang_hoat_dong = True
                if self.thuc_hien_nuoc_di(hang1, cot1, hang2, cot2):
                    # Nước đi hợp lệ
                    pass
                else:
                    # Nước đi không hợp lệ
                    pass
                self.dang_hoat_dong = False
            
            # Bỏ chọn kẹo
            self.keo_da_chon = None
    
    def tim_goi_y(self):
        """Tìm một nước đi gợi ý cho người chơi"""
        for hang1 in range(KICH_THUOC_LUOI):
            for cot1 in range(KICH_THUOC_LUOI):
                # Kiểm tra nước đi sang phải
                if cot1 < KICH_THUOC_LUOI - 1:
                    # Tạo bản sao của bảng
                    bang_thu = copy.deepcopy(self.luoi)
                    # Hoán đổi kẹo
                    bang_thu[hang1][cot1], bang_thu[hang1][cot1+1] = bang_thu[hang1][cot1+1], bang_thu[hang1][cot1]
                    # Kiểm tra xem có tạo ra kết hợp không
                    if self.tim_ket_hop(bang_thu) > 0:
                        return (hang1, cot1, hang1, cot1+1)
                
                # Kiểm tra nước đi xuống dưới
                if hang1 < KICH_THUOC_LUOI - 1:
                    # Tạo bản sao của bảng
                    bang_thu = copy.deepcopy(self.luoi)
                    # Hoán đổi kẹo
                    bang_thu[hang1][cot1], bang_thu[hang1+1][cot1] = bang_thu[hang1+1][cot1], bang_thu[hang1][cot1]
                    # Kiểm tra xem có tạo ra kết hợp không
                    if self.tim_ket_hop(bang_thu) > 0:
                        return (hang1, cot1, hang1+1, cot1)
        
        return None
    
    def xao_tron_bang(self):
        """Xáo trộn các kẹo trên bảng"""
        # Thu thập tất cả kẹo
        tat_ca_keo = []
        for hang in range(KICH_THUOC_LUOI):
            for cot in range(KICH_THUOC_LUOI):
                if self.luoi[hang][cot] is not TRONG:
                    tat_ca_keo.append(self.luoi[hang][cot])
        
        # Xáo trộn
        random.shuffle(tat_ca_keo)
        
        # Đặt lại vào bảng
        index = 0
        for hang in range(KICH_THUOC_LUOI):
            for cot in range(KICH_THUOC_LUOI):
                if index < len(tat_ca_keo):
                    self.luoi[hang][cot] = tat_ca_keo[index]
                    index += 1
        
        # Đảm bảo không có kết hợp ban đầu
        while self.tim_ket_hop(self.luoi) > 0:
            self.ap_dung_trong_luc(self.luoi)
        
        # Đặt lại trạng thái
        self.keo_da_chon = None
        self.goi_y = None

# Lớp Button
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.icon = icon  # Biểu tượng cho nút (emoji hoặc ký tự đặc biệt)
    
    def draw(self, screen, font):
        # Vẽ nút
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, DEN, self.rect, 2, border_radius=5)  # Viền
        
        # Vẽ văn bản
        if self.icon:
            text_surface = font.render(f"{self.icon} {self.text}", True, DEN)
        else:
            text_surface = font.render(self.text, True, DEN)
        
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

# Hàm chính
def main():
    # Thiết lập cửa sổ
    screen = pygame.display.set_mode((CHIEU_RONG, CHIEU_CAO))
    pygame.display.set_caption("Candy Crush - Level 1")
    
    # Thiết lập font
    font = pygame.font.SysFont(None, 30)
    font_small = pygame.font.SysFont(None, 24)
    font_large = pygame.font.SysFont(None, 36)
    
    # Tạo bảng
    bang = BangCandyCrush()
    
    # Tạo các nút
    nut_reset = Button(KICH_THUOC_LUOI * KICH_THUOC_O + 50, 150, 200, 40, "Chơi lại", XANH_LA, (100, 255, 100), "↺")
    nut_goi_y = Button(KICH_THUOC_LUOI * KICH_THUOC_O + 50, 200, 200, 40, "Gợi ý", XANH_DUONG, (100, 100, 255), "⚡")
    nut_xao_tron = Button(KICH_THUOC_LUOI * KICH_THUOC_O + 50, 250, 200, 40, "Xáo trộn", CAM, (255, 200, 100), "🔄")
    nut_bua = Button(KICH_THUOC_LUOI * KICH_THUOC_O + 50, 300, 200, 40, "Búa phá kẹo", DO, (255, 100, 100), "💥")
    nut_tam_dung = Button(KICH_THUOC_LUOI * KICH_THUOC_O + 50, 350, 200, 40, "Tạm dừng", XAM, (150, 150, 150), "⏸")
    nut_tiep_tuc = Button(CHIEU_RONG // 2 - 100, CHIEU_CAO // 2 + 50, 200, 40, "Tiếp tục", XANH_LA, (100, 255, 100))
    nut_level_tiep = Button(CHIEU_RONG // 2 - 100, CHIEU_CAO // 2 + 50, 200, 40, "Level tiếp theo", VANG, (255, 255, 100), "⏭")
    
    # Biến trạng thái
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Xử lý nhấp chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Kiểm tra nhấp vào bảng (chỉ khi không tạm dừng)
                if not bang.dang_tam_dung and pos[0] < KICH_THUOC_LUOI * KICH_THUOC_O and pos[1] < KICH_THUOC_LUOI * KICH_THUOC_O:
                    hang = pos[1] // KICH_THUOC_O
                    cot = pos[0] // KICH_THUOC_O
                    bang.xu_ly_click(hang, cot)
                
                # Kiểm tra nhấp vào nút
                if nut_reset.is_clicked(pos, True):
                    bang = BangCandyCrush()
                
                if not bang.dang_tam_dung and not bang.hoan_thanh and bang.nuoc_di_con_lai > 0:
                    if nut_goi_y.is_clicked(pos, True):
                        # Tìm gợi ý
                        bang.goi_y = bang.tim_goi_y()
                    
                    if nut_xao_tron.is_clicked(pos, True):
                        # Xáo trộn bảng
                        bang.xao_tron_bang()
                    
                    if nut_bua.is_clicked(pos, True):
                        # Kích hoạt búa phá kẹo
                        bang.keo_dac_biet_san_sang = "bua"
                
                if nut_tam_dung.is_clicked(pos, True):
                    # Tạm dừng/tiếp tục trò chơi
                    bang.dang_tam_dung = not bang.dang_tam_dung
                
                if bang.dang_tam_dung and nut_tiep_tuc.is_clicked(pos, True):
                    # Tiếp tục trò chơi
                    bang.dang_tam_dung = False
                
                if bang.hoan_thanh and nut_level_tiep.is_clicked(pos, True):
                    # Chuyển sang level tiếp theo (trong trường hợp này, tạo level mới)
                    bang = BangCandyCrush()
        
        # Cập nhật trạng thái nút khi di chuột
        mouse_pos = pygame.mouse.get_pos()
        nut_reset.check_hover(mouse_pos)
        nut_goi_y.check_hover(mouse_pos)
        nut_xao_tron.check_hover(mouse_pos)
        nut_bua.check_hover(mouse_pos)
        nut_tam_dung.check_hover(mouse_pos)
        nut_tiep_tuc.check_hover(mouse_pos)
        nut_level_tiep.check_hover(mouse_pos)
        
        # Vẽ màn hình
        screen.fill(XAM)
        
        # Vẽ bảng
        for hang in range(KICH_THUOC_LUOI):
            for cot in range(KICH_THUOC_LUOI):
                # Vẽ ô
                x = cot * KICH_THUOC_O
                y = hang * KICH_THUOC_O
                pygame.draw.rect(screen, TRANG, (x, y, KICH_THUOC_O, KICH_THUOC_O))
                pygame.draw.rect(screen, DEN, (x, y, KICH_THUOC_O, KICH_THUOC_O), 1)
                
                # Vẽ kẹo
                if bang.luoi[hang][cot] is not TRONG:
                    keo = bang.luoi[hang][cot]
                    mau = MAU_KEO[keo.loai]
                    
                    # Vẽ kẹo thường
                    if keo.dac_biet == KEO_THUONG:
                        pygame.draw.circle(screen, mau, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 2 - 5)
                        pygame.draw.circle(screen, TRANG, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 4 - 5)
                    
                    # Vẽ kẹo sọc ngang
                    elif keo.dac_biet == KEO_SOC_NGANG:
                        pygame.draw.circle(screen, mau, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 2 - 5)
                        for i in range(3):
                            pygame.draw.line(screen, TRANG, 
                                            (x + 10, y + KICH_THUOC_O // 2 - 10 + i * 10), 
                                            (x + KICH_THUOC_O - 10, y + KICH_THUOC_O // 2 - 10 + i * 10), 
                                            3)
                    
                    # Vẽ kẹo sọc dọc
                    elif keo.dac_biet == KEO_SOC_DOC:
                        pygame.draw.circle(screen, mau, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 2 - 5)
                        for i in range(3):
                            pygame.draw.line(screen, TRANG, 
                                            (x + KICH_THUOC_O // 2 - 10 + i * 10, y + 10), 
                                            (x + KICH_THUOC_O // 2 - 10 + i * 10, y + KICH_THUOC_O - 10), 
                                            3)
                    
                    # Vẽ kẹo gói
                    elif keo.dac_biet == KEO_GOI:
                        pygame.draw.circle(screen, mau, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 2 - 5)
                        pygame.draw.rect(screen, TRANG, (x + KICH_THUOC_O // 4, y + KICH_THUOC_O // 4, 
                                                        KICH_THUOC_O // 2, KICH_THUOC_O // 2))
                    
                    # Vẽ kẹo cầu vồng
                    elif keo.dac_biet == KEO_CAU_VONG:
                        for i in range(6):
                            angle = i * math.pi / 3
                            color = MAU_KEO[i]
                            pygame.draw.polygon(screen, color, [
                                (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2),
                                (x + KICH_THUOC_O // 2 + int((KICH_THUOC_O // 2 - 5) * math.cos(angle)), 
                                 y + KICH_THUOC_O // 2 + int((KICH_THUOC_O // 2 - 5) * math.sin(angle))),
                                (x + KICH_THUOC_O // 2 + int((KICH_THUOC_O // 2 - 5) * math.cos(angle + math.pi / 3)), 
                                 y + KICH_THUOC_O // 2 + int((KICH_THUOC_O // 2 - 5) * math.sin(angle + math.pi / 3)))
                            ])
                        pygame.draw.circle(screen, TRANG, (x + KICH_THUOC_O // 2, y + KICH_THUOC_O // 2), KICH_THUOC_O // 6)
                
                # Đánh dấu kẹo đã chọn
                if bang.keo_da_chon is not None and bang.keo_da_chon == (hang, cot):
                    pygame.draw.rect(screen, VANG, (x, y, KICH_THUOC_O, KICH_THUOC_O), 3)
                
                # Đánh dấu gợi ý
                if bang.goi_y is not None:
                    hang1, cot1, hang2, cot2 = bang.goi_y
                    if (hang == hang1 and cot == cot1) or (hang == hang2 and cot == cot2):
                        pygame.draw.rect(screen, XANH_DUONG, (x, y, KICH_THUOC_O, KICH_THUOC_O), 3)
        
        # Vẽ thông tin bên phải
        # Tiêu đề
        tieu_de = font_large.render("CANDY CRUSH", True, HONG)
        screen.blit(tieu_de, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 20))
        
        level_text = font.render("Level 1", True, VANG)
        screen.blit(level_text, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 60))
        
        # Mục tiêu
        muc_tieu_text = font.render(f"Mục tiêu: {DIEM_MUC_TIEU} điểm", True, DEN)
        screen.blit(muc_tieu_text, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 90))
        
        # Điểm số
        diem_text = font.render(f"Điểm: {bang.diem}", True, DEN)
        screen.blit(diem_text, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 120))
        
        # Số nước đi còn lại
        nuoc_di_text = font.render(f"Nước đi còn lại: {bang.nuoc_di_con_lai}", True, DEN)
        screen.blit(nuoc_di_text, (KICH_THUOC_LUOI * KICH_THUOC_O + 170, 120))
        
        # Vẽ thanh tiến trình
        pygame.draw.rect(screen, XAM_DAM, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 400, 200, 20))
        tien_trinh = min(bang.diem / DIEM_MUC_TIEU, 1.0)
        pygame.draw.rect(screen, XANH_LA, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 400, int(200 * tien_trinh), 20))
        pygame.draw.rect(screen, DEN, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 400, 200, 20), 1)
        
        # Vẽ các nút
        nut_reset.draw(screen, font_small)
        
        if not bang.dang_tam_dung and not bang.hoan_thanh and bang.nuoc_di_con_lai > 0:
            nut_goi_y.draw(screen, font_small)
            nut_xao_tron.draw(screen, font_small)
            nut_bua.draw(screen, font_small)
        
        # Đổi tên nút tạm dừng nếu đang tạm dừng
        if bang.dang_tam_dung:
            nut_tam_dung.text = "Tiếp tục"
            nut_tam_dung.icon = "▶️"
        else:
            nut_tam_dung.text = "Tạm dừng"
            nut_tam_dung.icon = "⏸"
        
        nut_tam_dung.draw(screen, font_small)
        
        # Vẽ hướng dẫn
        huong_dan1 = font_small.render("Nhấp vào hai kẹo liền kề", True, DEN)
        huong_dan2 = font_small.render("để hoán đổi chúng", True, DEN)
        screen.blit(huong_dan1, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 430))
        screen.blit(huong_dan2, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 455))
        
        # Hiển thị trạng thái kẹo đặc biệt
        if bang.keo_dac_biet_san_sang == "bua":
            trang_thai = font_small.render("Chọn kẹo để phá", True, DO)
            screen.blit(trang_thai, (KICH_THUOC_LUOI * KICH_THUOC_O + 50, 480))
        
        # Vẽ màn hình tạm dừng
        if bang.dang_tam_dung:
            # Vẽ lớp mờ
            s = pygame.Surface((CHIEU_RONG, CHIEU_CAO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
            screen.blit(s, (0, 0))
            
            # Vẽ thông báo
            tam_dung_text = font_large.render("TẠM DỪNG", True, TRANG)
            text_rect = tam_dung_text.get_rect(center=(CHIEU_RONG // 2, CHIEU_CAO // 2 - 20))
            screen.blit(tam_dung_text, text_rect)
            
            # Vẽ nút tiếp tục
            nut_tiep_tuc.draw(screen, font)
        
        # Vẽ màn hình hoàn thành
        if bang.hoan_thanh:
            # Vẽ lớp mờ
            s = pygame.Surface((CHIEU_RONG, CHIEU_CAO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
            screen.blit(s, (0, 0))
            
            # Vẽ thông báo
            hoan_thanh_text = font_large.render("HOÀN THÀNH!", True, VANG)
            text_rect = hoan_thanh_text.get_rect(center=(CHIEU_RONG // 2, CHIEU_CAO // 2 - 50))
            screen.blit(hoan_thanh_text, text_rect)
            
            diem_text = font.render(f"Điểm: {bang.diem}", True, TRANG)
            text_rect = diem_text.get_rect(center=(CHIEU_RONG // 2, CHIEU_CAO // 2))
            screen.blit(diem_text, text_rect)
            
            # Vẽ nút level tiếp theo
            nut_level_tiep.draw(screen, font)
        
        # Vẽ màn hình thua cuộc
        if bang.nuoc_di_con_lai <= 0 and not bang.hoan_thanh:
            # Vẽ lớp mờ
            s = pygame.Surface((CHIEU_RONG, CHIEU_CAO), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Màu đen với độ trong suốt
            screen.blit(s, (0, 0))
            
            # Vẽ thông báo
            thua_text = font_large.render("HẾT LƯỢT!", True, DO)
            text_rect = thua_text.get_rect(center=(CHIEU_RONG // 2, CHIEU_CAO // 2 - 50))
            screen.blit(thua_text, text_rect)
            
            diem_text = font.render(f"Điểm: {bang.diem}", True, TRANG)
            text_rect = diem_text.get_rect(center=(CHIEU_RONG // 2, CHIEU_CAO // 2))
            screen.blit(diem_text, text_rect)
            
            # Vẽ nút chơi lại
            nut_reset_thua = Button(CHIEU_RONG // 2 - 100, CHIEU_CAO // 2 + 50, 200, 40, "Chơi lại", XANH_LA, (100, 255, 100), "↺")
            nut_reset_thua.check_hover(mouse_pos)
            nut_reset_thua.draw(screen, font)
            
            # Xử lý nhấp chuột cho nút chơi lại
            if event.type == pygame.MOUSEBUTTONDOWN and nut_reset_thua.is_clicked(mouse_pos, True):
                bang = BangCandyCrush()
        
        # Cập nhật màn hình
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()