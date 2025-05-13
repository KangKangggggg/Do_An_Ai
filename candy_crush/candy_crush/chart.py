import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY

class Chart:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.chart_width = SCREEN_WIDTH - 100
        self.chart_height = SCREEN_HEIGHT - 100
        self.chart_x = 100
        self.chart_y = 100
        self.bar_width = 20  # Chiều rộng cột nhỏ hơn để chứa nhiều thuật toán
        self.close_button_rect = None

    def draw_comparison_chart(self, comparison_data):
        """Vẽ biểu đồ so sánh cho tất cả thuật toán đã chọn với giao diện đẹp hơn"""
        if not comparison_data:
            return

        # Tạo lớp phủ bán trong suốt
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Tạo panel đẹp hơn cho biểu đồ
        panel_width = SCREEN_WIDTH - 200
        panel_height = SCREEN_HEIGHT - 200
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Vẽ panel với nền gradient
        chart_surface = pygame.Surface((panel_width, panel_height))
        for y in range(panel_height):
            # Tạo gradient từ xám đậm đến xám nhạt
            color = (80 + (y * 60 // panel_height), 80 + (y * 60 // panel_height), 90 + (y * 60 // panel_height))
            pygame.draw.line(chart_surface, color, (0, y), (panel_width, y))
        
        # Thêm viền và hiệu ứng góc bo tròn
        pygame.draw.rect(chart_surface, (200, 200, 200), (0, 0, panel_width, panel_height), 3, border_radius=15)
        
        # Vẽ tiêu đề với kiểu dáng đẹp hơn
        title_font = pygame.font.SysFont(None, 42)
        title = title_font.render("So sánh thuật toán", True, (255, 255, 255))
        title_rect = title.get_rect(center=(panel_width // 2, 40))
        chart_surface.blit(title, title_rect)
        
        # Vẽ phụ đề với kiểu dáng đẹp hơn
        subtitle_font = pygame.font.SysFont(None, 24)
        time_subtitle = subtitle_font.render("Xanh la: Thoi gian thuc (giay)", True, (200, 255, 200))
        cost_subtitle = subtitle_font.render("Do: Tong chi phi ( khoang cach)", True, (255, 200, 200))
        chart_surface.blit(time_subtitle, (50, 80))
        chart_surface.blit(cost_subtitle, (50, 110))

        algorithms = comparison_data["algorithms"]
        total_time_data = comparison_data["total_time_data"]
        total_cost_data = comparison_data["total_cost_data"]

        if not algorithms or len(algorithms) != len(total_time_data) or len(algorithms) != len(total_cost_data):
            print("Dữ liệu không hợp lệ để vẽ biểu đồ")
            return

        num_algorithms = len(algorithms)
        
        # Tính toán kích thước biểu đồ
        chart_area_height = panel_height - 200  # Leave space for title and labels
        chart_area_width = panel_width - 150    # Leave space for labels
        chart_area_x = 100                      # Left margin
        chart_area_y = 150                      # Top margin
        
        # Tính toán chiều rộng và khoảng cách của cột
        bar_width = 40
        group_width = (bar_width * 2) + 10      # Width for time and cost bars with spacing
        group_spacing = (chart_area_width - (group_width * num_algorithms)) // (num_algorithms + 1)
        
        # Tìm giá trị tối đa để tỷ lệ
        max_value = max(
            max(time_val for _, time_val, _ in total_time_data) if total_time_data else 0,
            max(cost_val for _, cost_val, _ in total_cost_data) if total_cost_data else 0
        )
        max_value = max(max_value, 1)
        
        # Vẽ đường lưới ngang
        for i in range(6):
            y_pos = chart_area_y + chart_area_height - (i * chart_area_height // 5)
            value = max_value * i / 5
            
            # Vẽ đường lưới
            pygame.draw.line(chart_surface, (150, 150, 150), 
                            (chart_area_x - 10, y_pos), 
                            (chart_area_x + chart_area_width, y_pos), 1)
            
            # Vẽ nhãn giá trị
            value_text = subtitle_font.render(f"{value:.1f}", True, (200, 200, 200))
            value_rect = value_text.get_rect(midright=(chart_area_x - 15, y_pos))
            chart_surface.blit(value_text, value_rect)

        # Vẽ cột cho mỗi thuật toán
        for i, (algo_name, time_value, time_color) in enumerate(total_time_data):
            _, cost_value, cost_color = total_cost_data[i]
            
            # Tính toán vị trí cột
            group_x = chart_area_x + group_spacing + (i * (group_width + group_spacing))
            time_x = group_x
            cost_x = group_x + bar_width + 10
            
            # Tính toán chiều cao cột (đã tỷ lệ)
            time_height = (time_value / max_value) * chart_area_height
            cost_height = (cost_value / max_value) * chart_area_height
            
            # Vẽ cột thời gian với gradient và hiệu ứng 3D
            time_rect = pygame.Rect(time_x, chart_area_y + chart_area_height - time_height, 
                                   bar_width, time_height)
            
            # Tạo gradient cho cột thời gian (xanh lá)
            for y in range(int(time_height)):
                # Gradient từ xanh đậm đến xanh nhạt
                green_val = min(255, 100 + (y * 155 // int(time_height)))
                color = (0, green_val, 0)
                pygame.draw.line(chart_surface, color, 
                                (time_x, chart_area_y + chart_area_height - y), 
                                (time_x + bar_width - 5, chart_area_y + chart_area_height - y))
            
            # Thêm hiệu ứng 3D
            pygame.draw.rect(chart_surface, (0, 200, 0), time_rect, 1)
            pygame.draw.line(chart_surface, (0, 255, 0), 
                            (time_x + bar_width - 5, chart_area_y + chart_area_height - time_height),
                            (time_x + bar_width, chart_area_y + chart_area_height - time_height + 5), 5)
            pygame.draw.line(chart_surface, (0, 255, 0), 
                            (time_x + bar_width, chart_area_y + chart_area_height - time_height + 5),
                            (time_x + bar_width, chart_area_y + chart_area_height), 5)
            
            # Vẽ cột chi phí với gradient và hiệu ứng 3D
            cost_rect = pygame.Rect(cost_x, chart_area_y + chart_area_height - cost_height, 
                                   bar_width, cost_height)
            
            # Tạo gradient cho cột chi phí (đỏ)
            for y in range(int(cost_height)):
                # Gradient từ đỏ đậm đến đỏ nhạt
                red_val = min(255, 100 + (y * 155 // int(cost_height)))
                color = (red_val, 0, 0)
                pygame.draw.line(chart_surface, color, 
                                (cost_x, chart_area_y + chart_area_height - y), 
                                (cost_x + bar_width - 5, chart_area_y + chart_area_height - y))
            
            # Thêm hiệu ứng 3D
            pygame.draw.rect(chart_surface, (200, 0, 0), cost_rect, 1)
            pygame.draw.line(chart_surface, (255, 0, 0), 
                            (cost_x + bar_width - 5, chart_area_y + chart_area_height - cost_height),
                            (cost_x + bar_width, chart_area_y + chart_area_height - cost_height + 5), 5)
            pygame.draw.line(chart_surface, (255, 0, 0), 
                            (cost_x + bar_width, chart_area_y + chart_area_height - cost_height + 5),
                            (cost_x + bar_width, chart_area_y + chart_area_height), 5)
            
            # Hiển thị giá trị trên cột
            if time_height > 20:  # Chỉ hiển thị nếu cột đủ cao
                time_value_text = subtitle_font.render(f"{time_value:.2f}s", True, (255, 255, 255))
                time_value_rect = time_value_text.get_rect(midbottom=(time_x + bar_width // 2, 
                                                                    chart_area_y + chart_area_height - time_height - 5))
                chart_surface.blit(time_value_text, time_value_rect)
            
            if cost_height > 20:  # Chỉ hiển thị nếu cột đủ cao
                cost_value_text = subtitle_font.render(f"{cost_value:.2f}", True, (255, 255, 255))
                cost_value_rect = cost_value_text.get_rect(midbottom=(cost_x + bar_width // 2, 
                                                                    chart_area_y + chart_area_height - cost_height - 5))
                chart_surface.blit(cost_value_text, cost_value_rect)
            
            # Vẽ tên thuật toán
            algo_text = subtitle_font.render(algo_name, True, (255, 255, 255))
            algo_rect = algo_text.get_rect(center=(group_x + group_width // 2, chart_area_y + chart_area_height + 25))
            chart_surface.blit(algo_text, algo_rect)

        # Vẽ nút đóng với kiểu dáng đẹp hơn
        close_button_size = 40
        close_button_x = panel_width - close_button_size - 10
        close_button_y = 10
        
        # Vẽ nền nút với gradient
        for i in range(close_button_size):
            # Gradient từ đỏ đậm đến đỏ nhạt
            red_val = min(255, 150 + (i * 105 // close_button_size))
            pygame.draw.line(chart_surface, (red_val, 0, 0), 
                            (close_button_x, close_button_y + i), 
                            (close_button_x + close_button_size, close_button_y + i))
        
        # Vẽ viền nút và dấu X
        pygame.draw.rect(chart_surface, (255, 255, 255), 
                        (close_button_x, close_button_y, close_button_size, close_button_size), 
                        2, border_radius=10)
        
        # Vẽ dấu X
        x_font = pygame.font.SysFont(None, 36)
        x_text = x_font.render("X", True, (255, 255, 255))
        x_rect = x_text.get_rect(center=(close_button_x + close_button_size // 2, 
                                        close_button_y + close_button_size // 2))
        chart_surface.blit(x_text, x_rect)
        
        # Lưu trữ rect của nút đóng để phát hiện click
        self.close_button_rect = pygame.Rect(panel_x + close_button_x, panel_y + close_button_y, 
                                            close_button_size, close_button_size)
        
        # Thêm hiệu ứng bóng đổ nhẹ cho toàn bộ panel
        shadow_surface = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 100))
        self.screen.blit(shadow_surface, (panel_x - 5, panel_y - 5))
        
        # Vẽ bề mặt biểu đồ lên màn hình
        self.screen.blit(chart_surface, (panel_x, panel_y))
        
        # Thêm hiệu ứng hoạt ảnh nhẹ (đường viền nhấp nháy)
        highlight = pygame.Surface((panel_width, 5), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 100))
        self.screen.blit(highlight, (panel_x, panel_y + 5))
