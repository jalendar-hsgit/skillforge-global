import { useState, useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { Card } from './Card';
import { Button } from './Button';
import { Input } from './Input';
import VideoCall from './VideoCall';

interface Message {
  id: number;
  sender_id: number;
  content: string;
  created_at: string;
}

interface MentorChatProps {
  sessionId: number;
  currentUserId: number;
  otherUserId: number;
  token: string;
}

export default function MentorChat({ sessionId, currentUserId, otherUserId, token }: MentorChatProps) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [otherUserTyping, setOtherUserTyping] = useState(false);
  const [inCall, setInCall] = useState(false);
  const [incomingCall, setIncomingCall] = useState(false);
  const [callerId, setCallerId] = useState<number | null>(null);
  const [callType, setCallType] = useState<'video' | 'audio'>('video');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io('http://localhost:8001/ws', {
      auth: { token },
      transports: ['websocket']
    });

    newSocket.on('connect', () => {
      console.log('Connected to chat server');
      setIsConnected(true);
      
      // Join session room
      newSocket.emit('join_session', { session_id: sessionId });
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from chat server');
      setIsConnected(false);
    });

    newSocket.on('message_history', (data) => {
      setMessages(data.messages);
    });

    newSocket.on('new_message', (message: Message) => {
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('user_typing', (data) => {
      if (data.user_id !== currentUserId) {
        setOtherUserTyping(data.is_typing);
      }
    });

    newSocket.on('call_incoming', (data) => {
      if (data.session_id === sessionId && data.caller_id !== currentUserId) {
        setIncomingCall(true);
        setCallerId(data.caller_id);
        setCallType(data.call_type);
      }
    });

    newSocket.on('call_accepted', (data) => {
      if (data.session_id === sessionId) {
        setInCall(true);
        setIncomingCall(false);
      }
    });

    newSocket.on('call_rejected', (data) => {
      if (data.session_id === sessionId) {
        alert('Call was rejected');
        setIncomingCall(false);
      }
    });

    newSocket.on('error', (data) => {
      console.error('Chat error:', data.message);
    });

    setSocket(newSocket);

    return () => {
      if (newSocket) {
        newSocket.emit('leave_session', { session_id: sessionId });
        newSocket.close();
      }
    };
  }, [sessionId, currentUserId, token]);

  useEffect(() => {
    // Auto-scroll to bottom
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !socket || !isConnected) return;

    socket.emit('send_message', {
      session_id: sessionId,
      content: newMessage.trim()
    });

    setNewMessage('');
    setIsTyping(false);
    
    // Stop typing indicator
    socket.emit('typing', {
      session_id: sessionId,
      is_typing: false
    });
  };

  const handleTyping = (value: string) => {
    setNewMessage(value);

    if (!socket || !isConnected) return;

    // Send typing indicator
    if (!isTyping && value.length > 0) {
      setIsTyping(true);
      socket.emit('typing', {
        session_id: sessionId,
        is_typing: true
      });
    }

    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 2 seconds of inactivity
    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      socket?.emit('typing', {
        session_id: sessionId,
        is_typing: false
      });
    }, 2000);
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const initiateCall = (type: 'video' | 'audio') => {
    if (!socket || !isConnected) {
      alert('Not connected to chat server');
      return;
    }
    
    socket.emit('call_initiate', {
      session_id: sessionId,
      call_type: type
    });
    
    setCallType(type);
    setInCall(true);
  };

  const acceptCall = () => {
    if (!socket || !callerId) return;
    
    socket.emit('call_accept', {
      session_id: sessionId,
      caller_id: callerId
    });
    
    setIncomingCall(false);
    setInCall(true);
  };

  const rejectCall = () => {
    if (!socket) return;
    
    socket.emit('call_reject', {
      session_id: sessionId
    });
    
    setIncomingCall(false);
    setCallerId(null);
  };

  const endCall = () => {
    setInCall(false);
    setIncomingCall(false);
    setCallerId(null);
  };

  // Render video call if active
  if (inCall) {
    return (
      <VideoCall
        socket={socket}
        sessionId={sessionId}
        currentUserId={currentUserId}
        otherUserId={otherUserId}
        onCallEnd={endCall}
      />
    );
  }

  return (
    <>
      {/* Incoming Call Modal */}
      {incomingCall && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold mb-4 text-gray-900">
              Incoming {callType === 'video' ? 'Video' : 'Audio'} Call
            </h3>
            <p className="text-gray-600 mb-6">
              {callType === 'video' ? '📹' : '🎤'} Someone is calling you...
            </p>
            <div className="flex gap-4">
              <Button
                onClick={acceptCall}
                variant="primary"
                className="flex-1"
              >
                Accept
              </Button>
              <Button
                onClick={rejectCall}
                variant="secondary"
                className="flex-1 bg-red-600 hover:bg-red-700 text-white"
              >
                Reject
              </Button>
            </div>
          </Card>
        </div>
      )}

      <Card className="flex flex-col h-[600px]">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Session Chat</h3>
          <div className="flex items-center gap-3">
            {/* Call Buttons */}
            <button
              onClick={() => initiateCall('video')}
              disabled={!isConnected}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Start Video Call"
            >
              📹
            </button>
            <button
              onClick={() => initiateCall('audio')}
              disabled={!isConnected}
              className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Start Audio Call"
            >
              🎤
            </button>
            
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm text-gray-600">
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((message) => {
            const isOwn = message.sender_id === currentUserId;
            return (
              <div
                key={message.id}
                className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    isOwn
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                  <p
                    className={`text-xs mt-1 ${
                      isOwn ? 'text-blue-100' : 'text-gray-500'
                    }`}
                  >
                    {formatTime(message.created_at)}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Typing Indicator */}
      {otherUserTyping && (
        <div className="px-4 py-2 text-sm text-gray-500 italic">
          Other user is typing...
        </div>
      )}

        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <Input
              type="text"
              value={newMessage}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleTyping(e.target.value)}
              placeholder="Type your message..."
              disabled={!isConnected}
              className="flex-1"
            />
            <Button
              type="submit"
              variant="primary"
              disabled={!newMessage.trim() || !isConnected}
            >
              Send
            </Button>
          </div>
        </form>
      </Card>
    </>
  );
}
