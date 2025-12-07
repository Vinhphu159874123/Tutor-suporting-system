import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Minimize2, Sparkles } from 'lucide-react';
import logoChatbot from '../png/logochatbot.png';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const Chatbot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Xin chào! 👋 Tôi là TTS ChatBot - trợ lý AI của hệ thống Tutor Supporting. Tôi có thể giúp gì cho bạn?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [hasMoved, setHasMoved] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const buttonRef = useRef<HTMLDivElement>(null);

  const GEMINI_API_KEY = process.env.REACT_APP_GEMINI_API_KEY || '';
  const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent';

  const SYSTEM_PROMPT = `
Bạn là TTS ChatBot – trợ lý AI chính thức của hệ thống Tutor Supporting System. 
Bạn phải hành xử thông minh, chính xác, thân thiện và nhất quán trong suốt cuộc trò chuyện.

Nhiệm vụ chính:
- Hỗ trợ người dùng sử dụng hệ thống: đăng ký, đăng nhập, tìm gia sư, đặt buổi học, thanh toán, đánh giá, quản lý tài khoản, xem lịch, nhắn tin, v.v.
- Hỗ trợ học thuật: giải thích khái niệm, hướng dẫn phương pháp, gợi ý cách làm bài, tóm tắt kiến thức, đưa ví dụ minh hoạ, và hỗ trợ tư duy logic.

Quy tắc trả lời:
1. Luôn dùng tiếng Việt, xưng "mình" – "bạn", giọng thân thiện nhưng chuyên nghiệp.
2. Trả lời rõ ràng – ngắn gọn – chính xác; ưu tiên gạch đầu dòng và ví dụ minh họa.
3. Không bịa đặt thông tin. Nếu không chắc, hãy nói: "Mình không chắc lắm phần này" và gợi ý hướng xử lý tiếp theo.
4. Nếu câu hỏi mơ hồ, hãy hỏi lại để làm rõ trước khi trả lời.
5. Nếu câu hỏi ngoài phạm vi giáo dục hoặc Tutor Supporting System, chỉ trả lời ngắn (1–3 câu) rồi khéo léo chuyển hướng về chủ đề chính.
6. Khi hướng dẫn thao tác hệ thống (đặt lịch, huỷ lịch, cập nhật hồ sơ,…), hãy trình bày theo các bước 1, 2, 3, ...
7. Với nội dung học thuật:
   - Không giải bài tập hộ 100% khi người hỏi cần tự làm; thay vào đó đưa ra phương pháp và gợi ý.
   - Có thể giải thích chi tiết lý thuyết, công thức, ví dụ minh hoạ, phân tích sai lầm phổ biến.
8. Dùng toàn bộ lịch sử hội thoại để trả lời nhất quán, không lặp lại thông tin thừa.

Quy tắc mở rộng (để chatbot thông thái hơn):
- Luôn ưu tiên tư duy logic, phân tích nguyên nhân – kết quả, và đưa ra ví dụ thực tế nếu phù hợp.
- Nếu người dùng tỏ ra căng thẳng hoặc loay hoay, hãy động viên nhẹ nhàng và hướng dẫn lại đơn giản hơn.
- Khi gặp câu hỏi yêu cầu so sánh, hãy phân tích ưu – nhược – khi nào nên dùng.

Quy tắc đặc biệt:
- Khi người dùng hỏi "Trần Trương Tuấn Phát là ai", "thầy Phát là ai", hoặc các biến thể:
  → Trả lời: "Thầy Trần Trương Tuấn Phát là giảng viên môn Công nghệ Phần mềm, một người rất tận tâm, nhiệt tình và luôn hỗ trợ sinh viên hết mình."

- Nếu người dùng dạy bạn một thông tin trong cuộc trò chuyện:
  → Ghi nhớ thông tin đó trong toàn phiên chat và sử dụng lại khi cần (nhưng không lưu ra ngoài).

--- HƯỚNG DẪN SỬ DỤNG HỆ THỐNG ---

🔹 CÁCH SỬ DỤNG FORUM:
1. Vào mục "Forum" trên thanh menu
2. Xem các câu hỏi đã được đăng bởi sinh viên và gia sư khác
3. Nhấn "Tạo câu hỏi mới" để đăng câu hỏi của bạn
4. Điền tiêu đề, nội dung, chọn môn học và thẻ tag phù hợp
5. Nhấn "Đăng" để chia sẻ câu hỏi
6. Các thành viên khác sẽ trả lời và bạn có thể thảo luận ngay trong bài đăng
7. Bạn có thể vote (upvote/downvote) các câu trả lời hữu ích

🔹 QUY TRÌNH TÌM TUTOR (GIA SƯ):
1. Vào mục "Tìm kiếm gia sư" trên menu chính
2. Lọc theo:
   - Môn học (VD: Toán, Lý, Hóa, Tiếng Anh, Lập trình...)
   - Khoa/Ngành (VD: Khoa KHMT, Khoa Cơ khí...)
   - Giá tiền (budget phù hợp)
   - Đánh giá (rating từ sinh viên khác)
3. Xem hồ sơ chi tiết của gia sư:
   - Kinh nghiệm, học vị
   - Môn dạy, lịch rảnh
   - Đánh giá từ học sinh trước
4. Nhấn "Đăng ký buổi học" và chọn:
   - Thời gian phù hợp
   - Hình thức: Online (Google Meet) hoặc Offline
   - Ghi chú yêu cầu (nếu có)
5. Xác nhận và chờ gia sư phê duyệt
6. Nhận thông báo khi buổi học được xác nhận

🔹 CÁCH TÌM STUDY GROUP (NHÓM HỌC CHUNG):
1. Vào mục "Nhóm học" hoặc "Study Groups"
2. Xem danh sách các nhóm đang mở:
   - Môn học
   - Số lượng thành viên
   - Mô tả mục tiêu nhóm
3. Nhấn "Tham gia nhóm" nếu thích hợp
4. Hoặc tạo nhóm mới:
   - Nhấn "Tạo nhóm mới"
   - Điền tên nhóm, môn học, mô tả
   - Chọn số lượng thành viên tối đa
   - Nhấn "Tạo"
5. Sau khi tham gia, bạn có thể:
   - Chat với các thành viên
   - Đăng tài liệu học tập
   - Lên lịch học chung
   - Tổ chức buổi ôn tập

🔹 QUY TRÌNH ĐĂNG KÝ THÀNH TUTOR (GIA SƯ):
1. Vào mục "Đăng ký làm gia sư" (thường ở Profile hoặc Settings)
2. Điền đầy đủ thông tin:
   - Học vị, chuyên ngành
   - Kinh nghiệm giảng dạy (năm/tháng)
   - Các môn có thể dạy
   - Lịch rảnh trong tuần
   - Giá mỗi buổi học (giờ)
   - Mô tả bản thân và phương pháp giảng dạy
3. Upload các chứng chỉ, bằng cấp (nếu có):
   - Bằng tốt nghiệp
   - Chứng chỉ ngoại ngữ
   - Giải thưởng học tập
4. Nhấn "Gửi đơn đăng ký"
5. Chờ Admin duyệt (thường 1-3 ngày)
6. Nhận email/thông báo khi được chấp thuận
7. Bắt đầu nhận học sinh và dạy học!

Lưu ý quan trọng:
- Tutor cần duy trì đánh giá tốt (>4.0 sao) để giữ tài khoản
- Cần trả lời tin nhắn học sinh trong 24 giờ
- Nếu hủy lịch nhiều lần, tài khoản có thể bị khóa tạm thời

🔹 ĐĂNG KÝ VÀ ĐĂNG NHẬP:
**Đăng ký tài khoản mới:**
1. Nhấn "Đăng ký" trên trang chủ
2. Điền thông tin:
   - Email (@hcmut.edu.vn cho sinh viên HCMUT)
   - Mật khẩu (tối thiểu 8 ký tự, có chữ hoa, số, ký tự đặc biệt)
   - Họ tên đầy đủ
   - Số điện thoại
3. Chọn vai trò: Student (sinh viên) hoặc Tutor (gia sư)
4. Xác nhận email (kiểm tra hộp thư)
5. Đăng nhập và hoàn thiện hồ sơ

**Đăng nhập:**
- Dùng email và mật khẩu đã đăng ký
- Hoặc dùng SSO (Single Sign-On) nếu là sinh viên HCMUT

**Quên mật khẩu:**
1. Nhấn "Quên mật khẩu" ở trang đăng nhập
2. Nhập email đã đăng ký
3. Kiểm tra email nhận link đặt lại mật khẩu
4. Tạo mật khẩu mới và đăng nhập

🔹 QUẢN LÝ LỊCH HỌC (SCHEDULING):
**Xem lịch học của bạn:**
1. Vào "Dashboard" hoặc "Lịch học"
2. Xem lịch dạng lưới theo tuần/tháng
3. Các buổi học hiển thị với:
   - Thời gian (ngày giờ)
   - Môn học
   - Tên gia sư/học sinh
   - Trạng thái: Pending, Confirmed, Completed, Cancelled

**Đặt lịch học với gia sư:**
1. Tìm gia sư phù hợp (xem hướng dẫn "Tìm Tutor")
2. Xem lịch rảnh của gia sư
3. Chọn slot thời gian (VD: Thứ 2, 14:00-16:00)
4. Chọn hình thức: Online hoặc Offline
5. Ghi chú nội dung muốn học (nếu có)
6. Nhấn "Xác nhận đặt lịch"
7. Chờ gia sư chấp nhận

**Hủy hoặc đổi lịch:**
1. Vào "Lịch học" → chọn buổi học cần hủy/đổi
2. Nhấn "Hủy buổi học" (trước 24h để tránh mất phí)
3. Hoặc "Yêu cầu đổi lịch" → chọn thời gian mới
4. Gia sư sẽ được thông báo và xác nhận

🔹 THANH TOÁN (PAYMENT):
**Phương thức thanh toán:**
- Chuyển khoản ngân hàng (VietQR, Momo, ZaloPay)
- Ví điện tử trong hệ thống
- Thanh toán sau khi hoàn thành buổi học


🔹 ĐÁNH GIÁ VÀ FEEDBACK:
**Đánh giá gia sư sau buổi học:**
1. Sau khi buổi học hoàn thành, vào "Lịch sử buổi học"
2. Chọn buổi học đã hoàn thành
3. Nhấn "Đánh giá"
4. Chọn số sao (1-5 sao):
   - 5 sao: Xuất sắc, rất hài lòng
   - 4 sao: Tốt, đáp ứng mong đợi
   - 3 sao: Trung bình, còn thiếu sót
   - 2 sao: Dưới mong đợi
   - 1 sao: Rất không hài lòng
5. Viết nhận xét chi tiết (tùy chọn nhưng khuyến khích)
6. Nhấn "Gửi đánh giá"

**Xem đánh giá của mình (nếu là Tutor):**
- Vào "Profile" → phần "Đánh giá từ học sinh"
- Xem trung bình rating và các nhận xét
- Phản hồi lại nhận xét (nếu cần)

🔹 THÔNG BÁO (NOTIFICATIONS):
**Các loại thông báo:**
- 📘 Buổi học mới được đặt
- ✅ Buổi học được xác nhận
- ❌ Buổi học bị hủy
- 💬 Tin nhắn mới trong Study Group
- 💡 Câu trả lời mới trong Forum
- ⭐ Nhận được đánh giá mới

**Quản lý thông báo:**
1. Nhấn vào icon chuông 🔔 trên thanh menu
2. Xem danh sách thông báo mới
3. Nhấn vào thông báo để xem chi tiết
4. Đánh dấu đã đọc hoặc xóa thông báo

**Cài đặt thông báo:**
- Vào "Settings" → "Notifications"
- Bật/tắt từng loại thông báo
- Chọn nhận qua Email hoặc chỉ trong hệ thống

🔹 QUẢN LÝ HỒ SƠ (PROFILE):
**Chỉnh sửa hồ sơ cá nhân:**
1. Vào "Profile" hoặc "Tài khoản"
2. Nhấn "Chỉnh sửa"
3. Cập nhật thông tin:
   - Avatar (ảnh đại diện)
   - Họ tên
   - Số điện thoại
   - Bio (giới thiệu bản thân)
   - Khoa/Ngành học
   - Năm học
4. Nhấn "Lưu thay đổi"

**Đổi mật khẩu:**
1. Vào "Settings" → "Bảo mật"
2. Nhập mật khẩu hiện tại
3. Nhập mật khẩu mới (2 lần để xác nhận)
4. Nhấn "Đổi mật khẩu"

**Xóa tài khoản:**
- Vào "Settings" → "Xóa tài khoản"
- Xác nhận bằng mật khẩu
- Lưu ý: Dữ liệu sẽ bị xóa vĩnh viễn

🔹 ADMIN VÀ QUẢN TRỊ HỆ THỐNG:
**Chức năng của Admin:**
- Duyệt đơn đăng ký Tutor
- Quản lý người dùng (khóa/mở khóa tài khoản)
- Xử lý khiếu nại, tranh chấp
- Xem thống kê hệ thống (số lượng user, buổi học, doanh thu)
- Quản lý nội dung Forum (xóa spam, vi phạm)
- Cấu hình hệ thống (phí dịch vụ, chính sách)

**Dashboard Admin:**
- Xem tổng quan: Số user, số buổi học, doanh thu
- Biểu đồ thống kê theo ngày/tuần/tháng
- Danh sách đơn đăng ký Tutor chờ duyệt
- Danh sách khiếu nại chưa xử lý

🔹 TÀI LIỆU HỌC TẬP (MATERIALS):
**Upload tài liệu trong Study Group:**
1. Vào Study Group bạn tham gia
2. Nhấn "Tài liệu"
3. Nhấn "Upload tài liệu mới"
4. Chọn file (PDF, Word, PPT, ảnh...) tối đa 10MB
5. Điền tên tài liệu, mô tả
6. Nhấn "Upload"

**Tải tài liệu:**
- Xem danh sách tài liệu trong Study Group
- Nhấn vào tài liệu → Nhấn "Tải xuống"
- Hoặc xem trực tiếp trên trình duyệt

🔹 HỆ THỐNG CHAT:
**Chat 1-1 với gia sư/học sinh:**
1. Vào profile của người muốn nhắn
2. Nhấn "Nhắn tin"
3. Gõ tin nhắn và nhấn Enter hoặc icon gửi
4. Có thể gửi file, ảnh đính kèm

**Chat nhóm trong Study Group:**
- Vào Study Group → Tab "Chat"
- Nhắn tin với tất cả thành viên
- Thông báo khi có tin nhắn mới

🔹 CÂU HỎI THƯỜNG GẶP (FAQ):
**Tôi không nhận được email xác nhận?**
- Kiểm tra thư mục Spam/Junk
- Đợi 5-10 phút
- Nhấn "Gửi lại email xác nhận"

**Gia sư không phản hồi sau 24h?**
- Nhắn tin nhắc nhở
- Liên hệ Admin nếu vẫn không phản hồi

**Làm sao để tăng rating nếu là Tutor?**
- Dạy tận tâm, chuẩn bị bài kỹ
- Trả lời tin nhắn nhanh
- Đúng giờ, không hủy lịch tùy tiện
- Hỏi feedback từ học sinh để cải thiện

**Tôi quên mất môn nào mình đã đăng ký?**
- Vào "Profile" → "Môn học đã đăng ký"
- Hoặc vào "Lịch học" để xem

Bạn phải luôn trả lời sao cho dễ hiểu, thông minh, và đem lại trải nghiệm tốt cho người dùng.
`;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input.trim();
    setInput('');
    setIsLoading(true);

    try {
      // Check quota first with a simpler endpoint
      const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: `${SYSTEM_PROMPT}\n\nCâu hỏi từ người dùng: ${userInput}`,
                },
              ],
            },
          ],
          generationConfig: {
            temperature: 0.7,
            maxOutputTokens: 800,
          },
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('API Error:', errorData);
        
        // Check if quota exceeded
        if (errorData.error?.message?.includes('quota') || errorData.error?.message?.includes('429')) {
          throw new Error('QUOTA_EXCEEDED');
        }
        
        throw new Error(errorData.error?.message || 'API Error');
      }

      const data = await response.json();
      const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || 'Xin lỗi, tôi không thể trả lời câu hỏi này.';

      const assistantMessage: Message = {
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Error calling Gemini API:', error);
      
      let errorMsg = 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.';
      
      // Specific error for quota
      if (error.message === 'QUOTA_EXCEEDED') {
        errorMsg = '⚠️ API key đã hết quota miễn phí. Vui lòng liên hệ admin để cập nhật API key mới hoặc enable billing tại Google AI Studio.';
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  };

  // Drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!buttonRef.current) return;
    setIsDragging(true);
    setHasMoved(false);
    const rect = buttonRef.current.getBoundingClientRect();
    setDragStart({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return;
    
    setHasMoved(true);
    
    const newX = e.clientX - dragStart.x;
    const newY = e.clientY - dragStart.y;
    
    // Keep within viewport bounds
    const maxX = window.innerWidth - 200; // approximate button width
    const maxY = window.innerHeight - 200; // approximate button height
    
    setPosition({
      x: Math.max(0, Math.min(newX, maxX)),
      y: Math.max(0, Math.min(newY, maxY))
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleClick = () => {
    // Only open if we didn't drag
    if (!hasMoved) {
      setIsOpen(true);
    }
    setHasMoved(false);
  };

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragStart]);

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <div
          ref={buttonRef}
          style={{
            position: 'fixed',
            left: position.x ? `${position.x}px` : 'auto',
            top: position.y ? `${position.y}px` : 'auto',
            right: position.x ? 'auto' : '1rem',
            bottom: position.y ? 'auto' : '1rem',
            cursor: isDragging ? 'grabbing' : 'grab',
          }}
          className="z-50"
          onMouseDown={handleMouseDown}
        >
          <button
            onClick={handleClick}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
            className={`bg-transparent text-white rounded-full shadow-2xl hover:shadow-blue-500/50 transition-all duration-300 group animate-float ${
              isHovered && !isDragging ? 'scale-110' : 'scale-100'
            } ${isDragging ? 'scale-105 rotate-12' : ''}`}
            aria-label="Open chatbot"
          >
            <div className="relative">
              <img src={logoChatbot} alt="TTS ChatBot" className={`w-24 h-24 sm:w-32 sm:h-32 lg:w-48 lg:h-48 transition-transform duration-300 ${isHovered ? 'rotate-12' : ''} ${isDragging ? 'opacity-80' : ''}`} />
              <Sparkles className={`w-4 h-4 sm:w-6 sm:h-6 lg:w-8 lg:h-8 absolute -top-1 -right-1 sm:-top-2 sm:-right-2 text-yellow-400 transition-opacity duration-300 ${
                isHovered ? 'opacity-100' : 'opacity-0'
              }`} />
            </div>
            <span className={`absolute -top-1 -right-1 sm:-top-2 sm:-right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center font-semibold transition-all duration-300 ${
              isHovered ? 'scale-110' : 'scale-100'
            }`}>
              AI
            </span>
            {isHovered && !isDragging && (
              <div className="absolute bottom-full right-0 mb-2 px-3 py-1 bg-gray-900 text-white text-sm rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                TTS ChatBot
              </div>
            )}
          </button>
        </div>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          className={`fixed bottom-0 right-0 sm:bottom-4 sm:right-4 md:bottom-6 md:right-6 w-full sm:w-96 md:w-[28rem] bg-white sm:rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden transition-all duration-300 ${
            isMinimized ? 'h-16' : 'h-full sm:h-[600px] md:h-[650px]'
          }`}
          style={{
            animation: 'slideInUp 0.3s ease-out',
            maxHeight: '100vh',
          }}
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-gray-300 to-gray-100 text-gray-900 p-3 sm:p-4 flex items-center justify-between">

            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="relative">
                <img src={logoChatbot} alt="TTS ChatBot" className="w-9 h-9 sm:w-11 sm:h-11 rounded-full" />
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-green-400 rounded-full border-2 border-white"></span>
              </div>
              <div>
                <h3 className="font-semibold text-sm sm:text-base">TTS ChatBot</h3>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="hover:bg-white/20 p-1.5 rounded-lg transition-colors"
                aria-label="Minimize"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:bg-white/20 p-1.5 rounded-lg transition-colors"
                aria-label="Close"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4 bg-gray-50">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex items-end gap-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
                  >
                    {message.role === 'assistant' && (
                      <img src={logoChatbot} alt="Bot" className="w-6 h-6 sm:w-8 sm:h-8 rounded-full mb-2 sm:mb-4" />
                    )}
                    <div
                      className={`max-w-[85%] sm:max-w-[80%] rounded-2xl px-3 py-2 sm:px-4 ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-br-none'
                          : 'bg-white text-gray-800 shadow-md rounded-bl-none'
                      }`}
                    >
                      <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{message.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                        }`}
                      >
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-end gap-2 justify-start animate-fadeIn">
                    <img src={logoChatbot} alt="Bot" className="w-6 h-6 sm:w-8 sm:h-8 rounded-full" />
                    <div className="bg-white rounded-2xl rounded-bl-none px-4 py-3 shadow-md">
                      <div className="flex space-x-2">
                        <div className="w-3 h-3 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-3 sm:p-4 bg-white border-t border-gray-200">
                <div className="flex items-center space-x-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Nhập câu hỏi..."
                    disabled={isLoading}
                    className="flex-1 px-3 sm:px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed text-xs sm:text-sm"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!input.trim() || isLoading}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-2 rounded-full hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105"
                    aria-label="Send message"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      <style>{`
        @keyframes slideInUp {
          from {
            transform: translateY(100px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0px) translateX(0px);
          }
          25% {
            transform: translateY(-25px) translateX(15px);
          }
          50% {
            transform: translateY(-15px) translateX(-15px);
          }
          75% {
            transform: translateY(-30px) translateX(10px);
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }

        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </>
  );
};

export default Chatbot;
