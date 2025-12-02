import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import apiClient from "../../services/api";
import {
  ArrowLeft,
  CalendarDays,
  Eye,
  MessageSquare,
  Share2,
  ThumbsUp,
  UserRound,
} from "lucide-react";

type ThreadCategory = "study" | "exam" | "project" | "career" | "other";

interface ThreadDetail {
  id: string;
  title: string;
  category: ThreadCategory;
  author: string;
  createdAt: string;
  views: number;
  likes: number;
  replies: number;
  isSolved?: boolean;
  tags: string[];
  content: string;
}

interface Reply {
  id: string;
  author: string;
  role: "Tutor" | "Student" | "Coordinator";
  content: string;
  createdAt: string;
  likes: number;
  isLiked?: boolean;
  isAuthor?: boolean;
}

const threadMap: ThreadDetail[] = [
  {
    id: "1",
    title: "Kinh nghiệm vượt môn Cấu trúc dữ liệu trong 1 học kỳ",
    category: "study",
    author: "Nguyễn Văn A",
    createdAt: "2025-11-20T09:30:00",
    views: 520,
    likes: 42,
    replies: 18,
    isSolved: true,
    tags: ["DSA", "Tips", "Midterm"],
    content:
      "Mình tổng hợp toàn bộ tài liệu + checklist luyện tập giúp vượt môn DSA trong 1 kỳ. Bao gồm: kế hoạch 6 tuần, bộ flashcard thuật toán, template phân tích độ phức tạp và gợi ý bài LeetCode tương ứng.",
  },
  {
    id: "2",
    title: "Tìm team làm project cuối kỳ môn Công nghệ phần mềm",
    category: "project",
    author: "Trần Thị B",
    createdAt: "2025-11-19T14:00:00",
    views: 310,
    likes: 25,
    replies: 9,
    tags: ["Project", "React", "FastAPI"],
    content:
      "Team mình đang build hệ thống Tutor Supporting System, cần thêm 1 backend (FastAPI) và 1 frontend (React). Đã có thiết kế, board Jira và guideline merge code.",
  },
  {
    id: "3",
    title: "Chia sẻ bộ đề cương ôn thi Hệ điều hành",
    category: "exam",
    author: "Lê Văn C",
    createdAt: "2025-11-18T20:15:00",
    views: 210,
    likes: 18,
    replies: 4,
    tags: ["Exam", "Flashcard"],
    content:
      "Mình vừa tổng hợp outline + đề ôn midterm/midterm năm trước. Có cả flashcard về scheduling, memory, file system.",
  },
  {
    id: "4",
    title: "Định hướng nghề nghiệp cho sinh viên IT năm 3",
    category: "career",
    author: "Phạm Thu Hà",
    createdAt: "2025-11-17T08:45:00",
    views: 264,
    likes: 31,
    replies: 7,
    tags: ["Career", "Workshop"],
    content:
      "Sau khi tham dự workshop định hướng, mình tổng hợp tài liệu + Q&A với anh chị IT đang làm tại doanh nghiệp.",
  },
];

const repliesSeed: Reply[] = [
  {
    id: "101",
    author: "Nguyễn Văn A",
    role: "Tutor",
    content:
      "Checklist gồm 3 phần: lý thuyết, phân tích bài toán, và template code. Bạn có thể bắt đầu mỗi tuần bằng 3 bài Easy, 2 Medium.",
    createdAt: "2025-11-20T10:00:00",
    likes: 12,
    isLiked: true,
    isAuthor: true,
  },
  {
    id: "102",
    author: "Trần Thị B",
    role: "Student",
    content:
      "Bạn có thể share link drive tài liệu không? Team mình đang cần bộ flashcard.",
    createdAt: "2025-11-20T10:45:00",
    likes: 7,
  },
  {
    id: "103",
    author: "Lê Văn C",
    role: "Tutor",
    content:
      "Bổ sung thêm playlist YouTube về phân tích độ phức tạp giúp mổ xẻ từng bước rõ hơn.",
    createdAt: "2025-11-20T11:10:00",
    likes: 5,
  },
];

const ForumDetail: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [thread, setThread] = useState<ThreadDetail | null>(null);
  const [replies, setReplies] = useState<Reply[]>([]);
  const [replyContent, setReplyContent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);

  // Fetch thread details from API
  useEffect(() => {
    const fetchThreadDetail = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get(`/forum/${id}/posts`);
        const data = response.data;
        
        setThread({
          id: data.id,
          title: data.title,
          category: data.category,
          author: data.author,
          createdAt: data.createdAt,
          views: data.views || 0,
          likes: data.likes || 0,
          replies: Array.isArray(data.replies_list) ? data.replies_list.length : (data.replies || 0),
          isSolved: data.isSolved,
          tags: data.tags || [],
          content: data.content
        });
        
        setReplies(Array.isArray(data.replies_list) ? data.replies_list : []);
      } catch (error: any) {
        console.error("Error fetching thread:", error);
        toast.error("Không thể tải bài viết");
        navigate("/forum");
      } finally {
        setLoading(false);
      }
    };
    
    if (id) {
      fetchThreadDetail();
    }
  }, [id, navigate]);

  const formatDateTime = (value: string) =>
    new Date(value).toLocaleString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });

  const handleToggleReplyLike = (replyId: string) => {
    setReplies((prev) =>
      prev.map((reply) => {
        if (reply.id !== replyId) return reply;
        const isLiked = !reply.isLiked;
        return {
          ...reply,
          isLiked,
          likes: isLiked ? reply.likes + 1 : Math.max(reply.likes - 1, 0),
        };
      })
    );
  };

  const handleReply = async () => {
    if (!replyContent.trim()) return;
    
    setIsSubmitting(true);
    try {
      const response = await apiClient.post(`/forum/${id}/reply`, {
        content: replyContent.trim(),
        parent_post_id: parseInt(id || "0")
      });
      
      // Add new reply to list
      const newReply: Reply = {
        id: response.data.reply_id?.toString() || Date.now().toString(),
        author: response.data.author || "Bạn",
        role: response.data.role || "Student",
        content: replyContent.trim(),
        createdAt: response.data.created_at || new Date().toISOString(),
        likes: 0,
        isLiked: false,
        isAuthor: true
      };
      
      setReplies((prev) => [...prev, newReply]);
      setReplyContent("");
      toast.success("Đã gửi phản hồi thành công!");
    } catch (error: any) {
      console.error("Error posting reply:", error);
      toast.error(error?.response?.data?.detail || "Không thể gửi phản hồi");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Đang tải bài viết...</p>
        </div>
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <p className="text-gray-600">Không tìm thấy bài viết</p>
          <button 
            onClick={() => navigate("/forum")}
            className="mt-4 text-blue-600 hover:underline"
          >
            Quay lại danh sách
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-6">
      <button
        onClick={() => navigate("/forum")}
        className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        Quay lại danh sách
      </button>

      {/* Thread header */}
      <article className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500">
          <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-semibold text-xs uppercase">
            {thread.category}
          </span>
          <span className="inline-flex items-center gap-1">
            <UserRound className="w-4 h-4" />
            {thread.author}
          </span>
          <span className="inline-flex items-center gap-1">
            <CalendarDays className="w-4 h-4" />
            {formatDateTime(thread.createdAt)}
          </span>
          <span className="inline-flex items-center gap-1">
            <Eye className="w-4 h-4" />
            {thread.views} lượt xem
          </span>
          <span className="inline-flex items-center gap-1">
            <MessageSquare className="w-4 h-4" />
            {thread.replies} phản hồi
          </span>
          {thread.isSolved && (
            <span className="text-green-600 font-semibold">Đã giải quyết</span>
          )}
        </div>

        <h1 className="text-3xl font-bold text-gray-900">{thread.title}</h1>
        <p className="text-gray-700 leading-relaxed">{thread.content}</p>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex gap-2 text-sm">
            {thread.tags.map((tag) => (
              <span key={tag} className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full">
                #{tag}
              </span>
            ))}
          </div>
          <div className="flex gap-3 ml-auto">
            <button className="px-4 py-2 rounded-lg border border-gray-200 text-gray-700 flex items-center gap-2">
              <ThumbsUp className="w-4 h-4" />
              {thread.likes}
            </button>
            <button className="px-4 py-2 rounded-lg border border-gray-200 text-gray-700 flex items-center gap-2">
              <Share2 className="w-4 h-4" />
              Chia sẻ
            </button>
          </div>
        </div>
      </article>

      {/* Replies */}
      <section className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-bold text-gray-900">Trao đổi ({replies.length})</h2>
          {replies.map((reply) => (
            <div key={reply.id} className="bg-white rounded-lg shadow-md p-5">
              <div className="flex gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                  <UserRound className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-2 justify-between">
                    <div>
                      <p className="font-semibold text-gray-900">{reply.author}</p>
                      <p className="text-sm text-gray-500">
                        {reply.role} • {formatDateTime(reply.createdAt)}
                      </p>
                    </div>
                    {reply.isAuthor && (
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-semibold">
                        Tác giả
                      </span>
                    )}
                  </div>
                  <p className="text-gray-700 mt-3 mb-4">{reply.content}</p>
                  <div className="flex gap-3 text-sm">
                    <button
                      onClick={() => handleToggleReplyLike(reply.id)}
                      className={`px-4 py-2 rounded-lg border flex items-center gap-2 transition ${
                        reply.isLiked
                          ? "bg-blue-50 border-blue-200 text-blue-700"
                          : "border-gray-200 text-gray-700 hover:bg-gray-50"
                      }`}
                    >
                      <ThumbsUp className="w-4 h-4" /> {reply.likes}
                    </button>
                    <button className="px-4 py-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2">
                      <MessageSquare className="w-4 h-4" />
                      Trả lời
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-5">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Thông tin chủ đề</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>Ngày tạo: {formatDateTime(thread.createdAt)}</li>
              <li>Tác giả: {thread.author}</li>
              <li>Lượt xem: {thread.views}</li>
              <li>Phản hồi: {replies.length}</li>
            </ul>
          </div>

          <div className="bg-white rounded-lg shadow-md p-5">
            <h3 className="text-lg font-bold text-gray-900 mb-3">Thêm phản hồi</h3>
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              rows={5}
              placeholder="Chia sẻ quan điểm hoặc tài liệu hỗ trợ..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-3"
            />
            <button
              onClick={handleReply}
              disabled={isSubmitting}
              className={`w-full py-3 rounded-lg font-semibold text-white transition ${
                isSubmitting
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isSubmitting ? "Đang gửi..." : "Gửi phản hồi"}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ForumDetail;
