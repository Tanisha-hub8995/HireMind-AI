import React, { useRef, Component, ErrorInfo, ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

class ThreeErrorBoundary extends Component<{ children: ReactNode; fallback: ReactNode }, { hasError: boolean }> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.warn('CyberBackground3D fallback engaged:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

function StarField() {
  const ref = useRef<THREE.Points>(null);

  const [positions] = React.useState(() => {
    const coords = new Float32Array(800 * 3);
    for (let i = 0; i < 800 * 3; i += 3) {
      coords[i] = (Math.random() - 0.5) * 25;
      coords[i + 1] = (Math.random() - 0.5) * 25;
      coords[i + 2] = (Math.random() - 0.5) * 15;
    }
    return coords;
  });

  useFrame((_, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta * 0.03;
      ref.current.rotation.y -= delta * 0.05;
    }
  });

  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
        <PointMaterial
          transparent
          color="#818cf8"
          size={0.045}
          sizeAttenuation={true}
          depthWrite={false}
          opacity={0.65}
        />
      </Points>
    </group>
  );
}

export const CyberBackground3D: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none -z-20 overflow-hidden">
      <ThreeErrorBoundary fallback={<div className="absolute inset-0 bg-[#070a10]" />}>
        <Canvas camera={{ position: [0, 0, 5], fov: 60 }} gl={{ alpha: true }}>
          <StarField />
        </Canvas>
      </ThreeErrorBoundary>
      <div className="absolute inset-0 bg-gradient-to-b from-[#070a10]/80 via-[#070a10]/95 to-[#070a10]" />
    </div>
  );
};
