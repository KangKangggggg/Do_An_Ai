# Do_An_Ai
Giới Thiệu
Candy Crush là một trò chơi match-3 được phát triển bằng Python và Pygame, nơi người chơi hoán đổi các viên kẹo để tạo chuỗi 3+ viên cùng loại, ghi điểm và hoàn thành mục tiêu của từng cấp độ. Dự án bao gồm giao diện người dùng (UI) thân thiện, các cấp độ đa dạng, và thuật toán AI hỗ trợ gợi ý nước đi tối ưu.

Tính Năng Chính
Giao diện người dùng:
4 màn hình chính: Menu, Chọn cấp độ, Chơi game, Cài đặt.
Hỗ trợ tương tác chuột (hoán đổi kẹo, gợi ý), hiệu ứng âm thanh/hình ảnh (swap, match, level complete).
Cấp độ chơi:
Level 1: Đạt 800 điểm (20 lượt).
Level 2: Phá 8 kẹo dẻo (30 lượt).
Level 3: Đạt 1200 điểm (15 lượt).
Tùy chỉnh cài đặt: Âm lượng, nhạc nền, rung, chế độ AI (A*, Hill Climbing, Hybrid), chế độ chơi (Auto Play, Free Movement).
Thuật Toán AI
AI hỗ trợ tìm nước đi tối ưu thông qua các thuật toán sau:

A*: Tìm kiếm có hướng, tối ưu nước đi dựa trên heuristic (điểm số, mục tiêu cấp độ).
BFS: Khám phá nước đi ngắn nhất trong phạm vi độ sâu giới hạn.
Backtracking: Thử nghiệm sâu để tìm chuỗi nước đi tối ưu.
Simulated Annealing: Thoát cực trị cục bộ, khám phá nước đi đa dạng.
Q-learning: Học hỏi từ trải nghiệm, cải thiện nước đi qua thời gian.
AND-OR: Xử lý nhiều mục tiêu (phá kẹo dẻo, thu thập nguyên liệu).
Hybrid: Kết hợp A* và Simulated Annealing để cân bằng hiệu suất và khám phá, trả về nước đi tối ưu.

Cách Chơi
Hoán đổi kẹo để tạo chuỗi 3+ viên cùng loại, ghi 10 điểm/viên.
Hoàn thành mục tiêu cấp độ trước khi hết lượt (điểm số, phá kẹo dẻo, thu thập nguyên liệu, phá sô-cô-la).
Sử dụng nút "Gợi ý" để nhận nước đi tối ưu từ AI (Hybrid).

Tài liệu tham khảo:
1.	Pygame Documentation. Truy cập tại: https://www.pygame.org/docs/. Tài liệu chính thức của Pygame, cung cấp hướng dẫn chi tiết về cách sử dụng thư viện để phát triển giao diện, xử lý sự kiện, và tích hợp âm thanh/hình ảnh trong trò chơi Candy Crush. 
2.	Candy Crush Saga Official Website. Truy cập tại: https://www.candycrushsaga.com/. Nguồn tham khảo chính về lối chơi, thiết kế cấp độ, và các yếu tố tạo nên sức hút của trò chơi match-3 gốc, giúp nhóm tái hiện các tính năng cốt lõi trong dự án. 
3.	Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press. Sách tham khảo về các thuật toán tìm kiếm và tối ưu, bao gồm A* và Hill Climbing, được sử dụng để triển khai AI trong trò chơi. 

Hướng Dẫn Cài Đặt
Cài Python 3.x và Pygame: pip install pygame.
Clone repository: git clone <repo-url>.
Chạy trò chơi: python main.py.

Tác giả: 
		
STT	HỌ VÀ TÊN            	MSSV
1	  Huỳnh Tấn Vinh       	23110365
2 	Nguyễn Phạm Bảo Trân	23110348
3	  Nguyễn Thị Kim Oanh  	23110372


