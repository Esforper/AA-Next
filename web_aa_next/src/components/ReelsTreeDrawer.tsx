import React, { useEffect, useMemo, useRef, useState } from 'react';
import clsx from 'clsx';
import { useReelsTreeViewModel } from '../viewmodels/useReelsTreeViewModel';

export interface ReelsTreeDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ReelsTreeDrawer: React.FC<ReelsTreeDrawerProps> = ({ isOpen, onClose }) => {
  const { nodes, edges, loading, error, fetchTree, scale, setScale, translate, setTranslate, resetView } = useReelsTreeViewModel();

  const containerRef = useRef<HTMLDivElement>(null);
  const isPanningRef = useRef(false);
  const lastPosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  useEffect(() => {
    if (isOpen) fetchTree();
  }, [isOpen, fetchTree]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = -e.deltaY;
    const factor = delta > 0 ? 1.1 : 0.9;
    setScale(scale * factor);
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    isPanningRef.current = true;
    lastPosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanningRef.current) return;
    const dx = e.clientX - lastPosRef.current.x;
    const dy = e.clientY - lastPosRef.current.y;
    setTranslate({ x: translate.x + dx, y: translate.y + dy });
    lastPosRef.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseUp = () => {
    isPanningRef.current = false;
  };

  const handleMouseLeave = () => {
    isPanningRef.current = false;
  };

  const openInSameTab = (nodeId: string) => {
    const url = `/reels?openId=${encodeURIComponent(nodeId)}`;
    window.history.pushState({}, '', url);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    onClose();
  };

  // Simple vertical layout: newest on top, linked by arrows upward
  const layout = useMemo(() => {
    const gapY = 140; // vertical space between items
    const startY = 40;
    const positions = new Map<string, { x: number; y: number }>();
    const centerX = 240;
    nodes.forEach((n, idx) => {
      positions.set(n.id, { x: centerX, y: startY + idx * gapY });
    });
    return positions;
  }, [nodes]);

  return (
    <div className={clsx(
      'fixed top-0 right-0 h-full w-full sm:w-[420px] bg-white shadow-2xl transition-transform duration-300 ease-out z-50',
      isOpen ? 'translate-x-0' : 'translate-x-full'
    )}>
      <div className="flex items-center justify-between px-4 py-3 border-b" id="haber-agaci-panel-header">
        <h3 className="font-semibold">Haber Ağacı</h3>
        <div className="flex items-center gap-2">
          <button className="text-sm px-2 py-1 border rounded" onClick={resetView}>Sıfırla</button>
          <button className="text-sm px-2 py-1 border rounded" onClick={onClose}>Kapat</button>
        </div>
      </div>

      <div
        ref={containerRef}
        className="relative overflow-hidden touch-pan-y"
        style={{ height: 'calc(100% - 52px)' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
      >
        <div
          className="absolute top-0 left-0 origin-top-left"
          style={{ transform: `translate(${translate.x}px, ${translate.y}px) scale(${scale})` }}
        >
          {/* Edges (arrows upward from older to newer) */}
          <svg width={800} height={Math.max(1000, nodes.length * 160)} className="absolute inset-0 pointer-events-none">
            {edges.map((e, i) => {
              const from = layout.get(e.fromId);
              const to = layout.get(e.toId);
              if (!from || !to) return null;
              return (
                <g key={i}>
                  <defs>
                    <marker id={`arrow-${i}`} markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
                      <path d="M0,0 L0,6 L6,3 z" fill="#9ca3af" />
                    </marker>
                  </defs>
                  <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="#9ca3af" strokeWidth={2} markerEnd={`url(#arrow-${i})`} />
                </g>
              );
            })}
          </svg>

          {/* Nodes */}
          <div className="relative">
            {nodes.map((n) => {
              const pos = layout.get(n.id)!;
              return (
                <div key={n.id} className="absolute" style={{ left: pos.x - 150, top: pos.y - 60 }}>
                  <div className="group w-[300px] h-[120px] bg-white border rounded-lg shadow hover:shadow-md transition-shadow overflow-hidden flex">
                    <div className="flex-1 p-3 flex items-center">
                      <button
                        onClick={() => openInSameTab(n.id)}
                        className="text-left text-sm font-semibold line-clamp-3 hover:underline"
                        title={n.title}
                      >
                        {n.title}
                      </button>
                    </div>
                    <button onClick={() => openInSameTab(n.id)} className="w-[150px] h-full relative">
                      <img src={n.thumbnailUrl} alt={n.title} className="w-full h-full object-cover" loading="lazy" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {(loading || error) && (
          <div className="absolute inset-0 flex items-center justify-center">
            {loading ? <span className="text-gray-500 text-sm">Yükleniyor…</span> : <span className="text-red-500 text-sm">{error}</span>}
          </div>
        )}
      </div>
    </div>
  );
};


