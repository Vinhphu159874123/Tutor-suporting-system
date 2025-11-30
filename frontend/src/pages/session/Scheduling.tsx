import React, { useEffect, useMemo, useState } from "react";
import SessionBackButton from "./SessionBackButton";
import { useAuthStore } from "../../stores/authStore";
import { schedulingApi } from "../../services/api";
import { toast } from "react-toastify";
import {
  CalendarPlus,
  CalendarRange,
  CalendarClock,
  CalendarDays,
  Search,
  Loader2,
  CalendarX2,
} from "lucide-react";

interface AvailabilitySlot {
  availability_id: number;
  date: string;
  start_time: string;
  end_time: string;
}

interface SlotSuggestion {
  date: string;
  start_time: string;
  end_time: string;
}

const Scheduling: React.FC = () => {
  const { user } = useAuthStore();
  const role = user?.role || "student";
  const isTutor = role === "tutor";
  const isStudent = role === "student";
  const isCoordinator = role === "coordinator";
  const isAdmin = role === "admin";
  const canManageTutorAvailability = isTutor || isCoordinator || isAdmin;
  const canScheduleSessions = isTutor || isCoordinator || isAdmin;
  const canManageExistingSessions = isTutor || isCoordinator || isAdmin;
  const canManageTutorSessionResponses = isTutor;
  const canManageStudentSessionResponses = isStudent;
  const canOrganizeSessions = isCoordinator || isAdmin;
  const defaultTutorId = isTutor && user?.user_id ? String(user.user_id) : "";
  const tutorIdFromProfile = defaultTutorId;

  const [tutorIdInput, setTutorIdInput] = useState<string>(tutorIdFromProfile);
  const [activeTutorId, setActiveTutorId] = useState<string>(tutorIdFromProfile);
  const [availabilitySlots, setAvailabilitySlots] = useState<AvailabilitySlot[]>([]);
  const [availabilityForm, setAvailabilityForm] = useState({
    date: "",
    start_time: "",
    end_time: "",
  });
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(false);
  const [isSavingAvailability, setIsSavingAvailability] = useState(false);
  const [editingAvailabilityId, setEditingAvailabilityId] = useState<number | null>(null);

  const [slotForm, setSlotForm] = useState({
    tutor_id: tutorIdFromProfile,
    start_date: "",
    end_date: "",
    duration_minutes: 60,
  });
  const [isFindingSlots, setIsFindingSlots] = useState(false);
  const [slotResults, setSlotResults] = useState<SlotSuggestion[]>([]);

  const [scheduleForm, setScheduleForm] = useState({
    tutor_id: tutorIdFromProfile,
    student_id: "",
    title: "",
    description: "",
    format: "online",
    duration_minutes: 60,
    scheduled_at: "",
    notes: "",
  });
  const [newSlotDraft, setNewSlotDraft] = useState({
    date: "",
    start_time: "",
    end_time: "",
  });
  const [sessionSlots, setSessionSlots] = useState<
    { date: string; start_time: string; end_time: string }[]
  >([]);
  const [tutorSessions, setTutorSessions] = useState([
    {
      session_id: 401,
      title: "Ôn tập Giải tích",
      proposed_time: "2025-11-22 09:00",
      format: "online",
      location: "Zoom",
      status: "pending",
    },
    {
      session_id: 402,
      title: "Thực hành Python",
      proposed_time: "2025-11-23 14:00",
      format: "in-person",
      location: "Phòng H2-203",
      status: "pending",
    },
  ]);
  const [studentSessions, setStudentSessions] = useState([
    {
      session_id: 601,
      title: "Kèm cặp XSTK",
      proposed_time: "2025-11-25 18:00",
      tutor_name: "TS. Nguyễn Văn A",
      status: "pending",
    },
  ]);
  const [pendingCoordinatorSessions, setPendingCoordinatorSessions] = useState([
    {
      session_id: 701,
      title: "AI Fundamentals",
      tutor_name: "ThS. Phạm Văn C",
      student_name: "SV Trần B",
      ai_score: 0.92,
      availability_hint: "Thứ 5, 9:00-11:00",
    },
  ]);
  const [isScheduling, setIsScheduling] = useState(false);

  const [rescheduleForm, setRescheduleForm] = useState({
    session_id: "",
    new_time: "",
    notes: "",
  });
  const [isRescheduling, setIsRescheduling] = useState(false);
  const [cancelSessionId, setCancelSessionId] = useState("");
  const [isCancelling, setIsCancelling] = useState(false);

  const formattedTutorLabel = useMemo(() => {
    if (isTutor && user?.full_name) {
      return `${user.full_name} (ID ${user.user_id})`;
    }
    if (activeTutorId) {
      return `Tutor ID ${activeTutorId}`;
    }
    return isStudent ? "Chế độ sinh viên" : "Chưa chọn tutor";
  }, [isTutor, isStudent, user, activeTutorId]);

  useEffect(() => {
    if (activeTutorId) {
      fetchAvailability(activeTutorId);
    } else {
      setAvailabilitySlots([]);
    }
  }, [activeTutorId]);

  const handleAddSessionSlot = () => {
    if (!newSlotDraft.date || !newSlotDraft.start_time || !newSlotDraft.end_time) {
      toast.warning("Điền đủ thông tin trước khi thêm khung giờ.");
      return;
    }
    if (newSlotDraft.end_time <= newSlotDraft.start_time) {
      toast.warning("Giờ kết thúc phải lớn hơn giờ bắt đầu.");
      return;
    }
    setSessionSlots((prev) => [...prev, newSlotDraft]);
    setNewSlotDraft({ date: "", start_time: "", end_time: "" });
  };

  const handleRemoveSessionSlot = (index: number) => {
    setSessionSlots((prev) => prev.filter((_, i) => i !== index));
  };

  const fetchAvailability = async (tutorIdValue: string) => {
    setIsLoadingAvailability(true);
    try {
      const response: any = await schedulingApi.getTutorAvailability(tutorIdValue);
      const data = response.data as { availability?: AvailabilitySlot[] };
      setAvailabilitySlots(data.availability || []);
    } catch (error: any) {
      console.error(error);
      toast.error("Không thể tải lịch rảnh. Vui lòng thử lại.");
    } finally {
      setIsLoadingAvailability(false);
    }
  };

  const handleApplyTutor = () => {
    if (!tutorIdInput) {
      toast.warning("Vui lòng nhập tutor ID trước khi tải lịch.");
      return;
    }
    setActiveTutorId(tutorIdInput);
    setScheduleForm((prev) => ({ ...prev, tutor_id: tutorIdInput }));
    setSlotForm((prev) => ({ ...prev, tutor_id: tutorIdInput }));
  };

  const handleAvailabilitySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeTutorId) {
      toast.warning("Hãy chọn gia sư trước khi thiết lập lịch rảnh.");
      return;
    }
    if (!availabilityForm.date || !availabilityForm.start_time || !availabilityForm.end_time) {
      toast.warning("Vui lòng điền đầy đủ thông tin.");
      return;
    }

    const payload = {
      tutor_id: Number(activeTutorId),
      ...availabilityForm,
    };

    setIsSavingAvailability(true);
    try {
      if (editingAvailabilityId) {
        const res: any = await schedulingApi.updateAvailability(editingAvailabilityId, payload);
        const updatedSlot = res.data as AvailabilitySlot;
        setAvailabilitySlots((prev) =>
          prev.map((slot) =>
            slot.availability_id === editingAvailabilityId ? updatedSlot : slot
          )
        );
        toast.success("Đã cập nhật lịch rảnh.");
      } else {
        const res: any = await schedulingApi.createAvailability(payload);
        const newSlot = res.data as AvailabilitySlot;
        setAvailabilitySlots((prev) => [...prev, newSlot]);
        toast.success("Đã thêm lịch rảnh mới.");
      }
      setAvailabilityForm({ date: "", start_time: "", end_time: "" });
      setEditingAvailabilityId(null);
    } catch (error: any) {
      console.error(error);
      toast.error("Lưu lịch rảnh thất bại. Vui lòng thử lại.");
    } finally {
      setIsSavingAvailability(false);
    }
  };

  const handleEditAvailability = (slot: AvailabilitySlot) => {
    setEditingAvailabilityId(slot.availability_id);
    setAvailabilityForm({
      date: slot.date,
      start_time: slot.start_time,
      end_time: slot.end_time,
    });
  };

  const handleDeleteAvailability = async (slotId: number) => {
    if (!window.confirm("Bạn chắc chắn muốn xóa khung giờ này?")) return;
    try {
      await schedulingApi.deleteAvailability(slotId);
      setAvailabilitySlots((prev) =>
        prev.filter((slot) => slot.availability_id !== slotId)
      );
      toast.success("Đã xóa lịch rảnh.");
    } catch (error: any) {
      console.error(error);
      toast.error("Xóa lịch thất bại. Vui lòng thử lại.");
    }
  };

  const handleFindSlots = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!slotForm.tutor_id) {
      toast.warning("Vui lòng nhập tutor ID để tìm slot.");
      return;
    }
    if (!slotForm.start_date || !slotForm.end_date) {
      toast.warning("Chọn khoảng ngày cần tìm.");
      return;
    }
    setIsFindingSlots(true);
    try {
      const res: any = await schedulingApi.findSlots({
        tutor_id: Number(slotForm.tutor_id),
        start_date: slotForm.start_date,
        end_date: slotForm.end_date,
        duration_minutes: Number(slotForm.duration_minutes),
      });
      const data = res.data as { slots?: SlotSuggestion[] };
      setSlotResults(data.slots || []);
      toast.success("Đã tìm thấy các slot khả dụng.");
    } catch (error: any) {
      console.error(error);
      toast.error("Không thể tìm slot phù hợp. Thử lại sau.");
    } finally {
      setIsFindingSlots(false);
    }
  };

  const handleScheduleSession = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!scheduleForm.tutor_id || !scheduleForm.student_id || !scheduleForm.title || !scheduleForm.description) {
      toast.warning("Điền đủ thông tin cơ bản để tạo buổi học.");
      return;
    }
    if (!sessionSlots.length) {
      toast.info("Cần ít nhất một khung giờ. Nếu muốn lưu nháp, hãy dùng nút “Lưu nháp”.");
      return;
    }
    if (!scheduleForm.scheduled_at) {
      toast.warning("Chọn thời gian bắt đầu chính cho phiên học.");
      return;
    }
    setIsScheduling(true);
    try {
      await schedulingApi.scheduleSession({
        tutor_id: Number(scheduleForm.tutor_id),
        student_id: Number(scheduleForm.student_id),
        title: scheduleForm.title,
        description: scheduleForm.description,
        format: scheduleForm.format,
        duration_minutes: scheduleForm.duration_minutes,
        scheduled_at: scheduleForm.scheduled_at,
        time_slots: sessionSlots,
        notes: scheduleForm.notes,
      });
      toast.success("Đã lên lịch phiên học mới.");
      setScheduleForm((prev) => ({
        ...prev,
        title: "",
        description: "",
        scheduled_at: "",
        notes: "",
      }));
      setSessionSlots([]);
    } catch (error: any) {
      console.error(error);
      toast.error("Không thể tạo buổi học. Kiểm tra lại thông tin.");
    } finally {
      setIsScheduling(false);
    }
  };

  const handleSaveDraft = async () => {
    if (!scheduleForm.tutor_id || !scheduleForm.student_id || !scheduleForm.title) {
      toast.warning("Cần ít nhất thông tin gia sư, sinh viên và tiêu đề phiên học để lưu nháp.");
      return;
    }
    setIsScheduling(true);
    try {
      await schedulingApi.scheduleSession({
        tutor_id: Number(scheduleForm.tutor_id),
        student_id: Number(scheduleForm.student_id),
        title: scheduleForm.title,
        description: scheduleForm.description,
        format: scheduleForm.format,
        duration_minutes: scheduleForm.duration_minutes,
        scheduled_at: scheduleForm.scheduled_at || null,
        time_slots: sessionSlots,
        notes: scheduleForm.notes,
        status: "draft",
      });
      toast.success("Đã lưu phiên học ở trạng thái nháp.");
    } catch (error) {
      console.error(error);
      toast.error("Lưu nháp thất bại.");
    } finally {
      setIsScheduling(false);
    }
  };

  const handleTutorDecision = (sessionId: number, decision: "accepted" | "declined") => {
    setTutorSessions((prev) =>
      prev.map((session) =>
        session.session_id === sessionId ? { ...session, status: decision } : session
      )
    );
    toast.success(
      decision === "accepted"
        ? "Bạn đã chấp nhận lịch. Điều phối viên sẽ nhận được thông báo."
        : "Bạn đã từ chối lịch. Điều phối viên sẽ sắp xếp lại."
    );
  };

  const handleStudentDecision = (sessionId: number, decision: "accepted" | "declined") => {
    setStudentSessions((prev) =>
      prev.map((session) =>
        session.session_id === sessionId ? { ...session, status: decision } : session
      )
    );
    toast.success(
      decision === "accepted"
        ? "Bạn đã xác nhận tham gia."
        : "Bạn đã từ chối. Điều phối viên sẽ nhận được thông báo."
    );
  };

  const handleCoordinatorFinalize = (sessionId: number) => {
    setPendingCoordinatorSessions((prev) =>
      prev.filter((session) => session.session_id !== sessionId)
    );
    toast.success("Đã tổ chức xong phiên học và thông báo cho gia sư/sinh viên.");
  };

  const handleCoordinatorRequestMoreInfo = (sessionId: number) => {
    toast.info(`Phiên ${sessionId} đã được đánh dấu cần bổ sung thông tin.`);
  };

  const handleReschedule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rescheduleForm.session_id || !rescheduleForm.new_time) {
      toast.warning("Nhập session ID và thời gian mới để sắp xếp lại lịch.");
      return;
    }
    setIsRescheduling(true);
    try {
      await schedulingApi.rescheduleSession(Number(rescheduleForm.session_id), {
        new_time: rescheduleForm.new_time,
        notes: rescheduleForm.notes,
      });
      toast.success("Đã cập nhật thời gian phiên học.");
      setRescheduleForm({ session_id: "", new_time: "", notes: "" });
    } catch (error: any) {
      console.error(error);
      toast.error("Sắp xếp lại lịch thất bại. Thử lại sau.");
    } finally {
      setIsRescheduling(false);
    }
  };

  const handleCancel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cancelSessionId) {
      toast.warning("Nhập session ID cần hủy.");
      return;
    }
    if (!window.confirm("Bạn chắc chắn muốn hủy phiên học này?")) return;
    setIsCancelling(true);
    try {
      await schedulingApi.cancelSession(Number(cancelSessionId));
      toast.success("Đã hủy phiên học.");
      setCancelSessionId("");
    } catch (error: any) {
      console.error(error);
      toast.error("Hủy phiên thất bại.");
    } finally {
      setIsCancelling(false);
    }
  };

  return (
    <div className="space-y-8">
      <SessionBackButton />

    <div className="card">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-start gap-4">
            <div className="rounded-2xl bg-blue-50 p-3 text-black-600">
              <CalendarDays className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-gray-900 leading-tight">
                Quản lý lịch học
      </h1>
              <p className="text-gray-600 mt-2">
                {isTutor
                  ? "Bạn đang xem lịch của chính mình. Mọi thay đổi sẽ áp dụng ngay."
                  : "Nhập tutor ID để xem lịch rảnh, tìm slot và đặt buổi học."}
              </p>
            </div>
          </div>
          <div className="rounded-2xl border border-blue-100 bg-blue-50 px-6 py-4 text-sm text-black-800">
            <p className="font-semibold text-gray-700">Đang thao tác với:</p>
            <p className="text-base font-semibold text-gray-900">{formattedTutorLabel}</p>
          </div>
        </div>
      </div>

      <div
        className={`grid gap-6 ${
          canManageTutorAvailability ? "lg:grid-cols-2" : "lg:grid-cols-1"
        }`}
      >
        {canManageTutorAvailability && (
          <div className="card space-y-4">
            <div className="flex items-center gap-2 text-gray-900 font-semibold">
              <CalendarPlus className="h-5 w-5" />
              Quản lý lịch rảnh của tutor
            </div>

            {!isTutor && (
              <div className="space-y-2">
                <label
                  htmlFor="manage-tutor-id"
                  className="text-sm font-medium text-gray-700"
                >
                  Tutor ID cần quản lý
                </label>
                <div className="flex gap-3">
                  <input
                    id="manage-tutor-id"
                    type="number"
                    value={tutorIdInput}
                    onChange={(e) => setTutorIdInput(e.target.value)}
                    className="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    placeholder="VD: 12"
                  />
                  <button
                    onClick={handleApplyTutor}
                    className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 transition"
                  >
                    Tải lịch
                  </button>
                </div>
                <p className="text-xs text-gray-500">
                  Điều phối viên có thể thay đổi tutor ID để thiết lập lịch giúp tutor.
                </p>
              </div>
            )}

            {isTutor && (
              <div className="text-sm text-gray-600 bg-blue-50 border border-blue-100 rounded-lg px-3 py-2">
                Bạn đang cập nhật lịch của chính mình (ID {user?.user_id}). Mọi thay đổi sẽ áp dụng ngay.
              </div>
            )}

            <form onSubmit={handleAvailabilitySubmit} className="grid gap-4 md:grid-cols-3">
              <div className="flex flex-col gap-2">
                <label
                  htmlFor="availability-date"
                  className="text-sm font-medium text-gray-700"
                >
                  Ngày
                </label>
                <input
                  id="availability-date"
                  type="date"
                  value={availabilityForm.date}
                  onChange={(e) =>
                    setAvailabilityForm((prev) => ({ ...prev, date: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label
                  htmlFor="availability-start"
                  className="text-sm font-medium text-gray-700"
                >
                  Từ
                </label>
                <input
                  id="availability-start"
                  type="time"
                  value={availabilityForm.start_time}
                  onChange={(e) =>
                    setAvailabilityForm((prev) => ({ ...prev, start_time: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label
                  htmlFor="availability-end"
                  className="text-sm font-medium text-gray-700"
                >
                  Đến
                </label>
                <input
                  id="availability-end"
                  type="time"
                  value={availabilityForm.end_time}
                  onChange={(e) =>
                    setAvailabilityForm((prev) => ({ ...prev, end_time: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="md:col-span-3 flex gap-3">
                <button
                  type="submit"
                  className="flex-1 rounded-lg bg-green-600 px-4 py-2 text-white font-semibold hover:bg-green-700 transition inline-flex items-center justify-center gap-2"
                  disabled={isSavingAvailability}
                >
                  {isSavingAvailability && <Loader2 className="h-4 w-4 animate-spin" />}
                  {editingAvailabilityId ? "Lưu thay đổi" : "Thêm lịch rảnh"}
                </button>
                {editingAvailabilityId && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingAvailabilityId(null);
                      setAvailabilityForm({ date: "", start_time: "", end_time: "" });
                    }}
                    className="rounded-lg border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 transition"
                  >
                    Hủy
                  </button>
                )}
              </div>
            </form>

            <div className="border-t pt-4">
              <p className="text-sm font-medium text-gray-700 mb-3">Danh sách khung giờ</p>
              {isLoadingAvailability ? (
                <div className="flex items-center gap-2 text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Đang tải...
                </div>
              ) : availabilitySlots.length ? (
                <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                  {availabilitySlots.map((slot) => (
                    <div
                      key={slot.availability_id}
                      className="rounded-xl border border-gray-200 px-4 py-3 flex items-center justify-between"
                    >
                      <div>
                        <p className="font-semibold text-gray-900">{slot.date}</p>
                        <p className="text-sm text-gray-600">
                          {slot.start_time} - {slot.end_time}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          className="text-blue-600 text-sm font-semibold hover:text-black-700"
                          onClick={() => handleEditAvailability(slot)}
                        >
                          Sửa
                        </button>
                        <button
                          className="text-red-600 text-sm font-semibold hover:text-black-700"
                          onClick={() => handleDeleteAvailability(slot.availability_id)}
                        >
                          Xóa
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">Chưa có khung giờ nào.</p>
              )}
            </div>
          </div>
        )}

        <div className="card space-y-5">
          <div className="flex items-center gap-2 text-gray-900 font-semibold">
            <Search className="h-5 w-5" />
            Tìm slot phù hợp
          </div>
          <p className="text-sm text-gray-600">
            {isStudent
              ? "Sinh viên dùng tính năng này để đề xuất thời gian khác trước khi gửi cho tutor."
              : "Hỗ trợ tutor/điều phối viên rà soát nhanh các slot trống đáp ứng tiêu chí."}
          </p>
          <form onSubmit={handleFindSlots} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
              <label
                htmlFor="slot-tutor-id"
                className="text-sm font-medium text-gray-700"
              >
                Tutor ID
              </label>
                <input
                id="slot-tutor-id"
                  type="number"
                  value={slotForm.tutor_id}
                  onChange={(e) =>
                    setSlotForm((prev) => ({ ...prev, tutor_id: e.target.value }))
                  }
                  disabled={isTutor}
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-100 disabled:text-gray-500"
                  placeholder="ID tutor"
                />
                {isTutor && (
                  <p className="text-xs text-gray-500">Tự động dùng ID của bạn.</p>
                )}
              </div>
              <div className="flex flex-col gap-2">
              <label
                htmlFor="slot-duration"
                className="text-sm font-medium text-gray-700"
              >
                Thời lượng (phút)
              </label>
                <input
                id="slot-duration"
                  type="number"
                  min={30}
                  step={15}
                  value={slotForm.duration_minutes}
                  onChange={(e) =>
                    setSlotForm((prev) => ({
                      ...prev,
                      duration_minutes: Number(e.target.value),
                    }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
              <label
                htmlFor="slot-start-date"
                className="text-sm font-medium text-gray-700"
              >
                Từ ngày
              </label>
                <input
                id="slot-start-date"
                  type="date"
                  value={slotForm.start_date}
                  onChange={(e) =>
                    setSlotForm((prev) => ({ ...prev, start_date: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex flex-col gap-2">
              <label
                htmlFor="slot-end-date"
                className="text-sm font-medium text-gray-700"
              >
                Đến ngày
              </label>
                <input
                id="slot-end-date"
                  type="date"
                  value={slotForm.end_date}
                  onChange={(e) =>
                    setSlotForm((prev) => ({ ...prev, end_date: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </div>
            <button
              type="submit"
              className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white font-semibold hover:bg-indigo-700 transition inline-flex items-center justify-center gap-2"
              disabled={isFindingSlots}
            >
              {isFindingSlots && <Loader2 className="h-4 w-4 animate-spin" />}
              Tìm slot trống
            </button>
          </form>

          <div className="border-t pt-4">
            <p className="text-sm font-medium text-gray-700 mb-3">Gợi ý slot</p>
            {slotResults.length ? (
              <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                {slotResults.map((slot, index) => (
                  <div
                    key={`${slot.date}-${slot.start_time}-${index}`}
                    className="rounded-xl border border-gray-200 px-4 py-3"
                  >
                    <p className="font-semibold text-gray-900">{slot.date}</p>
                    <p className="text-sm text-gray-600">
                      {slot.start_time} - {slot.end_time}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                Điền thông tin để xem các slot khả dụng.
              </p>
            )}
          </div>
        </div>
      </div>

      <div
        className={`grid gap-6 ${
          canScheduleSessions && canManageExistingSessions
            ? "lg:grid-cols-2"
            : "lg:grid-cols-1"
        }`}
      >
        {canScheduleSessions && (
          <div className="card space-y-4">
            <div className="flex items-center gap-2 text-gray-900 font-semibold">
              <CalendarClock className="h-5 w-5" />
              Tạo phiên học mới
            </div>
            <p className="text-sm text-gray-600">
              Điền thông tin cơ bản, thêm khung giờ bắt buộc và xác nhận.
            </p>
            <form onSubmit={handleScheduleSession} className="space-y-4">
              <div className="grid gap-3 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-tutor-id"
                    className="text-sm font-medium text-gray-700"
                  >
                    Tutor ID
                  </label>
                  <input
                    id="schedule-tutor-id"
                    type="number"
                    value={scheduleForm.tutor_id}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({ ...prev, tutor_id: e.target.value }))
                    }
                    disabled={isTutor}
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500 disabled:bg-gray-100 disabled:text-gray-500"
                  />
                  {isTutor && (
                    <p className="text-xs text-gray-500">
                      Tự động dùng ID của bạn.
                    </p>
                  )}
                </div>
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-student-id"
                    className="text-sm font-medium text-gray-700"
                  >
                    Student ID
                  </label>
                  <input
                    id="schedule-student-id"
                    type="number"
                    value={scheduleForm.student_id}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({ ...prev, student_id: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-title"
                    className="text-sm font-medium text-gray-700"
                  >
                    Tiêu đề
                  </label>
                  <input
                    id="schedule-title"
                    type="text"
                    value={scheduleForm.title}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({ ...prev, title: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                    placeholder="VD: Ôn tập Giải tích"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-format"
                    className="text-sm font-medium text-gray-700"
                  >
                    Hình thức
                  </label>
                  <select
                    id="schedule-format"
                    value={scheduleForm.format}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({ ...prev, format: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="online">Online</option>
                    <option value="in-person">In-person</option>
                  </select>
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <label
                  htmlFor="schedule-description"
                  className="text-sm font-medium text-gray-700"
                >
                  Mô tả ngắn
                </label>
                <textarea
                  id="schedule-description"
                  rows={3}
                  value={scheduleForm.description}
                  onChange={(e) =>
                    setScheduleForm((prev) => ({ ...prev, description: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  placeholder="Mục tiêu, nội dung chính..."
                />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-duration"
                    className="text-sm font-medium text-gray-700"
                  >
                    Thời lượng (phút)
                  </label>
                  <input
                    id="schedule-duration"
                    type="number"
                    min={30}
                    step={15}
                    value={scheduleForm.duration_minutes}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({
                        ...prev,
                        duration_minutes: Number(e.target.value),
                      }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="schedule-start-time"
                    className="text-sm font-medium text-gray-700"
                  >
                    Thời gian bắt đầu chính
                  </label>
                  <input
                    id="schedule-start-time"
                    type="datetime-local"
                    value={scheduleForm.scheduled_at}
                    onChange={(e) =>
                      setScheduleForm((prev) => ({ ...prev, scheduled_at: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div className="space-y-3 rounded-xl border border-dashed border-emerald-200 bg-emerald-50/60 p-4">
                <p className="text-sm font-semibold text-black-700">
                  Bước 3: Thêm các khung giờ khả dụng
                </p>
                <div className="grid gap-3 md:grid-cols-3">
                  <div className="flex flex-col gap-2">
                    <label
                      htmlFor="slot-draft-date"
                      className="text-xs font-medium text-gray-600"
                    >
                      Ngày
                    </label>
                    <input
                      id="slot-draft-date"
                      type="date"
                      value={newSlotDraft.date}
                      onChange={(e) =>
                        setNewSlotDraft((prev) => ({ ...prev, date: e.target.value }))
                      }
                      className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label
                      htmlFor="slot-draft-start"
                      className="text-xs font-medium text-gray-600"
                    >
                      Từ
                    </label>
                    <input
                      id="slot-draft-start"
                      type="time"
                      value={newSlotDraft.start_time}
                      onChange={(e) =>
                        setNewSlotDraft((prev) => ({ ...prev, start_time: e.target.value }))
                      }
                      className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                  <div className="flex flex-col gap-2">
                    <label
                      htmlFor="slot-draft-end"
                      className="text-xs font-medium text-gray-600"
                    >
                      Đến
                    </label>
                    <input
                      id="slot-draft-end"
                      type="time"
                      value={newSlotDraft.end_time}
                      onChange={(e) =>
                        setNewSlotDraft((prev) => ({ ...prev, end_time: e.target.value }))
                      }
                      className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleAddSessionSlot}
                  className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-white text-sm font-semibold hover:bg-emerald-700 transition"
                >
                  Thêm slot
                </button>
                {sessionSlots.length > 0 ? (
                  <div className="space-y-2">
                    {sessionSlots.map((slot, idx) => (
                      <div
                        key={`${slot.date}-${slot.start_time}-${idx}`}
                        className="flex items-center justify-between rounded-lg border border-white/70 bg-white px-4 py-2"
                      >
                        <span className="text-sm text-gray-700">
                          {slot.date} • {slot.start_time} - {slot.end_time}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleRemoveSessionSlot(idx)}
                          className="text-xs font-semibold text-red-600 hover:text-red-700"
                        >
                          Xóa
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500">
                    Chưa có slot nào. Bạn cần ít nhất 1 slot để hoàn tất hoặc lưu nháp nếu chưa sẵn sàng.
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-2">
                <label
                  htmlFor="schedule-notes"
                  className="text-sm font-medium text-gray-700"
                >
                  Ghi chú (tuỳ chọn)
                </label>
                <textarea
                  id="schedule-notes"
                  rows={3}
                  value={scheduleForm.notes}
                  onChange={(e) =>
                    setScheduleForm((prev) => ({ ...prev, notes: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-emerald-500"
                  placeholder="Link Zoom, dụng cụ cần chuẩn bị..."
                />
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <button
                  type="button"
                  onClick={handleSaveDraft}
                  className="rounded-lg border border-emerald-200 px-4 py-2 font-semibold text-emerald-600 hover:bg-emerald-50 transition"
                  disabled={isScheduling}
                >
                  Lưu nháp
                </button>
                <button
                  type="submit"
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-white font-semibold hover:bg-emerald-700 transition inline-flex items-center justify-center gap-2"
                  disabled={isScheduling}
                >
                  {isScheduling && <Loader2 className="h-4 w-4 animate-spin" />}
                  Tạo phiên học
                </button>
              </div>
            </form>
          </div>
        )}

        {canManageExistingSessions && (
          <div className="card space-y-6">
            <div className="flex items-center gap-2 text-gray-900 font-semibold">
              <CalendarRange className="h-5 w-5" />
              Cập nhật / hủy phiên đã có
            </div>

            <form onSubmit={handleReschedule} className="space-y-3">
              <div className="grid gap-3 md:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="reschedule-session-id"
                    className="text-sm font-medium text-gray-700"
                  >
                    Session ID
                  </label>
                  <input
                    id="reschedule-session-id"
                    type="number"
                    value={rescheduleForm.session_id}
                    onChange={(e) =>
                      setRescheduleForm((prev) => ({ ...prev, session_id: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-orange-500"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <label
                    htmlFor="reschedule-new-time"
                    className="text-sm font-medium text-gray-700"
                  >
                    Thời gian mới
                  </label>
                  <input
                    id="reschedule-new-time"
                    type="datetime-local"
                    value={rescheduleForm.new_time}
                    onChange={(e) =>
                      setRescheduleForm((prev) => ({ ...prev, new_time: e.target.value }))
                    }
                    className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-orange-500"
                  />
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <label
                  htmlFor="reschedule-notes"
                  className="text-sm font-medium text-gray-700"
                >
                  Ghi chú (tuỳ chọn)
                </label>
                <textarea
                  id="reschedule-notes"
                  rows={2}
                  value={rescheduleForm.notes}
                  onChange={(e) =>
                    setRescheduleForm((prev) => ({ ...prev, notes: e.target.value }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-orange-500"
                  placeholder="Lý do hoặc lưu ý thêm"
                />
              </div>
              <button
                type="submit"
                className="w-full rounded-lg bg-orange-600 px-4 py-2 text-white font-semibold hover:bg-orange-700 transition inline-flex items-center justify-center gap-2"
                disabled={isRescheduling}
              >
                {isRescheduling && <Loader2 className="h-4 w-4 animate-spin" />}
                Reschedule phiên
              </button>
            </form>

            <div className="border-t pt-4 space-y-3">
              <div className="flex items-center gap-2 text-red-600 font-semibold">
                <CalendarX2 className="h-5 w-5" />
                Hủy phiên học
              </div>
              <form onSubmit={handleCancel} className="flex gap-3">
                <input
                  id="cancel-session-id"
                  type="number"
                  value={cancelSessionId}
                  onChange={(e) => setCancelSessionId(e.target.value)}
                  className="flex-1 rounded-lg border border-gray-300 px-3 py-2 focus:ring-2 focus:ring-red-500"
                  placeholder="Session ID"
                />
                <button
                  type="submit"
                  className="rounded-lg bg-red-600 px-4 py-2 text-white font-semibold hover:bg-red-700 transition inline-flex items-center gap-2"
                  disabled={isCancelling}
                >
                  {isCancelling && <Loader2 className="h-4 w-4 animate-spin" />}
                  Hủy
                </button>
              </form>
            </div>
          </div>
        )}
      </div>

      {canManageTutorSessionResponses && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2 text-black-700 font-semibold">
            <CalendarRange className="h-5 w-5" />
            Quản lý phiên học
          </div>
          <p className="text-sm text-gray-600">
            Danh sách phiên học phù hợp với bạn
          </p>
          <div className="space-y-3">
            {tutorSessions.map((session) => (
              <div
                key={session.session_id}
                className="rounded-xl border border-gray-200 px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <p className="font-semibold text-gray-900">
                    #{session.session_id} • {session.title}
                  </p>
                  <p className="text-sm text-gray-600">
                    {session.proposed_time} • {session.format === "online" ? "Online" : "Trực tiếp"} ({session.location})
                  </p>
                  <p className="text-xs uppercase text-gray-500">Trạng thái: {session.status}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleTutorDecision(session.session_id, "accepted")}
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-white text-sm font-semibold hover:bg-emerald-700 transition"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleTutorDecision(session.session_id, "declined")}
                    className="rounded-lg bg-red-50 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-100 transition"
                  >
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {canManageStudentSessionResponses && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2 text-black-700 font-semibold">
            <CalendarRange className="h-5 w-5" />
            Quản lý phiên học của sinh viên
          </div>
          <p className="text-sm text-gray-600">
            Xem chi tiết từng phiên học
          </p>
          <div className="space-y-3">
            {studentSessions.map((session) => (
              <div
                key={session.session_id}
                className="rounded-xl border border-gray-200 px-4 py-3 flex flex-col gap-2 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <p className="font-semibold text-gray-900">
                    #{session.session_id} • {session.title}
                  </p>
                  <p className="text-sm text-gray-600">
                    {session.proposed_time} • Tutor: {session.tutor_name}
                  </p>
                  <p className="text-xs uppercase text-gray-500">Trạng thái: {session.status}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleStudentDecision(session.session_id, "accepted")}
                    className="rounded-lg bg-emerald-600 px-4 py-2 text-white text-sm font-semibold hover:bg-emerald-700 transition"
                  >
                    Accept
                  </button>
                  <button
                    onClick={() => handleStudentDecision(session.session_id, "declined")}
                    className="rounded-lg bg-red-50 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-100 transition"
                  >
                    Decline
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {canOrganizeSessions && (
        <div className="card space-y-4">
          <div className="flex items-center gap-2 text-black-700 font-semibold">
            <CalendarClock className="h-5 w-5" />
            Điều phối phiên học (Organize session)
          </div>
          <p className="text-sm text-gray-600">
            Dữ liệu mô phỏng từ HCMUT_DATACORE / AI_RECOMMENDER. Điều phối viên duyệt đề xuất và hoàn tất session.
          </p>
          <div className="space-y-3">
            {pendingCoordinatorSessions.map((session) => (
              <div
                key={session.session_id}
                className="rounded-xl border border-gray-200 px-4 py-3 flex flex-col gap-3"
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                  <div>
                    <p className="font-semibold text-gray-900">
                      #{session.session_id} • {session.title}
                    </p>
                    <p className="text-sm text-gray-600">
                      Tutor: {session.tutor_name} • Student: {session.student_name}
                    </p>
                  </div>
                  <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-600">
                    Gợi ý AI: {(session.ai_score * 100).toFixed(0)}% phù hợp
                  </span>
                </div>
                <p className="text-sm text-gray-600">
                  Khung giờ khả dụng: {session.availability_hint}
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleCoordinatorFinalize(session.session_id)}
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-white text-sm font-semibold hover:bg-indigo-700 transition"
                  >
                    Finalize & Notify
                  </button>
                  <button
                    onClick={() => handleCoordinatorRequestMoreInfo(session.session_id)}
                    className="rounded-lg border border-indigo-200 px-4 py-2 text-sm font-semibold text-indigo-600 hover:bg-indigo-50 transition"
                  >
                    Yêu cầu thêm thông tin
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Scheduling;