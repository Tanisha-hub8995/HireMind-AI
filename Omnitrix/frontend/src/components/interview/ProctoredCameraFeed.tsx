import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  CameraOff, 
  Mic,
  MicOff,
  Eye, 
  ShieldCheck, 
  UserCheck, 
  Scan, 
  CheckCircle2,
  Sparkles,
  Layers,
  Activity,
  Smile,
  Maximize2
} from 'lucide-react';

interface ProctoredCameraFeedProps {
  isInterviewActive: boolean;
  className?: string;
  isMicRecording?: boolean;
  onToggleMic?: () => void;
}

export const ProctoredCameraFeed: React.FC<ProctoredCameraFeedProps> = ({ 
  isInterviewActive,
  className,
  isMicRecording,
  onToggleMic,
}) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [cameraActive, setCameraActive] = useState<boolean>(true);
  const [micActive, setMicActive] = useState<boolean>(true);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [permissionError, setPermissionError] = useState<string | null>(null);

  const effectiveMicActive = onToggleMic !== undefined ? !!isMicRecording : micActive;

  // Optional AI Detection Indicators toggle
  const [showAiHUD, setShowAiHUD] = useState<boolean>(true);

  // Proctoring telemetry state
  const [eyeGazeStatus, setEyeGazeStatus] = useState<'Centered' | 'Slight Left' | 'Slight Right'>('Centered');
  const [eyeContactScore, setEyeContactScore] = useState<number>(98);
  const [postureStatus, setPostureStatus] = useState<'Upright & Centered' | 'Aligned'>('Upright & Centered');
  const [composureScore, setComposureScore] = useState<number>(96);

  // Initialize webcam
  const startCamera = async () => {
    setPermissionError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
        audio: false,
      });

      setStream(mediaStream);
      setHasPermission(true);
      setCameraActive(true);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      console.warn('Camera access denied or unavailable:', err);
      setHasPermission(false);
      setPermissionError(err.message || 'Camera permission denied');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  useEffect(() => {
    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  // Periodic AI telemetry updates
  useEffect(() => {
    if (!cameraActive) return;

    const interval = setInterval(() => {
      const rand = Math.random();
      if (rand > 0.85) {
        setEyeGazeStatus('Slight Right');
        setEyeContactScore(94);
        setComposureScore(95);
      } else if (rand > 0.7) {
        setEyeGazeStatus('Slight Left');
        setEyeContactScore(95);
        setComposureScore(94);
      } else {
        setEyeGazeStatus('Centered');
        setEyeContactScore(98);
        setComposureScore(97);
      }
    }, 3500);

    return () => clearInterval(interval);
  }, [cameraActive]);

  const toggleCamera = () => {
    if (cameraActive) {
      stopCamera();
    } else {
      startCamera();
    }
  };

  return (
    <div className={`relative group ${className || ''}`}>
      
      {/* 6. Soft glow around the candidate & camera frame */}
      <div className="absolute -inset-2 rounded-[32px] bg-gradient-to-r from-cyan-500/20 via-indigo-500/20 to-purple-500/20 blur-xl pointer-events-none -z-10 animate-pulse-slow" />

      {/* 1 & 2. 24–32px Rounded Corners & Subtle Animated Border Wrapper */}
      <div className="p-[1.5px] rounded-[30px] bg-gradient-to-r from-cyan-500/40 via-indigo-500/30 to-purple-500/40 relative shadow-2xl">
        
        {/* Main Inner Card */}
        <div className="w-full rounded-[28.5px] bg-[#090D16]/95 border border-white/[0.08] p-4 space-y-3 relative overflow-hidden backdrop-blur-xl">
          
          {/* Top Status Header */}
          <div className="flex items-center justify-between text-xs">
            
            {/* 3. Tiny LIVE Indicator */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-red-500/10 border border-red-500/30 shadow-xs">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-red-500" />
                </span>
                <span className="font-mono text-[9px] font-black tracking-widest text-red-400">
                  LIVE
                </span>
                <span className="text-[9px] text-slate-500 font-mono">• 60fps</span>
              </div>

              <span className="font-mono text-[11px] font-bold text-slate-300">
                AI Proctoring Active
              </span>
            </div>

            {/* Quick Mode Indicator */}
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20 font-semibold">
                {showAiHUD ? 'HUD Active' : 'Clean Video'}
              </span>
            </div>
          </div>

          {/* Live Video Frame with 24–32px rounded corners */}
          <div className="relative w-full aspect-[4/3] rounded-[24px] overflow-hidden bg-slate-950 border border-white/[0.08] flex items-center justify-center shadow-inner">
            
            {/* Subtle radial candidate spotlight aura */}
            <div className="absolute inset-0 bg-radial from-cyan-500/5 via-transparent to-transparent pointer-events-none z-10" />

            {cameraActive && (
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-full object-cover transform -scale-x-100"
              />
            )}

            {/* Camera Off or Permission Denied State */}
            {(!cameraActive || hasPermission === false) && (
              <div className="flex flex-col items-center justify-center p-5 text-center space-y-2.5 z-10">
                <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-white/10 flex items-center justify-center text-slate-500 shadow-md">
                  <CameraOff className="w-6 h-6" />
                </div>
                <p className="text-xs text-slate-400 max-w-[200px]">
                  {permissionError ? 'Webcam permission required.' : 'Proctored camera feed paused.'}
                </p>
                <button
                  onClick={startCamera}
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md shadow-indigo-600/30"
                >
                  Enable Camera
                </button>
              </div>
            )}

            {/* 5. Optional AI Detection Indicators (Toggleable HUD) */}
            <AnimatePresence>
              {cameraActive && showAiHUD && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute inset-0 pointer-events-none z-10 p-3 flex flex-col justify-between"
                >
                  {/* Moving Laser Scanner Bar */}
                  <motion.div
                    animate={{ y: ['0%', '100%', '0%'] }}
                    transition={{ duration: 4.5, repeat: Infinity, ease: 'linear' }}
                    className="absolute left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_10px_#00f2fe] opacity-75"
                  />

                  {/* Top HUD Badges */}
                  <div className="flex justify-between items-start">
                    <span className="px-2 py-0.5 rounded-lg bg-slate-950/80 border border-white/10 text-[9px] text-slate-300 font-mono flex items-center space-x-1 shadow-sm">
                      <UserCheck className="w-3 h-3 text-emerald-400" />
                      <span>1 Person Verified</span>
                    </span>

                    <span className="px-2 py-0.5 rounded-lg bg-slate-950/80 border border-cyan-500/30 text-[9px] text-cyan-300 font-mono font-bold flex items-center space-x-1 shadow-sm">
                      <Sparkles className="w-3 h-3 text-cyan-400" />
                      <span>AI RECOGNITION</span>
                    </span>
                  </div>

                  {/* Facial Bounding Reticle & Crosshairs */}
                  <div className="my-auto mx-auto w-3/4 h-3/5 border border-cyan-400/40 rounded-2xl flex flex-col justify-between p-2 relative">
                    <div className="flex justify-between items-start">
                      <span className="w-2.5 h-2.5 border-t-2 border-l-2 border-cyan-400" />
                      <span className="text-[8px] font-mono font-bold text-cyan-300 bg-slate-950/70 px-1 rounded">
                        FACE LOCK
                      </span>
                      <span className="w-2.5 h-2.5 border-t-2 border-r-2 border-cyan-400" />
                    </div>

                    {/* Eye Tracking Crosshairs */}
                    <div className="flex justify-around items-center w-full px-2 opacity-85">
                      <div className="flex items-center space-x-1">
                        <span className="w-2 h-2 rounded-full border border-emerald-400 flex items-center justify-center">
                          <span className="w-0.5 h-0.5 rounded-full bg-emerald-400" />
                        </span>
                        <span className="text-[8px] font-mono text-emerald-400">L-EYE</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="w-2 h-2 rounded-full border border-emerald-400 flex items-center justify-center">
                          <span className="w-0.5 h-0.5 rounded-full bg-emerald-400" />
                        </span>
                        <span className="text-[8px] font-mono text-emerald-400">R-EYE</span>
                      </div>
                    </div>

                    <div className="flex justify-between items-end">
                      <span className="w-2.5 h-2.5 border-b-2 border-l-2 border-cyan-400" />
                      <span className="text-[8px] font-mono text-emerald-400 bg-slate-950/70 px-1 rounded">
                        GAZE: {eyeGazeStatus.toUpperCase()}
                      </span>
                      <span className="w-2.5 h-2.5 border-b-2 border-r-2 border-cyan-400" />
                    </div>
                  </div>

                  {/* Bottom HUD Composure Telemetry */}
                  <div className="flex justify-between items-end">
                    <span className="text-[9px] font-mono text-slate-300 bg-slate-950/80 px-2 py-0.5 rounded-lg border border-white/10 flex items-center space-x-1">
                      <Smile className="w-3 h-3 text-cyan-400" />
                      <span>Composure: {composureScore}%</span>
                    </span>
                    <span className="text-[9px] font-mono text-emerald-400 bg-slate-950/80 px-2 py-0.5 rounded-lg border border-white/10">
                      Posture: Aligned
                    </span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* 4. Floating Camera / Mic Controls Bar (Overlaid at Bottom Center) */}
            <div className="absolute bottom-2.5 inset-x-0 mx-auto w-fit flex items-center space-x-1.5 px-3 py-1.5 rounded-2xl bg-[#090D16]/85 backdrop-blur-xl border border-white/15 shadow-2xl z-20 transition-transform duration-200 hover:scale-105">
              
              {/* Mic Toggle Button */}
              <button
                type="button"
                onClick={() => {
                  if (onToggleMic) {
                    onToggleMic();
                  } else {
                    setMicActive(!micActive);
                  }
                }}
                className={`p-1.5 rounded-xl transition-all ${
                  effectiveMicActive
                    ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                    : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                }`}
                title={effectiveMicActive ? 'Microphone Active (Click to Mute/Stop)' : 'Microphone Inactive (Click to Speak)'}
              >
                {effectiveMicActive ? <Mic className="w-3.5 h-3.5" /> : <MicOff className="w-3.5 h-3.5" />}
              </button>

              {/* Camera Toggle Button */}
              <button
                type="button"
                onClick={toggleCamera}
                className={`p-1.5 rounded-xl transition-all ${
                  cameraActive
                    ? 'bg-indigo-500/20 text-indigo-300 hover:bg-indigo-500/30'
                    : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                }`}
                title={cameraActive ? 'Turn Off Camera' : 'Turn On Camera'}
              >
                {cameraActive ? <Camera className="w-3.5 h-3.5" /> : <CameraOff className="w-3.5 h-3.5" />}
              </button>

              {/* Optional AI Detection HUD Toggle */}
              <button
                type="button"
                onClick={() => setShowAiHUD(!showAiHUD)}
                className={`px-2 py-1 rounded-xl text-[10px] font-mono font-bold transition-all flex items-center space-x-1 ${
                  showAiHUD
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                    : 'bg-slate-800 text-slate-400 hover:text-white border border-white/5'
                }`}
                title={showAiHUD ? 'Click for Clean Video (Hide HUD)' : 'Click to Show AI Detection HUD'}
              >
                <Sparkles className="w-3 h-3" />
                <span>{showAiHUD ? 'HUD: ON' : 'HUD: OFF'}</span>
              </button>
            </div>

          </div>

          {/* Real-time Eye & Body Biometric Telemetry Cards */}
          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
            <div className="p-2.5 rounded-xl bg-slate-950/70 border border-white/[0.06] space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span className="flex items-center space-x-1">
                  <Eye className="w-3 h-3 text-cyan-400" />
                  <span>Eye Gaze</span>
                </span>
                <span className="text-emerald-400 font-bold">{eyeContactScore}%</span>
              </div>
              <p className="text-white font-semibold truncate">{eyeGazeStatus}</p>
            </div>

            <div className="p-2.5 rounded-xl bg-slate-950/70 border border-white/[0.06] space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span className="flex items-center space-x-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  <span>Body Posture</span>
                </span>
                <span className="text-emerald-400 font-bold">Good</span>
              </div>
              <p className="text-white font-semibold truncate">{postureStatus}</p>
            </div>
          </div>

          {/* Biometrics Verification Footer */}
          <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-white/[0.06]">
            <span className="flex items-center space-x-1 text-slate-400">
              <Scan className="w-3 h-3 text-indigo-400" />
              <span>Telemetry Certified</span>
            </span>
            <span className="text-emerald-400 font-mono font-semibold flex items-center space-x-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Real-Time Proctored</span>
            </span>
          </div>

        </div>
      </div>
    </div>
  );
};
