import { useEffect, useRef, useState } from 'react';
import { Socket } from 'socket.io-client';

interface VideoCallProps {
  socket: Socket | null;
  sessionId: number;
  currentUserId: number;
  otherUserId: number;
  onCallEnd: () => void;
}

interface RTCConfig {
  iceServers: RTCIceServer[];
}

const VideoCall: React.FC<VideoCallProps> = ({
  socket,
  sessionId,
  currentUserId,
  otherUserId,
  onCallEnd,
}) => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingUrl, setRecordingUrl] = useState<string | null>(null);
  
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);
  const peerConnectionRef = useRef<RTCPeerConnection | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  
  // WebRTC configuration with public STUN servers
  const rtcConfig: RTCConfig = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' },
      { urls: 'stun:stun2.l.google.com:19302' },
    ],
  };

  useEffect(() => {
    initializeCall();
    
    return () => {
      cleanup();
    };
  }, []);

  useEffect(() => {
    if (!socket) return;

    // Listen for WebRTC signaling events
    socket.on('webrtc_offer', handleReceiveOffer);
    socket.on('webrtc_answer', handleReceiveAnswer);
    socket.on('webrtc_ice_candidate', handleReceiveIceCandidate);
    socket.on('call_ended', handleCallEnded);

    return () => {
      socket.off('webrtc_offer', handleReceiveOffer);
      socket.off('webrtc_answer', handleReceiveAnswer);
      socket.off('webrtc_ice_candidate', handleReceiveIceCandidate);
      socket.off('call_ended', handleCallEnded);
    };
  }, [socket, sessionId]);

  const initializeCall = async () => {
    try {
      setIsConnecting(true);
      
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      
      setLocalStream(stream);
      
      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream;
      }
      
      // Create peer connection
      const pc = new RTCPeerConnection(rtcConfig);
      peerConnectionRef.current = pc;
      
      // Add local stream tracks to peer connection
      stream.getTracks().forEach(track => {
        pc.addTrack(track, stream);
      });
      
      // Handle remote stream
      pc.ontrack = (event) => {
        console.log('Received remote track');
        const [remoteStream] = event.streams;
        setRemoteStream(remoteStream);
        
        if (remoteVideoRef.current) {
          remoteVideoRef.current.srcObject = remoteStream;
        }
        
        setIsConnected(true);
        setIsConnecting(false);
      };
      
      // Handle ICE candidates
      pc.onicecandidate = (event) => {
        if (event.candidate && socket) {
          socket.emit('webrtc_ice_candidate', {
            session_id: sessionId,
            target_user_id: otherUserId,
            candidate: event.candidate,
          });
        }
      };
      
      // Handle connection state changes
      pc.onconnectionstatechange = () => {
        console.log('Connection state:', pc.connectionState);
        if (pc.connectionState === 'connected') {
          setIsConnected(true);
          setIsConnecting(false);
        } else if (pc.connectionState === 'failed' || pc.connectionState === 'disconnected') {
          setIsConnected(false);
        }
      };
      
      // Create and send offer
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      if (socket) {
        socket.emit('webrtc_offer', {
          session_id: sessionId,
          target_user_id: otherUserId,
          offer: offer,
        });
      }
      
    } catch (error) {
      console.error('Error initializing call:', error);
      alert('Failed to access camera/microphone. Please check permissions.');
      onCallEnd();
    }
  };

  const handleReceiveOffer = async (data: any) => {
    if (data.session_id !== sessionId) return;
    
    try {
      const pc = peerConnectionRef.current;
      if (!pc) return;
      
      await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
      
      const answer = await pc.createAnswer();
      await pc.setLocalDescription(answer);
      
      if (socket) {
        socket.emit('webrtc_answer', {
          session_id: sessionId,
          target_user_id: data.from_user_id,
          answer: answer,
        });
      }
    } catch (error) {
      console.error('Error handling offer:', error);
    }
  };

  const handleReceiveAnswer = async (data: any) => {
    if (data.session_id !== sessionId) return;
    
    try {
      const pc = peerConnectionRef.current;
      if (!pc) return;
      
      await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
    } catch (error) {
      console.error('Error handling answer:', error);
    }
  };

  const handleReceiveIceCandidate = async (data: any) => {
    if (data.session_id !== sessionId) return;
    
    try {
      const pc = peerConnectionRef.current;
      if (!pc) return;
      
      await pc.addIceCandidate(new RTCIceCandidate(data.candidate));
    } catch (error) {
      console.error('Error handling ICE candidate:', error);
    }
  };

  const handleCallEnded = (data: any) => {
    if (data.session_id === sessionId) {
      cleanup();
      onCallEnd();
    }
  };

  const toggleAudio = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsAudioEnabled(audioTrack.enabled);
      }
    }
  };

  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsVideoEnabled(videoTrack.enabled);
      }
    }
  };

  const startRecording = async () => {
    try {
      if (!localStream) {
        alert('No stream available to record');
        return;
      }

      // Create a combined stream with both local and remote audio/video
      const combinedStream = new MediaStream();
      
      // Add local stream tracks
      localStream.getTracks().forEach(track => {
        combinedStream.addTrack(track);
      });
      
      // Add remote stream tracks if available
      if (remoteStream) {
        remoteStream.getTracks().forEach(track => {
          combinedStream.addTrack(track);
        });
      }

      const mediaRecorder = new MediaRecorder(combinedStream, {
        mimeType: 'video/webm;codecs=vp8,opus',
      });

      mediaRecorderRef.current = mediaRecorder;
      recordedChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
        await uploadRecording(blob);
      };

      mediaRecorder.start();
      setIsRecording(true);

      // Notify backend that recording started
      const response = await fetch(`http://localhost:8001/api/v1x/recordings/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        console.error('Failed to mark recording start');
      }
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const uploadRecording = async (blob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('file', blob, `session_${sessionId}_recording.webm`);
      formData.append('session_id', sessionId.toString());

      const response = await fetch(`http://localhost:8001/api/v1x/recordings/stop`, {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setRecordingUrl(data.recording_url);
        alert('Recording saved successfully!');
      } else {
        alert('Failed to upload recording');
      }
    } catch (error) {
      console.error('Error uploading recording:', error);
      alert('Failed to upload recording');
    }
  };

  const endCall = () => {
    // Stop recording if active
    if (isRecording) {
      stopRecording();
    }
    
    if (socket) {
      socket.emit('call_end', { session_id: sessionId });
    }
    cleanup();
    onCallEnd();
  };

  const cleanup = () => {
    // Stop all tracks
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
    }
    if (remoteStream) {
      remoteStream.getTracks().forEach(track => track.stop());
    }
    
    // Close peer connection
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }
    
    setLocalStream(null);
    setRemoteStream(null);
    setIsConnected(false);
    setIsConnecting(false);
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Video Container */}
      <div className="flex-1 relative">
        {/* Remote Video (full screen) */}
        <div className="absolute inset-0 bg-gray-900 flex items-center justify-center">
          {isConnecting && (
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p>Connecting...</p>
            </div>
          )}
          {!remoteStream && !isConnecting && (
            <div className="text-white text-center">
              <p className="text-lg">Waiting for other participant...</p>
            </div>
          )}
          <video
            ref={remoteVideoRef}
            autoPlay
            playsInline
            className={`w-full h-full object-contain ${remoteStream ? 'block' : 'hidden'}`}
          />
        </div>
        
        {/* Local Video (picture-in-picture) */}
        <div className="absolute top-4 right-4 w-48 h-36 bg-gray-800 rounded-lg overflow-hidden shadow-lg border-2 border-white">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover mirror"
          />
          {!isVideoEnabled && (
            <div className="absolute inset-0 bg-gray-800 flex items-center justify-center">
              <span className="text-white text-4xl">📷</span>
            </div>
          )}
        </div>
        
        {/* Connection Status */}
        {isConnected && (
          <div className="absolute top-4 left-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm flex items-center">
            <span className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></span>
            Connected
          </div>
        )}
      </div>
      
      {/* Controls */}
      <div className="bg-gray-900 p-6 flex justify-center items-center gap-4">
        <button
          onClick={toggleAudio}
          className={`w-14 h-14 rounded-full flex items-center justify-center text-white text-xl transition-all ${
            isAudioEnabled
              ? 'bg-gray-700 hover:bg-gray-600'
              : 'bg-red-600 hover:bg-red-700'
          }`}
          title={isAudioEnabled ? 'Mute Audio' : 'Unmute Audio'}
        >
          {isAudioEnabled ? '🎤' : '🔇'}
        </button>
        
        <button
          onClick={toggleVideo}
          className={`w-14 h-14 rounded-full flex items-center justify-center text-white text-xl transition-all ${
            isVideoEnabled
              ? 'bg-gray-700 hover:bg-gray-600'
              : 'bg-red-600 hover:bg-red-700'
          }`}
          title={isVideoEnabled ? 'Stop Video' : 'Start Video'}
        >
          {isVideoEnabled ? '📹' : '📷'}
        </button>
        
        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`w-14 h-14 rounded-full flex items-center justify-center text-white text-xl transition-all ${
            isRecording
              ? 'bg-red-600 hover:bg-red-700 animate-pulse'
              : 'bg-gray-700 hover:bg-gray-600'
          }`}
          title={isRecording ? 'Stop Recording' : 'Start Recording'}
        >
          ⏺️
        </button>
        
        <button
          onClick={endCall}
          className="w-14 h-14 rounded-full bg-red-600 hover:bg-red-700 flex items-center justify-center text-white text-xl transition-all"
          title="End Call"
        >
          📞
        </button>
      </div>
      
      {/* Recording Status & Download */}
      {recordingUrl && (
        <div className="bg-green-600 text-white px-4 py-2 text-center">
          Recording saved! 
          <a 
            href={`http://localhost:8001/api/v1x/recordings/${sessionId}/download`}
            download
            className="ml-2 underline hover:text-green-200"
          >
            Download Recording
          </a>
        </div>
      )}
      
      <style jsx>{`
        .mirror {
          transform: scaleX(-1);
        }
      `}</style>
    </div>
  );
};

export default VideoCall;
