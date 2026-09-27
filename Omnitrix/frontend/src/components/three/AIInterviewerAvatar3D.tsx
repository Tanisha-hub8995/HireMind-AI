import React, { useRef, Component, ErrorInfo, ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Float, MeshDistortMaterial, Sphere, Ring, Stars } from '@react-three/drei';
import * as THREE from 'three';

interface AIInterviewerProps {
  state?: 'idle' | 'speaking' | 'listening' | 'evaluating';
  audioLevel?: number; // 0 to 1
  size?: 'sm' | 'md' | 'lg';
}

class ThreeErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.warn('3D Canvas fallback engaged:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

const CoreSphere: React.FC<{ state: string; audioLevel: number }> = ({ state, audioLevel }) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const ring3Ref = useRef<THREE.Mesh>(null);

  // Dynamic colors based on AI state
  const getColor = () => {
    switch (state) {
      case 'speaking':
        return '#00f2fe'; // Neon cyan
      case 'listening':
        return '#10b981'; // Cyber emerald
      case 'evaluating':
        return '#a855f7'; // Cosmic purple
      default:
        return '#6366f1'; // Indigo
    }
  };

  const getSecondaryColor = () => {
    switch (state) {
      case 'speaking':
        return '#4facfe';
      case 'listening':
        return '#34d399';
      case 'evaluating':
        return '#ec4899';
      default:
        return '#818cf8';
    }
  };

  useFrame((stateObj, delta) => {
    const time = stateObj.clock.getElapsedTime();

    if (meshRef.current) {
      // Rotate core
      meshRef.current.rotation.y += delta * 0.4;
      meshRef.current.rotation.x += delta * 0.2;

      // Pulsing scale based on audio level or state
      const targetScale = state === 'speaking' 
        ? 1.0 + Math.sin(time * 6) * 0.12 + (audioLevel * 0.3)
        : state === 'listening'
        ? 1.0 + Math.sin(time * 3) * 0.06
        : 1.0 + Math.sin(time * 1.5) * 0.03;
      
      meshRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    }

    if (ring1Ref.current) {
      ring1Ref.current.rotation.x = time * 0.7;
      ring1Ref.current.rotation.y = time * 0.5;
    }
    if (ring2Ref.current) {
      ring2Ref.current.rotation.y = -time * 0.6;
      ring2Ref.current.rotation.z = time * 0.4;
    }
    if (ring3Ref.current) {
      ring3Ref.current.rotation.z = -time * 0.5;
      ring3Ref.current.rotation.x = time * 0.8;
    }
  });

  const primaryColor = getColor();
  const secondaryColor = getSecondaryColor();
  const speed = state === 'speaking' ? 3.5 : state === 'evaluating' ? 4 : 1.5;
  const distort = state === 'speaking' ? 0.45 + (audioLevel * 0.25) : 0.3;

  return (
    <group>
      {/* Central Holographic Liquid Sphere */}
      <Sphere ref={meshRef} args={[1.2, 64, 64]}>
        <MeshDistortMaterial
          color={primaryColor}
          emissive={primaryColor}
          emissiveIntensity={state === 'speaking' ? 0.6 : 0.3}
          roughness={0.15}
          metalness={0.8}
          distort={distort}
          speed={speed}
        />
      </Sphere>

      {/* Cyber Orbital Rings */}
      <Ring ref={ring1Ref} args={[1.6, 1.63, 64]}>
        <meshBasicMaterial color={secondaryColor} transparent opacity={0.6} side={THREE.DoubleSide} />
      </Ring>

      <Ring ref={ring2Ref} args={[1.9, 1.92, 64]}>
        <meshBasicMaterial color={primaryColor} transparent opacity={0.4} side={THREE.DoubleSide} />
      </Ring>

      <Ring ref={ring3Ref} args={[2.2, 2.22, 64]}>
        <meshBasicMaterial color="#ffffff" transparent opacity={0.25} side={THREE.DoubleSide} />
      </Ring>
    </group>
  );
};

export const AIInterviewerAvatar3D: React.FC<AIInterviewerProps> = ({
  state = 'idle',
  audioLevel = 0,
  size = 'md',
}) => {
  const heightClass =
    size === 'sm' ? 'h-48' : size === 'lg' ? 'h-[380px] md:h-[460px]' : 'h-64 md:h-80';

  const fallbackCore = (
    <div className="relative flex items-center justify-center w-36 h-36">
      <div
        className={`absolute inset-0 rounded-full animate-ping opacity-30 ${
          state === 'speaking'
            ? 'bg-cyber-cyan'
            : state === 'listening'
            ? 'bg-emerald-400'
            : state === 'evaluating'
            ? 'bg-purple-500'
            : 'bg-brand-500'
        }`}
      />
      <div
        className={`relative w-28 h-28 rounded-full shadow-2xl flex items-center justify-center transition-all duration-500 ${
          state === 'speaking'
            ? 'bg-gradient-to-tr from-cyan-500 via-blue-500 to-indigo-500 shadow-cyan-500/50 scale-105'
            : state === 'listening'
            ? 'bg-gradient-to-tr from-emerald-500 via-teal-500 to-cyan-500 shadow-emerald-500/50 scale-105'
            : state === 'evaluating'
            ? 'bg-gradient-to-tr from-purple-500 via-pink-500 to-brand-500 shadow-purple-500/50 animate-spin'
            : 'bg-gradient-to-tr from-brand-600 via-indigo-600 to-cyber-cyan shadow-brand-500/40'
        }`}
      >
        <div className="w-16 h-16 rounded-full bg-slate-950/70 border border-white/20 backdrop-blur-md flex items-center justify-center">
          <div
            className={`w-5 h-5 rounded-full ${
              state === 'speaking'
                ? 'bg-cyber-cyan animate-pulse'
                : state === 'listening'
                ? 'bg-emerald-400 animate-bounce'
                : 'bg-brand-400'
            }`}
          />
        </div>
      </div>
    </div>
  );

  return (
    <div className={`relative w-full ${heightClass} flex items-center justify-center`}>
      <ThreeErrorBoundary fallback={fallbackCore}>
        <Canvas
          camera={{ position: [0, 0, 4.5], fov: 45 }}
          gl={{ alpha: true, antialias: true, powerPreference: 'default' }}
        >
          <ambientLight intensity={0.7} />
          <pointLight position={[10, 10, 10]} intensity={1.2} />
          <pointLight position={[-10, -10, -10]} color="#6366f1" intensity={0.8} />
          <spotLight position={[0, 5, 5]} intensity={1.5} angle={0.6} penumbra={0.8} />

          <Float speed={2} rotationIntensity={0.5} floatIntensity={0.8}>
            <CoreSphere state={state} audioLevel={audioLevel} />
          </Float>

          <Stars radius={40} depth={30} count={350} factor={3} saturation={0} fade speed={1.2} />
          <OrbitControls enableZoom={false} enablePan={false} maxPolarAngle={Math.PI / 1.6} minPolarAngle={Math.PI / 2.4} />
        </Canvas>
      </ThreeErrorBoundary>

      {/* Glow aura underneath avatar */}
      <div
        className="pointer-events-none absolute inset-0 -z-10 rounded-full blur-3xl opacity-30 transition-all duration-700"
        style={{
          background:
            state === 'speaking'
              ? 'radial-gradient(circle, rgba(0,242,254,0.6) 0%, transparent 70%)'
              : state === 'listening'
              ? 'radial-gradient(circle, rgba(16,185,129,0.6) 0%, transparent 70%)'
              : state === 'evaluating'
              ? 'radial-gradient(circle, rgba(168,85,247,0.6) 0%, transparent 70%)'
              : 'radial-gradient(circle, rgba(99,102,241,0.5) 0%, transparent 70%)',
        }}
      />
    </div>
  );
};
