# Do_An_Ai
# Candy Crush 

# Nhóm thực hiện: 
		
Huỳnh Tấn Vinh-23110365

Nguyễn Phạm Bảo Trân-23110348

Nguyễn Thị Kim Oanh-23110372
## Mục Tiêu

Dự án Candy Crush này được xây dựng nhằm minh họa và so sánh hiệu quả của các thuật toán trí tuệ nhân tạo (AI) trong việc tìm kiếm nước đi tối ưu. Thay vì đua cá trong mê cung, người chơi và các thuật toán AI sẽ cùng tham gia vào thế giới đầy màu sắc của Candy Crush, nơi mục tiêu là đạt điểm cao, hoàn thành nhiệm vụ và vượt qua các cấp độ bằng cách thực hiện những nước đi thông minh nhất. Trò chơi không chỉ mang tính giải trí mà còn giúp người dùng trực quan hóa cách các thuật toán khác nhau phân tích và đưa ra quyết định trong một môi trường game năng động.


## Mô Tả Trò Chơi

Candy Crush là một trò chơi giải đố nổi tiếng, nơi người chơi phải hoán đổi vị trí các viên kẹo liền kề để tạo thành các hàng hoặc cột gồm ba hoặc nhiều hơn các viên kẹo cùng loại. Khi một nhóm kẹo được tạo thành, chúng sẽ biến mất, tạo ra khoảng trống để các viên kẹo phía trên rơi xuống và những viên kẹo mới xuất hiện. Mục tiêu chính là đạt điểm số nhất định, phá hủy các vật cản hoặc hoàn thành các nhiệm vụ đặc biệt trong một số lượng nước đi giới hạn.


Trong dự án này, các thuật toán AI sẽ đóng vai trò là "người chơi máy", phân tích trạng thái bảng kẹo để tìm ra nước đi mang lại lợi ích cao nhất (điểm số, tạo kẹo đặc biệt, hoàn thành mục tiêu cấp độ). Điều này giúp người dùng quan sát trực tiếp hiệu suất, tốc độ và chiến lược của từng thuật toán.


## Chế Độ Chơi

Trò chơi cung cấp hai chế độ chơi chính để trải nghiệm và đánh giá các thuật toán AI:


**Chế độ Người chơi (Human Play Mode):**

Mô tả: Trong chế độ này, người chơi sẽ tự mình tương tác với bảng kẹo, thực hiện các nước đi bằng chuột hoặc bàn phím để đạt được mục tiêu của cấp độ.

Mục tiêu: Người chơi thể hiện kỹ năng và chiến lược cá nhân để vượt qua các thử thách của trò chơi.


**Chế độ AI (AI Play Mode):**

Mô tả: Đây là chế độ mà một hoặc nhiều thuật toán AI được kích hoạt để chơi trò chơi. Người chơi có thể quan sát cách AI phân tích bảng kẹo, đưa ra quyết định và thực hiện các nước đi một cách tự động. Chế độ này có thể bao gồm:

AI Hỗ trợ: AI đưa ra gợi ý nước đi tốt nhất cho người chơi.

AI Tự động chơi: AI tự động hoàn thành cấp độ mà không cần sự can thiệp của người chơi.

So sánh Thuật toán: Hai hoặc nhiều thuật toán AI thi đấu với nhau trên cùng một cấp độ, cho phép người dùng trực quan so sánh hiệu suất và chiến lược của chúng.

Mục tiêu: Giúp người dùng quan sát, phân tích và so sánh hiệu quả, tốc độ, cũng như chiến lược của các thuật toán AI trong môi trường thực tế của trò chơi Candy Crush.

## Các Cấp Độ: 
Trò chơi được thiết kế với 3 cấp độ khác nhau, mỗi cấp độ có mục tiêu và thử thách riêng:

**Cấp độ 1:**

Mục tiêu: Đạt 800 điểm

Số lượt chơi: 20 lượt

**Cấp độ 2:**

Mục tiêu: Phá hủy hết kẹo dẻo (Jelly) để qua màn.

Số lượt chơi: 15 lượt

**Cấp độ 3:**

Mục tiêu: Đạt 1200 điểm

Số lượt chơi: 10 lượt


## Các Thuật Toán AI Sử Dụng Trong Dự Án: 
Dự án này tích hợp 7 thuật toán AI để tìm kiếm nước đi tối ưu trong trò chơi Candy Crush. Mỗi thuật toán có cách tiếp cận riêng, thể hiện sự đa dạng trong lĩnh vực trí tuệ nhân tạo:


****A** Search**

Loại: Tìm kiếm có thông tin (Informed Search).

Mô tả: Thuật toán này tìm kiếm nước đi bằng cách cân bằng giữa chi phí đã đi đến trạng thái hiện tại (g(n)) và ước lượng chi phí để đến đích (h(n)), sử dụng hàm f(n) = g(n) + h(n). Trong Candy Crush, A* cố gắng tìm chuỗi nước đi dẫn đến điểm số cao nhất hoặc hoàn thành mục tiêu cấp độ một cách hiệu quả.

Ứng dụng: Hiệu quả trong việc tìm kiếm các nước đi tối ưu trong không gian trạng thái lớn của bảng kẹo.


**BFS Search (Breadth-First Search)**

Loại: Tìm kiếm không có thông tin (Uninformed Search).

Mô tả: BFS khám phá tất cả các nước đi có thể ở cùng một độ sâu trước khi chuyển sang độ sâu tiếp theo. Nó đảm bảo tìm thấy nước đi "ngắn nhất" (ít bước nhất) để đạt được một trạng thái mong muốn.

Ứng dụng: Tìm kiếm chuỗi nước đi tối thiểu để đạt được một mục tiêu cụ thể, ví dụ như tạo ra một kẹo đặc biệt hoặc phá hủy một số lượng kẹo nhất định.


**Backtracking**

Loại: Tìm kiếm dựa trên thử và sai (Trial and Error).

Mô tả: Thuật toán này thử một chuỗi nước đi, và nếu chuỗi đó không dẫn đến kết quả mong muốn hoặc đạt đến ngõ cụt, nó sẽ "quay lui" để thử một lựa chọn khác.

Ứng dụng: Phù hợp cho các bài toán mà cần khám phá nhiều chuỗi hành động tiềm năng và đánh giá chúng, chẳng hạn như tìm kiếm nước đi combo lớn nhất.


**AND-OR Search**

Loại: Tìm kiếm trong không gian trạng thái phức tạp với điều kiện (AND/OR).

Mô tả: Thuật toán này phân chia bài toán thành các nhánh con logic: nhánh AND yêu cầu tất cả các điều kiện con phải được thỏa mãn (ví dụ: tạo kẹo đặc biệt AND kích hoạt nó), trong khi nhánh OR chỉ cần một trong các điều kiện con được thỏa mãn (ví dụ: tạo kẹo sọc HOẶC tạo kẹo bọc).

Ứng dụng: Xử lý các tình huống phức tạp nơi nước đi có thể dẫn đến nhiều kết quả tiềm năng phụ thuộc lẫn nhau.


**Simulated Annealing**

Loại: Thuật toán tối ưu hóa metaheuristic.

Mô tả: Lấy cảm hứng từ quá trình tôi luyện kim loại, thuật toán này bắt đầu với một "nhiệt độ" cao, cho phép nó chấp nhận cả những nước đi kém hơn với một xác suất nhất định để thoát khỏi các cực tiểu cục bộ. Nhiệt độ giảm dần theo thời gian, khiến thuật toán tập trung vào những nước đi tốt hơn.

Ứng dụng: Tìm kiếm một nước đi tốt trong không gian giải pháp rộng lớn, đặc biệt khi có nhiều nước đi tiềm năng có thể dẫn đến kết quả tương tự.


**Q-Learning**

Loại: Học tăng cường (Reinforcement Learning).

Mô tả: Thuật toán này cho phép AI học cách tối ưu hành động (hoán đổi kẹo) thông qua phản hồi (thưởng/phạt) từ môi trường trò chơi. AI xây dựng một "bảng Q" để lưu trữ giá trị của việc thực hiện một hành động trong một trạng thái cụ thể.

Ứng dụng: Học các chiến lược chơi tối ưu qua nhiều lần thử nghiệm và lỗi, có khả năng thích nghi với các tình huống bảng kẹo khác nhau.


**Hybrid Search**

Loại: Kết hợp các thuật toán.

Mô tả: Thuật toán này kết hợp sức mạnh của A* Search và Simulated Annealing. Nó có thể sử dụng A* để tìm một tập hợp các nước đi tiềm năng tốt nhất ban đầu, sau đó sử dụng Simulated Annealing để tinh chỉnh và khám phá các biến thể của những nước đi đó, giúp tránh các bẫy cục bộ và tìm ra nước đi thực sự tối ưu hơn.

Ứng dụng: Cung cấp một giải pháp mạnh mẽ và linh hoạt, tận dụng lợi thế của cả tìm kiếm có thông tin và heuristic.

## Tài liệu tham khảo:

1.	Pygame Documentation. Truy cập tại: https://www.pygame.org/docs/. Tài liệu chính thức của Pygame, cung cấp hướng dẫn chi tiết về cách sử dụng thư viện để phát triển giao diện, xử lý sự kiện, và tích hợp âm thanh/hình ảnh trong trò chơi Candy Crush. 

2.	Candy Crush Saga Official Website. Truy cập tại: https://www.candycrushsaga.com/. Nguồn tham khảo chính về lối chơi, thiết kế cấp độ, và các yếu tố tạo nên sức hút của trò chơi match-3 gốc, giúp nhóm tái hiện các tính năng cốt lõi trong dự án. 

3.	Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). Introduction to Algorithms (3rd ed.). MIT Press. Sách tham khảo về các thuật toán tìm kiếm và tối ưu, bao gồm A* và Hill Climbing, được sử dụng để triển khai AI trong trò chơi. 

# Hướng Dẫn Cài Đặt
Cài Python 3.x và Pygame: pip install pygame.

Clone repository: git clone <repo-url>.

Chạy trò chơi: python main.py.
