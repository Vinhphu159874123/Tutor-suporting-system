import React from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import {
  ClipboardList,
  FileText,
  CalendarClock,
  UploadCloud,
  BookOpen,
  Monitor,
  TrendingUp,
  CalendarCheck2,
} from "lucide-react";

type SessionGroupItem = {
  key: string;
  title: string;
  description: string;
  actionText: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles?: string[];
};

type SessionGroup = {
  title: string;
  items: SessionGroupItem[];
};

const sessionGroups: SessionGroup[] = [
  {
    title: "Quản lý phiên học",
    items: [
      {
        key: "history",
        title: "Danh sách & lịch sử phiên học",
        description:
          "Theo dõi mọi buổi học bạn đã đăng ký, xem trạng thái và mở nhanh chi tiết từng phiên.",
        actionText: "Xem danh sách",
        href: "/history",
        icon: ClipboardList,
      },
      {
        key: "detail",
        title: "Chi tiết phiên học",
        description:
          "Xem mục tiêu, tài liệu đính kèm và thành viên của một phiên cụ thể. Chọn phiên từ danh sách rồi mở chi tiết.",
        actionText: "Thông tin phiên học",
        href: "/sessions/demo",
        icon: FileText,
      },
      {
        key: "scheduling",
        title: "Quản lý lịch học",
        description:
          "Đề xuất thời gian mới, xác nhận lịch và nhận thông báo khi có thay đổi từ gia sư.",
        actionText: "Quản lý lịch học",
        href: "/scheduling",
        icon: CalendarClock,
      },
    ],
  },
  {
    title: "Tài liệu & lớp học online",
    items: [
      {
        key: "upload",
        title: "Tải tài liệu",
        description:
          "Gia sư có thể chuẩn bị giáo án, slide, bài tập và chia sẻ cho lớp chỉ sau vài giây.",
        actionText: "Tải tài liệu",
        href: "/upload-materials",
        icon: UploadCloud,
        roles: ["tutor", "coordinator", "admin"],
      },
      {
        key: "materials",
        title: "Danh sách tài liệu",
        description:
          "Sinh viên tải nhanh tài liệu, bài tập và ghi chú sau mỗi phiên học.",
        actionText: "Xem tài liệu",
        href: "/materials",
        icon: BookOpen,
      },
      {
        key: "online",
        title: "Tham gia session online",
        description:
          "Phòng học trực tuyến với mic, camera và chat nhóm như lớp học thật.",
        actionText: "Tham gia phòng học",
        href: "/online-session/demo",
        icon: Monitor,
      },
    ],
  },
  {
    title: "Theo dõi tiến độ",
    items: [
      {
        key: "progress",
        title: "Tiến trình học",
        description:
          "Nhìn tổng quan mức độ hoàn thành, kỹ năng đạt được và mục tiêu kế tiếp của bạn.",
        actionText: "Mở bảng tiến độ",
        href: "/learning-progress",
        icon: TrendingUp,
      },
    ],
  },
];

const Sessions: React.FC = () => {
  const { user } = useAuthStore();
  const role = user?.role || "";

  return (
    <div className="space-y-10">
      <div className="card">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            <div className="rounded-2xl bg-blue-50 p-3 text-blue-600">
              <CalendarCheck2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-blue-600 font-semibold">
                Session hub
              </p>
              <h1 className="mt-1 text-3xl font-black text-gray-900 leading-tight">
                Quản lý phiên học
              </h1>
            </div>
          </div>
        </div>
      </div>

      {sessionGroups.map((group) => (
        <div key={group.title} className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">{group.title}</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {group.items
              .filter((item) => !item.roles || item.roles.includes(role))
              .map((item) => (
                <div
                  key={item.key}
                  className="card h-full flex flex-col border border-gray-100 hover:border-blue-200 transition"
                >
                  <div className="flex items-center justify-center h-12 w-12 rounded-2xl bg-blue-50 text-blue-600 mb-4">
                    <item.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {item.title}
                  </h3>
                  <p className="text-gray-600 mt-2 flex-1">
                    {item.description}
                  </p>
                  <Link
                    to={item.href}
                    className="mt-6 inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition"
                  >
                    {item.actionText}
                  </Link>
                </div>
              ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Sessions;