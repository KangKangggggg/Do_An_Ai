import sys
import pygame
import importlib.util
import os

def load_module(file_path, module_name):
    """Tải một module Python từ đường dẫn file"""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            print(f"Không thể tải module từ {file_path}")
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Lỗi khi tải module {module_name}: {e}")
        return None

class GameSelector:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Candy Crush Game Selector")
        
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.background_color = (204, 153, 255)  # Màu tím nhạt
        self.button_color = (50, 205, 50)        # Màu xanh lá
        self.button_hover_color = (30, 180, 30)  # Màu xanh lá đậm hơn
        self.text_color = (255, 255, 255)        # Màu trắng
        
        self.buttons = [
            {
                "rect": pygame.Rect(self.width//2 - 150, 250, 300, 80),
                "text": "Phiên bản Cơ bản",
                "action": "basic",
                "hover": False
            },
            {
                "rect": pygame.Rect(self.width//2 - 150, 350, 300, 80),
                "text": "Phiên bản Nâng cao",
                "action": "advanced",
                "hover": False
            },
            {
                "rect": pygame.Rect(self.width//2 - 150, 450, 300, 80),
                "text": "Thoát",
                "action": "exit",
                "hover": False
            }
        ]
        
        # Tìm đường dẫn đến các file game
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.basic_game_path = os.path.join(self.current_dir, r"C:\Users\ACER\Desktop\TTNT\Do_An_AI\gui\mucde.py")
        self.advanced_game_path = os.path.join(self.current_dir, r"C:\Users\ACER\Desktop\TTNT\Do_An_AI\gui\mucde.py")
        
        # Kiểm tra xem các file có tồn tại không
        if not os.path.exists(self.basic_game_path):
            print(f"Không tìm thấy file {self.basic_game_path}")
            print("Đang sử dụng đường dẫn mặc định...")
            self.basic_game_path = r"C:\Users\ACER\Desktop\TTNT\Do_An_AI\gui\mucde.py"
            
        if not os.path.exists(self.advanced_game_path):
            print(f"Không tìm thấy file {self.advanced_game_path}")
            print("Đang sử dụng đường dẫn mặc định...")
            self.advanced_game_path = r"C:\Users\ACER\Desktop\TTNT\Do_An_AI\gui\mucde.py"
    
    def draw(self):
        """Vẽ màn hình chọn game"""
        self.screen.fill(self.background_color)
        
        # Vẽ tiêu đề
        title = self.font_large.render("Candy Crush", True, self.text_color)
        title_rect = title.get_rect(center=(self.width//2, 100))
        self.screen.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Chọn phiên bản để chơi", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, 170))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Vẽ các nút
        for button in self.buttons:
            color = self.button_hover_color if button["hover"] else self.button_color
            pygame.draw.rect(self.screen, color, button["rect"], border_radius=15)
            pygame.draw.rect(self.screen, self.text_color, button["rect"], 2, border_radius=15)
            
            text = self.font_small.render(button["text"], True, self.text_color)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        """Xử lý các sự kiện"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            
            if event.type == pygame.MOUSEMOTION:
                # Cập nhật trạng thái hover của các nút
                for button in self.buttons:
                    button["hover"] = button["rect"].collidepoint(event.pos)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Kiểm tra xem người dùng đã nhấp vào nút nào
                for button in self.buttons:
                    if button["rect"].collidepoint(event.pos):
                        return button["action"]
        
        return None
    
    def run(self):
        """Chạy màn hình chọn game"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            action = self.handle_events()
            
            if action == "exit":
                running = False
            elif action == "basic":
                self.run_basic_game()
            elif action == "advanced":
                self.run_advanced_game()
            
            self.draw()
            clock.tick(60)
        
        pygame.quit()
    
    def run_basic_game(self):
        """Chạy phiên bản cơ bản của game"""
        print("Đang chạy phiên bản cơ bản...")
        
        # Tải module game cơ bản
        basic_game = load_module(self.basic_game_path, "candy_crush_basic")
        if basic_game:
            pygame.quit()  # Đóng màn hình hiện tại
            
            # Lưu lại các module đã import để tránh xung đột
            saved_modules = dict(sys.modules)
            
            try:
                # Chạy hàm main của game cơ bản
                if hasattr(basic_game, 'main'):
                    basic_game.main()
                else:
                    print("Không tìm thấy hàm main trong module game cơ bản")
            except Exception as e:
                print(f"Lỗi khi chạy game cơ bản: {e}")
            
            # Khôi phục lại các module đã import
            sys.modules = saved_modules
            
            # Khởi tạo lại pygame cho màn hình chọn game
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Candy Crush Game Selector")
    
    def run_advanced_game(self):
        """Chạy phiên bản nâng cao của game"""
        print("Đang chạy phiên bản nâng cao...")
        
        # Tải module game nâng cao
        advanced_game = load_module(self.advanced_game_path, "candy_crush_advanced")
        if advanced_game:
            pygame.quit()  # Đóng màn hình hiện tại
            
            # Lưu lại các module đã import để tránh xung đột
            saved_modules = dict(sys.modules)
            
            try:
                # Chạy hàm main của game nâng cao
                if hasattr(advanced_game, 'main'):
                    advanced_game.main()
                else:
                    print("Không tìm thấy hàm main trong module game nâng cao")
            except Exception as e:
                print(f"Lỗi khi chạy game nâng cao: {e}")
            
            # Khôi phục lại các module đã import
            sys.modules = saved_modules
            
            # Khởi tạo lại pygame cho màn hình chọn game
            pygame.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Candy Crush Game Selector")

def main():
    """Hàm main chính để chạy chương trình"""
    # Đổi tên file để phù hợp với tên module
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Tạo bản sao của các file với tên mới
    try:
        # Đường dẫn đến file gốc
        file1_path = os.path.join(current_dir, "plP4U.py")
        file2_path = os.path.join(current_dir, "f1VOW.py")
        
        # Đường dẫn đến file đích
        basic_game_path = os.path.join(current_dir, "candy_crush_basic.py")
        advanced_game_path = os.path.join(current_dir, "candy_crush_advanced.py")
        
        # Kiểm tra xem các file gốc có tồn tại không
        if os.path.exists(file1_path):
            # Đọc nội dung file
            with open(file1_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ghi nội dung vào file mới
            with open(basic_game_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Đã tạo bản sao {basic_game_path}")
        
        if os.path.exists(file2_path):
            # Đọc nội dung file
            with open(file2_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ghi nội dung vào file mới
            with open(advanced_game_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Đã tạo bản sao {advanced_game_path}")
    except Exception as e:
        print(f"Lỗi khi tạo bản sao file: {e}")
    
    # Chạy màn hình chọn game
    selector = GameSelector()
    selector.run()

if __name__ == "__main__":
    main()