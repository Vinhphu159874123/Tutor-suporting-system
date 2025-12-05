import React, { useMemo, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { AxiosResponse } from "axios";
import apiClient from "../../services/api";
import {
  ArrowRight,
  CalendarDays,
  Eye,
  MessageSquare,
  Search,
  ThumbsUp,
  UserRound,
} from "lucide-react";

type ThreadCategory =
  | "all"
  | "study"
  | "exam"
  | "project"
  | "career"
  | "other";

interface ForumThread {
  id: string;
  title: string;
  category: Exclude<ThreadCategory, "all">;
  author: string;
  createdAt: string;
  excerpt: string;
  likes: number;
  replies: number;
  views: number;
  isPinned?: boolean;
  isSolved?: boolean;
  tags: string[];
  isLiked?: boolean;
}

const trendingTags = [
  { label: "React", count: 32 },
  { label: "Python", count: 27 },
  { label: "DSA", count: 21 },
  { label: "Career", count: 18 },
  { label: "Exam", count: 15 },
];

const topContributors = [
  { name: "Nguyễn Văn A", role: "Tutor", points: 842 },
  { name: "Trần Thị B", role: "Student", points: 790 },
  { name: "Lê Văn C", role: "Tutor", points: 720 },
];

const Forum: React.FC = () => {
  const navigate = useNavigate();
  const [threads, setThreads] = useState<ForumThread[]>([]);
  const [searchText, setSearchText] = useState("");
  const [category, setCategory] = useState<ThreadCategory>("all");
  const [sortBy, setSortBy] = useState<"latest" | "popular" | "unanswered">(
    "latest"
  );

  useEffect(() => {
    const fetchForumPosts = async () => {
      try {
        const response = await apiClient.get("/forum/posts") as AxiosResponse<any>;
        setThreads(response.data || []);
      } catch (error: any) {
        console.error("Error fetching forum posts:", error);
        toast.error("Không thể tải bài viết diễn đàn");
      }
    };
    
    fetchForumPosts();
  }, []);
  const [onlyPinned, setOnlyPinned] = useState(false);

  const filteredThreads = useMemo(() => {
    return threads
      .filter((thread) => {
        const matchCategory = category === "all" || thread.category === category;
        const matchPinned = !onlyPinned || thread.isPinned;
        const matchSearch =
          thread.title.toLowerCase().includes(searchText.toLowerCase()) ||
          thread.excerpt.toLowerCase().includes(searchText.toLowerCase()) ||
          thread.tags.some((tag) =>
            tag.toLowerCase().includes(searchText.toLowerCase())
          );
        return matchCategory && matchPinned && matchSearch;
      })
      .sort((a, b) => {
        if (sortBy === "latest") {
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        }
        if (sortBy === "popular") {
          return b.likes + b.replies - (a.likes + a.replies);
        }
        return a.replies - b.replies;
      });
  }, [threads, category, sortBy, searchText, onlyPinned]);

  const toggleLike = (threadId: string) => {
    setThreads((prev) =>
      prev.map((thread) => {
        if (thread.id !== threadId) return thread;
        const isLiked = !thread.isLiked;
        return {
          ...thread,
          isLiked,
          likes: isLiked ? thread.likes + 1 : Math.max(thread.likes - 1, 0),
        };
      })
    );
  };

  const categories: { value: ThreadCategory; label: string }[] = [
    { value: "all", label: "Tất cả" },
    { value: "study", label: "Học tập" },
    { value: "exam", label: "Ôn thi" },
    { value: "project", label: "Dự án" },
    { value: "career", label: "Nghề nghiệp" },
    { value: "other", label: "Khác" },
  ];

  const formatDate = (value: string) =>
    new Date(value).toLocaleDateString("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between mb-6">
        <div>
          <p className="text-sm uppercase tracking-wide text-blue-600 font-semibold">
            Cộng đồng học tập
          </p>
          <h1 className="text-3xl font-bold text-gray-900">Diễn đàn học tập</h1>
          <p className="text-gray-500">
            Nơi chia sẻ tài liệu, hỏi đáp và kết nối tutor - student trong hệ thống
          </p>
        </div>
        <button
          onClick={() => navigate("/forum/create")}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-semibold"
        >
          + Tạo chủ đề mới
        </button>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6 space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="relative">
            <input
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              placeholder="Tìm kiếm chủ đề, tag, tác giả..."
              className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <Search className="absolute right-3 top-2.5 h-5 w-5 text-gray-400" />
          </div>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="latest">Mới nhất</option>
            <option value="popular">Nổi bật</option>
            <option value="unanswered">Chưa trả lời</option>
          </select>
        </div>

        <div className="flex flex-wrap gap-2">
          {categories.map((item) => (
            <button
              key={item.value}
              onClick={() => setCategory(item.value)}
              className={`px-4 py-2 rounded-full text-sm font-semibold border transition ${
                category === item.value
                  ? "bg-blue-600 text-white border-blue-600"
                  : "border-gray-300 text-gray-700 hover:bg-gray-100"
              }`}
            >
              {item.label}
            </button>
          ))}
          <label className="flex items-center gap-2 ml-auto text-sm text-gray-600">
            <input
              type="checkbox"
              checked={onlyPinned}
              onChange={(e) => setOnlyPinned(e.target.checked)}
            />
            Chỉ xem chủ đề được ghim
          </label>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {filteredThreads.length === 0 && (
            <div className="text-center py-16 bg-white rounded-lg shadow-md text-gray-500">
              Không tìm thấy chủ đề phù hợp. Hãy thử từ khóa khác nhé!
            </div>
          )}

          {filteredThreads.map((thread) => (
            <article
              key={thread.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition relative"
            >
              {thread.isPinned && (
                <span className="absolute -top-3 right-4 bg-yellow-400 text-white px-3 py-1 rounded-full text-xs font-semibold">
                  Được ghim
                </span>
              )}

              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 mb-3">
                <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-semibold text-xs uppercase">
                  {thread.category}
                </span>
                <span className="inline-flex items-center gap-1">
                  <UserRound className="w-4 h-4" />
                  {thread.author}
                </span>
                <span className="inline-flex items-center gap-1">
                  <CalendarDays className="w-4 h-4" />
                  {formatDate(thread.createdAt)}
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

              <h2
                className="text-xl font-bold text-gray-900 mb-2 cursor-pointer"
                onClick={() => navigate(`/forum/${thread.id}`)}
              >
                {thread.title}
              </h2>
              <p className="text-gray-700 mb-4">{thread.excerpt}</p>

              <div className="flex flex-wrap items-center gap-3">
                <div className="flex gap-2 text-sm">
                  {thread.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
                <div className="flex gap-3 ml-auto text-sm">
                  <button
                    onClick={() => toggleLike(thread.id)}
                    className={`px-4 py-2 rounded-lg border flex items-center gap-2 transition ${
                      thread.isLiked
                        ? "bg-blue-50 border-blue-200 text-blue-700"
                        : "border-gray-200 text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    <ThumbsUp className="w-4 h-4" /> {thread.likes}
                  </button>
                  <button
                    onClick={() => navigate(`/forum/${thread.id}`)}
                    className="px-4 py-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                  >
                    Xem chi tiết
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>

        <aside className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Thống kê nhanh
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div className="p-3 bg-blue-50 rounded-lg">
                <p className="text-gray-600">Chủ đề tuần này</p>
                <p className="text-2xl font-bold text-blue-700">48</p>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <p className="text-gray-600">Tỉ lệ giải đáp</p>
                <p className="text-2xl font-bold text-green-700">86%</p>
              </div>
              <div className="p-3 bg-purple-50 rounded-lg">
                <p className="text-gray-600">Tutor hoạt động</p>
                <p className="text-2xl font-bold text-purple-700">32</p>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg">
                <p className="text-gray-600">Tài liệu chia sẻ</p>
                <p className="text-2xl font-bold text-yellow-700">128</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Tags nổi bật
            </h3>
            <div className="flex flex-wrap gap-2">
              {trendingTags.map((tag) => (
                <button
                  key={tag.label}
                  onClick={() => setSearchText(tag.label)}
                  className="px-3 py-1 rounded-full border border-gray-200 text-sm text-gray-700 hover:bg-gray-50"
                >
                  #{tag.label} ({tag.count})
                </button>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg shadow-md p-6 text-white">
            <h3 className="text-xl font-bold mb-2">Khám phá Study Groups</h3>
            <p className="text-sm text-purple-100 mb-4">
              Tham gia các nhóm học tập đang hoạt động để trao đổi chuyên sâu và luyện thi cùng bạn bè.
            </p>
            <button
              onClick={() => navigate("/study-groups")}
              className="w-full bg-white text-purple-600 font-semibold py-2 rounded-lg hover:bg-purple-50 transition inline-flex items-center justify-center gap-2"
            >
              Đi tới Study Groups
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Thành viên tích cực
            </h3>
            <div className="space-y-4">
              {topContributors.map((user, index) => (
                <div
                  key={user.name}
                  className="flex items-center justify-between p-3 border border-gray-100 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-semibold text-blue-600">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{user.name}</p>
                      <p className="text-sm text-gray-500">{user.role}</p>
                    </div>
                  </div>
                  <span className="font-semibold text-blue-600">{user.points} pts</span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Forum;