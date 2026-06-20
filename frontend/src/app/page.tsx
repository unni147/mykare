"use client";

import React, { useState, useRef, useEffect } from 'react';
import Avatar from '@/components/Avatar';
import ActivityPanel from '@/components/ActivityPanel';
import SummaryScreen from '@/components/SummaryScreen';

type AvatarState = 'idle' | 'listening' | 'processing' | 'speaking';

export default function Home() {
  const [state, setState] = useState<AvatarState>('idle');
  const [logs, setLogs] = useState<string[]>([]);
  const [sessionId, setSessionId] = useState("");
  const [summaryData, setSummaryData] = useState<any>(null);
  
  useEffect(() => {
    setSessionId(`sess_${Math.random().toString(36).substring(2, 9)}`);
  }, []);
  
  const streamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null);

  // Avatar Lip Sync Refs
  const ttsAudioContextRef = useRef<AudioContext | null>(null);
  const ttsAnalyserRef = useRef<AnalyserNode | null>(null);
  const ttsDataArrayRef = useRef<Uint8Array | null>(null);
  const ttsAnimRef = useRef<number | null>(null);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, msg]);
  };

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      audioChunksRef.current = [];
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorderRef.current?.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        await processAudio(audioBlob, mimeType);
      };

      mediaRecorder.start();
      setState('listening');
      addLog('Listening... Click "Stop & Send" when done.');
    } catch (err) {
      console.error("Microphone error:", err);
      addLog("Microphone access denied.");
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setState('processing');
      addLog('Processing audio...');
    }
  };

  const processAudio = async (audioBlob: Blob, mimeType: string = 'audio/webm') => {
    try {
      const ext = mimeType.includes('mp4') ? 'mp4' : mimeType.includes('ogg') ? 'ogg' : 'webm';
      const formData = new FormData();
      formData.append("audio", audioBlob, `recording.${ext}`);
      formData.append("session_id", sessionId);

      const res = await fetch("http://localhost:8000/api/conversation", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      
      addLog(`User: ${data.transcript}`);
      
      if (data.tools && data.tools.length > 0) {
        data.tools.forEach((t: string) => {
          let prettyTool = `Executing ${t}...`;
          if (t === 'identify_user') prettyTool = 'Identifying user...';
          else if (t === 'fetch_slots') prettyTool = 'Fetching available slots...';
          else if (t === 'book_appointment') prettyTool = 'Booking confirmed ✅';
          else if (t === 'retrieve_appointments') prettyTool = 'Retrieving appointments...';
          else if (t === 'cancel_appointment') prettyTool = 'Canceling appointment ❌';
          else if (t === 'modify_appointment') prettyTool = 'Modifying appointment 🔄';
          addLog(`[Tool] ${prettyTool}`);
        });
      }
      
      addLog(`AI: ${data.reply}`);
      
      if (data.audio_base64) {
        playTTSBase64(data.audio_base64);
      } else {
        setState('idle');
      }
      
    } catch (error) {
      console.error("Error processing audio:", error);
      addLog(`Error processing audio/network issue.`);
      setState('idle');
    }
  };

  const updateLipSync = () => {
    if (ttsAnalyserRef.current && ttsDataArrayRef.current) {
      ttsAnalyserRef.current.getByteFrequencyData(ttsDataArrayRef.current);
      let sum = 0;
      for (let i = 0; i < ttsDataArrayRef.current.length; i++) {
        sum += ttsDataArrayRef.current[i];
      }
      const avg = sum / ttsDataArrayRef.current.length;
      const scale = Math.min(Math.max((avg / 128), 0.0), 1.0);
      
      const mouth = document.getElementById('avatar-mouth');
      if (mouth) {
        mouth.setAttribute('d', `M 42 75 Q 50 ${75 + (scale * 18)} 58 75`);
      }
    }
    ttsAnimRef.current = requestAnimationFrame(updateLipSync);
  };

  const setupTTSAudioContext = (audioEl: HTMLAudioElement) => {
    if (!ttsAudioContextRef.current) {
      const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
      const ctx = new AudioContextClass();
      const analyser = ctx.createAnalyser();
      analyser.fftSize = 256;
      const source = ctx.createMediaElementSource(audioEl);
      source.connect(analyser);
      analyser.connect(ctx.destination);
      
      ttsAudioContextRef.current = ctx;
      ttsAnalyserRef.current = analyser;
      ttsDataArrayRef.current = new Uint8Array(analyser.frequencyBinCount);
    }
    if (ttsAudioContextRef.current.state === 'suspended') {
      ttsAudioContextRef.current.resume();
    }
  };

  const playTTSBase64 = (base64Audio: string) => {
    if (!ttsAudioRef.current) return;
    
    setState('speaking');
    const audio = ttsAudioRef.current;
    audio.src = `data:audio/mp3;base64,${base64Audio}`;
    
    audio.onplay = () => {
      setupTTSAudioContext(audio);
      updateLipSync();
    };
    
    audio.onended = () => {
      if (ttsAnimRef.current) cancelAnimationFrame(ttsAnimRef.current);
      const mouth = document.getElementById('avatar-mouth');
      if (mouth) mouth.setAttribute('d', 'M 42 75 Q 50 75 58 75');
      setState('idle');
    };
    
    audio.play().catch(e => {
      console.error("Audio playback failed:", e);
      setState('idle');
    });
  };

  const endConversation = async () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    streamRef.current?.getTracks().forEach(track => track.stop());

    addLog('Generating summary...');
    setState('processing');
    try {
      const res = await fetch(`http://localhost:8000/api/conversation/${sessionId}/summary`, {
        method: "POST"
      });
      const data = await res.json();
      addLog("Summary generated (check console)");
      
      if (!data.timestamp) {
        data.timestamp = new Date().toLocaleString('en-GB', {
          year: 'numeric', month: '2-digit', day: '2-digit',
          hour: '2-digit', minute: '2-digit', hour12: true
        }).toUpperCase().replace(',', '');
      }
      
      setSummaryData(data);
      setState('idle');
    } catch(err) {
      console.error(err);
      setState('idle');
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-5xl grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        <audio ref={ttsAudioRef} className="hidden" crossOrigin="anonymous" />
        
        {/* Left Column: Avatar & Controls */}
        <div className="flex flex-col items-center gap-8 bg-white p-12 rounded-3xl shadow-sm border border-slate-100">
          <Avatar state={state} />
          
          <div className="flex flex-col gap-4 w-full max-w-xs">
            {state === 'idle' && (
              <button 
                onClick={startListening}
                className="w-full px-6 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-full font-bold text-lg transition-colors shadow-md hover:shadow-lg flex items-center justify-center gap-2"
              >
                <span>🎤</span> Start Speaking
              </button>
            )}

            {state === 'listening' && (
              <button 
                onClick={stopListening}
                className="w-full px-6 py-4 bg-red-500 hover:bg-red-600 text-white rounded-full font-bold text-lg transition-colors shadow-md hover:shadow-lg animate-pulse"
              >
                Stop & Send
              </button>
            )}

            {state === 'idle' && logs.length > 0 && (
              <button 
                  onClick={endConversation}
                  className="w-full px-6 py-3 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-full font-medium transition-colors mt-4"
                >
                  End Conversation & View Summary
              </button>
            )}
          </div>
        </div>

        {/* Right Column: Activity Panel */}
        <div className="flex justify-center">
          <ActivityPanel logs={logs} />
        </div>

      </div>

      {summaryData && (
        <SummaryScreen summary={summaryData} onClose={() => setSummaryData(null)} />
      )}
    </main>
  );
}
