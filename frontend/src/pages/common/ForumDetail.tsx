import React from "react";
import { useParams, useNavigate } from "react-router-dom";

interface ForumPost {
  id: string;
  author: string;
  content: string;
  timestamp: string;
  likes: number;
  isLiked: boolean;
}

const ForumDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const forum = {
    id: id || "1",
    title: "Cách học hiệu quả môn Công nghệ phần mềm",
    author: "Nguyễn Văn A",
    createdAt: "2025-11-15 10:30:00",
    category: "Học tập",
    views: 152,
    replies: 12,
  };

  const posts: ForumPost[] = [
    {
      id: "1",
      author: "Nguyễn Văn A",
      content:
        "Xin chào mọi người! Mình đang học môn Công nghệ phần mềm và cảm thấy khá khó. Các bạn có thể chia sẻ kinh nghiệm học tập không?",
      timestamp: "2025-11-15 10:30:00",
      likes: 8,
      isLiked: false,
    },
    {
      id: "2",
      author: "Trần Thị B",
      content:
        "Mình nghĩ bạn nên tập trung vào thực hành nhiều hơn là học lý thuyết. Làm các bài tập nhóm sẽ giúp bạn hiểu sâu hơn về các mô hình phát triển phần mềm.",
      timestamp: "2025-11-15 11:00:00",
      likes: 12,
      isLiked: false,
    },
    {
      id: "3",
      author: "Lê Văn C",
      content:
        "Mình đồng ý! Và đừng quên đọc các case study thực tế. Nó sẽ giúp bạn liên hệ lý thuyết với thực tiễn tốt hơn.",
      timestamp: "2025-11-15 11:15:00",
      likes: 5,
      isLiked: true,
    },
  ];

  const [replyContent, setReplyContent] = React.useState("");

  const handleReply = () => {
    if (replyContent.trim()) {
      console.log("New reply:", replyContent);
      setReplyContent("");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <button
        onClick={() => navigate("/forum")}
        className="mb-4 text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-2"
      >
        ← Quay lại danh sách
      </button>

      {/* Forum Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="mb-4">
          <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-semibold">
            {forum.category}
          </span>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {forum.title}
        </h1>
        <div className="flex items-center gap-4 text-gray-600">
          <span>👤 {forum.author}</span>
          <span>📅 {forum.createdAt}</span>
          <span>👁️ {forum.views} lượt xem</span>
          <span>💬 {forum.replies} phản hồi</span>
        </div>
      </div>

      {/* Posts */}
      <div className="space-y-4 mb-6">
        {posts.map((post, index) => (
          <div key={post.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-xl">
                  👤
                </div>
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-bold text-gray-900">{post.author}</p>
                    <p className="text-sm text-gray-500">{post.timestamp}</p>
                  </div>
                  {index === 0 && (
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-semibold">
                      Tác giả
                    </span>
                  )}
                </div>
                <p className="text-gray-700 mb-4">{post.content}</p>
                <div className="flex gap-4">
                  <button
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                      post.isLiked
                        ? "bg-blue-100 text-blue-700"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    👍 {post.likes}
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
                    💬 Trả lời
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Reply Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Trả lời</h3>
        <textarea
          value={replyContent}
          onChange={(e) => setReplyContent(e.target.value)}
          placeholder="Nhập phản hồi của bạn..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
          rows={4}
        />
        <button
          onClick={handleReply}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          Gửi phản hồi
        </button>
      </div>
    </div>
  );
};

export default ForumDetail;
