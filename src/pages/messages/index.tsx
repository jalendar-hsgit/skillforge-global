import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import type { GetServerSideProps } from 'next';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import MessageBubble from '@/components/social/MessageBubble';
import { requireAuthSSR } from '@/lib/auth';

interface Message {
  id: number;
  sender: {
    id: number;
    name: string;
    avatar?: string;
  };
  content: string;
  timestamp: string;
  hasAttachment: boolean;
}

interface Conversation {
  id: number;
  participantId: number;
  participantName: string;
  participantAvatar?: string;
  lastMessage: string;
  unreadCount: number;
  updatedAt: string;
  messages: Message[];
}

export const getServerSideProps: GetServerSideProps = requireAuthSSR();

export default function MessagesPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConv, setSelectedConv] = useState<Conversation | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    fetchConversations();
  }, [isAuthenticated]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError('');
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/messages/conversations`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) throw new Error('Failed to fetch conversations');
      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading messages');
      console.error('Message fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedConv) return;

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiBase}/api/v1x/messages/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          recipientId: selectedConv.participantId,
          content: newMessage
        })
      });

      if (!response.ok) throw new Error('Failed to send message');
      setNewMessage('');
      await fetchConversations();
    } catch (err) {
      console.error('Send message error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">⏳</div>
          <p className="text-gray-600 dark:text-gray-400">Loading messages...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>Messages - SkillForge</title>
        <meta name="description" content="Direct messaging with other users" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-6xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            💌 Messages
          </h1>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-96 md:h-screen">
            {/* Conversations List */}
            <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col">
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <input
                  type="text"
                  placeholder="Search conversations..."
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <div className="flex-1 overflow-y-auto">
                {conversations.length === 0 ? (
                  <div className="p-6 text-center text-gray-600 dark:text-gray-400">
                    No conversations yet
                  </div>
                ) : (
                  conversations.map((conv) => (
                    <button
                      key={conv.id}
                      onClick={() => setSelectedConv(conv)}
                      className={`w-full text-left p-4 border-b border-gray-200 dark:border-gray-700 transition-colors ${
                        selectedConv?.id === conv.id
                          ? 'bg-blue-50 dark:bg-blue-900/20'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                      }`}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <img
                          src={conv.participantAvatar || `https://ui-avatars.com/api/?name=${conv.participantName}&background=random`}
                          alt={conv.participantName}
                          className="w-10 h-10 rounded-full"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 dark:text-white">
                            {conv.participantName}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                            {conv.lastMessage}
                          </p>
                        </div>
                        {conv.unreadCount > 0 && (
                          <span className="bg-blue-600 text-white text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center">
                            {conv.unreadCount}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-gray-500 dark:text-gray-500">
                        {conv.updatedAt}
                      </span>
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Chat Area */}
            <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 flex flex-col">
              {selectedConv ? (
                <>
                  {/* Header */}
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <img
                        src={selectedConv.participantAvatar || `https://ui-avatars.com/api/?name=${selectedConv.participantName}&background=random`}
                        alt={selectedConv.participantName}
                        className="w-10 h-10 rounded-full"
                      />
                      <div>
                        <Link href={`/profile/${selectedConv.participantId}`}>
                          <h2 className="font-semibold text-gray-900 dark:text-white hover:text-blue-600">
                            {selectedConv.participantName}
                          </h2>
                        </Link>
                      </div>
                    </div>
                    <button className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
                      ⋯
                    </button>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 p-4 overflow-y-auto">
                    {selectedConv.messages.length === 0 ? (
                      <div className="text-center text-gray-600 dark:text-gray-400 py-12">
                        Start a conversation by sending a message
                      </div>
                    ) : (
                      selectedConv.messages.map((msg) => (
                        <MessageBubble
                          key={msg.id}
                          id={msg.id}
                          sender={msg.sender}
                          content={msg.content}
                          timestamp={msg.timestamp}
                          isOwn={msg.sender.id === user?.id}
                          hasAttachment={msg.hasAttachment}
                        />
                      ))
                    )}
                  </div>

                  {/* Input */}
                  <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                      <button
                        type="submit"
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors"
                      >
                        Send
                      </button>
                    </div>
                  </form>
                </>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-600 dark:text-gray-400">
                  Select a conversation to start messaging
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
