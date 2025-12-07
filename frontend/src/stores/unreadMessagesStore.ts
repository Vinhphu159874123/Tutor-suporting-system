import { create } from 'zustand';

interface UnreadMessagesState {
  unreadCounts: Record<number, number>; // groupId -> unread count
  setUnreadCount: (groupId: number, count: number) => void;
  incrementUnread: (groupId: number) => void;
  clearUnread: (groupId: number) => void;
  getTotalUnread: () => number;
}

export const useUnreadMessagesStore = create<UnreadMessagesState>((set, get) => ({
  unreadCounts: {},
  
  setUnreadCount: (groupId, count) => 
    set((state) => ({
      unreadCounts: { ...state.unreadCounts, [groupId]: count }
    })),
  
  incrementUnread: (groupId) =>
    set((state) => ({
      unreadCounts: {
        ...state.unreadCounts,
        [groupId]: (state.unreadCounts[groupId] || 0) + 1
      }
    })),
  
  clearUnread: (groupId) =>
    set((state) => ({
      unreadCounts: { ...state.unreadCounts, [groupId]: 0 }
    })),
  
  getTotalUnread: () => {
    const state = get();
    return Object.values(state.unreadCounts).reduce((sum, count) => sum + count, 0);
  }
}));
