import React, { useState, useEffect, useRef } from 'react';
import { Send, Trash2, MessageCircle } from 'lucide-react';
import { studyGroupsApi } from '../services/api';
import { toast } from 'react-toastify';
import { useAuthStore } from '../stores/authStore';
import { useWebSocketContext } from '../contexts/WebSocketContext';
import { useUnreadMessagesStore } from '../stores/unreadMessagesStore';

interface Message {
  message_id: number;
  user_id: number;
  user_name: string;
  message_text: string;
  created_at: string;
  is_deleted: boolean;
}

interface ChatBoxProps {
  groupId: number;
}

const ChatBox: React.FC<ChatBoxProps> = ({ groupId }) => {
  const { user } = useAuthStore();
  const { clearUnread } = useUnreadMessagesStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [newMessageCount, setNewMessageCount] = useState(0);
  const [showNewMessageNotif, setShowNewMessageNotif] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const prevMessagesLengthRef = useRef(0);
  const isInitialLoadRef = useRef(true);
  
  // WebSocket connection from context
  const { isConnected, sendMessage: sendWsMessage, subscribe } = useWebSocketContext();

  useEffect(() => {
    loadMessages();
    // Clear unread count when viewing this chat
    clearUnread(groupId);
  }, [groupId, clearUnread]);

  // Subscribe to WebSocket messages
  useEffect(() => {
    const unsubscribe = subscribe((message) => {
      console.log('WebSocket message received:', message);
      
      if (message.type === 'new_message') {
        const chatMessage = message.data;
        
        // Only process messages for this group
        if (chatMessage.group_id === groupId) {
          // Add message to the list if it doesn't already exist
          setMessages((prev) => {
            const exists = prev.some(m => m.message_id === chatMessage.message_id);
            if (exists) return prev;
            
            const newMsg: Message = {
              message_id: chatMessage.message_id,
              user_id: chatMessage.user_id,
              user_name: chatMessage.user_name,
              message_text: chatMessage.message_text,
              created_at: chatMessage.created_at,
              is_deleted: false,
            };
            
            return [...prev, newMsg];
          });
        }
      }
      
      // Handle user online/offline status
      if (message.type === 'user_status') {
        const statusData = message.data;
        if (statusData.group_id === groupId) {
          setOnlineUsers((prev) => {
            const newSet = new Set(prev);
            if (statusData.is_online) {
              newSet.add(statusData.user_id);
            } else {
              newSet.delete(statusData.user_id);
            }
            return newSet;
          });
        }
      }
    });

    return unsubscribe;
  }, [groupId, subscribe]);

  useEffect(() => {
    // Skip notification on initial load
    if (isInitialLoadRef.current && messages.length > 0) {
      prevMessagesLengthRef.current = messages.length;
      isInitialLoadRef.current = false;
      scrollToBottom();
      return;
    }

    // Check for new messages
    if (messages.length > prevMessagesLengthRef.current && !isInitialLoadRef.current) {
      const newCount = messages.length - prevMessagesLengthRef.current;
      
      console.log('New messages detected:', newCount, 'shouldAutoScroll:', shouldAutoScroll);
      
      // If not at bottom, show notification
      if (!shouldAutoScroll) {
        setNewMessageCount(prev => prev + newCount);
        setShowNewMessageNotif(true);
        console.log('Showing notification for', newCount, 'new messages');
        
        // Auto hide notification after 5 seconds
        setTimeout(() => setShowNewMessageNotif(false), 5000);
      } else {
        // If at bottom, auto scroll
        scrollToBottom();
      }
    }
    prevMessagesLengthRef.current = messages.length;
  }, [messages, shouldAutoScroll]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;
      // Consider "near bottom" if within 100px
      const isNearBottom = distanceFromBottom < 100;
      setShouldAutoScroll(isNearBottom);
      
      // Clear notification when scrolling to bottom
      if (isNearBottom) {
        setNewMessageCount(0);
        setShowNewMessageNotif(false);
      }
    }
  };

  const scrollToBottomAndClearNotif = () => {
    scrollToBottom();
    setNewMessageCount(0);
    setShowNewMessageNotif(false);
  };

  const loadMessages = async () => {
    try {
      const response: any = await studyGroupsApi.getMessages(groupId, 50);
      setMessages(response.data || response || []);
    } catch (error) {
      // Silent fail - don't show error toast on auto-refresh
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;
    
    try {
      setSending(true);
      
      // Send via WebSocket if connected, otherwise fallback to HTTP
      if (isConnected) {
        sendWsMessage('chat_message', {
          group_id: groupId,
          message_text: newMessage.trim(),
        });
        setNewMessage('');
        setShouldAutoScroll(true); // Force scroll on send
      } else {
        // Fallback to HTTP API
        await studyGroupsApi.sendMessage(groupId, newMessage.trim());
        setNewMessage('');
        setShouldAutoScroll(true); // Force scroll on send
        await loadMessages(); // Reload to get new message
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể gửi tin nhắn');
    } finally {
      setSending(false);
    }
  };

  const deleteMessage = async (messageId: number) => {
    if (!window.confirm('Bạn có chắc muốn xóa tin nhắn này?')) return;
    
    try {
      await studyGroupsApi.deleteMessage(groupId, messageId);
      await loadMessages();
      toast.success('Đã xóa tin nhắn');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xóa tin nhắn');
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (hours < 24) {
      return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' }) + ' ' +
           date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="bg-white rounded-lg shadow-md flex flex-col h-[600px] relative">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-3 rounded-t-lg flex items-center">
        <MessageCircle size={20} className="mr-2" />
        <h3 className="font-semibold">Chat Nhóm</h3>
        <span className="ml-auto text-sm opacity-90 flex items-center gap-2">
          {messages.length} tin nhắn
          {isConnected ? (
            <span className="inline-flex items-center gap-1 bg-green-500 px-2 py-0.5 rounded-full text-xs">
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
              Live
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 bg-yellow-500 px-2 py-0.5 rounded-full text-xs">
              <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
              Offline
            </span>
          )}
        </span>
      </div>

      {/* New Message Notification */}
      {showNewMessageNotif && newMessageCount > 0 && (
        <div 
          onClick={scrollToBottomAndClearNotif}
          className="absolute top-16 left-1/2 transform -translate-x-1/2 z-10 bg-blue-600 text-white px-4 py-2 rounded-full shadow-lg cursor-pointer hover:bg-blue-700 transition-all animate-bounce flex items-center gap-2"
        >
          <MessageCircle size={16} />
          <span className="font-medium">
            {newMessageCount} tin nhắn mới
          </span>
        </div>
      )}

      {/* Messages */}
      <div 
        ref={chatContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
      >
        {loading && messages.length === 0 ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <MessageCircle size={48} className="mb-2 opacity-50" />
            <p>Chưa có tin nhắn nào</p>
            <p className="text-sm">Hãy bắt đầu cuộc trò chuyện!</p>
          </div>
        ) : (
          messages.map((message) => {
            const isMyMessage = message.user_id === user?.user_id;
            
            return (
              <div
                key={message.message_id}
                className={`flex ${isMyMessage ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[70%] ${isMyMessage ? 'items-end' : 'items-start'} flex flex-col`}>
                  {!isMyMessage && (
                    <span className="text-xs text-gray-600 font-medium mb-1 px-2 flex items-center gap-1">
                      {message.user_name}
                      {onlineUsers.has(message.user_id) && (
                        <span className="w-2 h-2 bg-green-500 rounded-full inline-block" title="Online"></span>
                      )}
                    </span>
                  )}
                  <div className="flex items-end gap-2">
                    {isMyMessage && (
                      <button
                        onClick={() => deleteMessage(message.message_id)}
                        className="text-gray-400 hover:text-red-500 transition-colors mb-1"
                        title="Xóa tin nhắn"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                    <div
                      className={`px-4 py-2 rounded-2xl ${
                        isMyMessage
                          ? 'bg-blue-600 text-white rounded-br-md'
                          : 'bg-white text-gray-800 rounded-bl-md shadow-sm'
                      }`}
                    >
                      <p className="break-words whitespace-pre-wrap">{message.message_text}</p>
                    </div>
                  </div>
                  <span className={`text-xs text-gray-500 mt-1 px-2`}>
                    {formatTime(message.created_at)}
                  </span>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="p-4 bg-white border-t border-gray-200 rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Nhập tin nhắn..."
            disabled={sending}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            maxLength={500}
          />
          <button
            type="submit"
            disabled={sending || !newMessage.trim()}
            className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {newMessage.length}/500 ký tự
        </p>
      </form>
    </div>
  );
};

export default ChatBox;
