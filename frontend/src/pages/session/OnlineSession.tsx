import React, { useState } from "react";

const OnlineSession: React.FC = () => {
  const [isMicOn, setIsMicOn] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    {
      id: "1",
      sender: "Tutor - TS. Nguyễn Văn A",
      message: "Chào mừng các bạn đến với buổi học hôm nay!",
      time: "10:00",
    },
    {
      id: "2",
      sender: "Student - Trần Văn B",
      message: "Chào thầy ạ!",
      time: "10:01",
    },
  ]);
  const [newMessage, setNewMessage] = useState("");

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      setChatMessages([
        ...chatMessages,
        {
          id: Date.now().toString(),
          sender: "You",
          message: newMessage,
          time: new Date().toLocaleTimeString("vi-VN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
        },
      ]);
      setNewMessage("");
    }
  };

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 text-white p-4 flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold">
            Session: Giới thiệu Python cơ bản
          </h1>
          <p className="text-sm text-gray-400">
            Tutor: TS. Nguyễn Văn A • 5 người tham gia
          </p>
        </div>
        <div className="text-lg font-mono">10:35:42</div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Video Area */}
        <div className="flex-1 flex flex-col">
          {/* Main Video */}
          <div className="flex-1 bg-gray-700 relative flex items-center justify-center">
            <div className="text-white text-center">
              <div className="text-6xl mb-4">👨‍🏫</div>
              <p className="text-xl font-semibold">TS. Nguyễn Văn A</p>
              <p className="text-gray-400">Tutor</p>
            </div>
            {isScreenSharing && (
              <div className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-semibold">
                🔴 Đang chia sẻ màn hình
              </div>
            )}
          </div>

          {/* Participants Thumbnails */}
          <div className="bg-gray-800 p-4">
            <div className="flex gap-2 overflow-x-auto">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="bg-gray-700 rounded-lg p-4 min-w-[120px] text-center"
                >
                  <div className="text-2xl mb-1">👤</div>
                  <p className="text-white text-sm">Student {i}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="bg-gray-800 p-4 flex justify-center gap-4">
            <button
              onClick={() => setIsMicOn(!isMicOn)}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                isMicOn
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-red-600 text-white hover:bg-red-700"
              }`}
            >
              {isMicOn ? "🎤 Tắt Mic" : "🔇 Bật Mic"}
            </button>
            <button
              onClick={() => setIsCameraOn(!isCameraOn)}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                isCameraOn
                  ? "bg-blue-600 text-white hover:bg-blue-700"
                  : "bg-red-600 text-white hover:bg-red-700"
              }`}
            >
              {isCameraOn ? "📹 Tắt Camera" : "📷 Bật Camera"}
            </button>
            <button
              onClick={() => setIsScreenSharing(!isScreenSharing)}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                isScreenSharing
                  ? "bg-green-600 text-white hover:bg-green-700"
                  : "bg-gray-600 text-white hover:bg-gray-700"
              }`}
            >
              {isScreenSharing ? "⏹️ Dừng chia sẻ" : "📺 Chia sẻ màn hình"}
            </button>
            <button className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold transition">
              📞 Rời phòng
            </button>
          </div>
        </div>

        {/* Chat Sidebar */}
        <div className="w-80 bg-white flex flex-col border-l border-gray-300">
          <div className="bg-gray-100 p-4 border-b border-gray-300">
            <h3 className="font-bold text-gray-900">Chat</h3>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {chatMessages.map((msg) => (
              <div key={msg.id} className="bg-gray-50 rounded-lg p-3">
                <div className="flex justify-between items-start mb-1">
                  <p className="font-semibold text-sm text-gray-900">
                    {msg.sender}
                  </p>
                  <p className="text-xs text-gray-500">{msg.time}</p>
                </div>
                <p className="text-gray-700">{msg.message}</p>
              </div>
            ))}
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-gray-300">
            <div className="flex gap-2">
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                placeholder="Nhập tin nhắn..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleSendMessage}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Gửi
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnlineSession;
