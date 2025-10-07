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
  const [containerWidth, setContainerWidth] = useState<number>(0);
  const [didInitZoom, setDidInitZoom] = useState<boolean>(false);
  const [overlayReelId, setOverlayReelId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) fetchTree();
  }, [isOpen, fetchTree]);

  // Measure container width to center layout horizontally
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const update = () => setContainerWidth(el.clientWidth || 0);
    update();
    const ro = new ResizeObserver(update);
    try { ro.observe(el); } catch {}
    return () => { try { ro.disconnect(); } catch {} };
  }, [isOpen]);

  // On open, start slightly zoomed-in and reset translate to center
  useEffect(() => {
    if (!isOpen) { setDidInitZoom(false); return; }
    if (!didInitZoom) {
      setScale(1.1);
      setTranslate({ x: 0, y: 0 });
      setDidInitZoom(true);
    }
  }, [isOpen, didInitZoom, setScale, setTranslate]);

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

  // Yeni: Cihaz tipine göre z-index üstünde overlay modal aç
  const openReelOverlay = (nodeId: string) => {
    setOverlayReelId(nodeId);
  };
  const closeOverlay = () => setOverlayReelId(null);

  // Simple vertical layout: newest on top, linked by arrows upward
  const layout = useMemo(() => {
    const gapY = 140; // vertical space between items
    const startY = 40;
    const positions = new Map<string, { x: number; y: number }>();
    const centerX = Math.max(160, Math.floor((containerWidth || 480) / 2));
    nodes.forEach((n, idx) => {
      positions.set(n.id, { x: centerX, y: startY + idx * gapY });
    });
    return positions;
  }, [nodes, containerWidth]);

  return (
    <div className={clsx(
      'fixed top-0 right-0 h-full w-full bg-white shadow-2xl transition-transform duration-300 ease-out z-50',
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
                    <marker id={`arrow-${i}`} markerWidth="16" markerHeight="16" refX="10" refY="8" orient="auto">
                      <path d="M0,0 L0,16 L12,8 z" fill="#4b5563" />
                    </marker>
                    <filter id={`glow-${i}`} x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                      <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>
                  <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="#e5e7eb" strokeWidth={5} opacity={0.5} />
                  <line x1={from.x} y1={from.y} x2={to.x} y2={to.y} stroke="#4b5563" strokeWidth={2.5} markerEnd={`url(#arrow-${i})`} filter={`url(#glow-${i})`} />
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
                        onClick={() => openReelOverlay(n.id)}
                        className="text-left text-sm font-semibold line-clamp-3 hover:underline"
                        title={n.title}
                      >
                        {n.title}
                      </button>
                    </div>
                    <button onClick={() => openReelOverlay(n.id)} className="w-[150px] h-full relative">
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
        {/* Zoom controls - bottom-left */}
        <div className="absolute bottom-4 left-4 flex flex-col gap-2 z-[1001]">
          <button
            onClick={() => setScale(scale * 1.1)}
            className="w-10 h-10 rounded-full bg-white shadow-md border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
            title="Yakınlaştır"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#111827" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </button>
          <button
            onClick={() => setScale(scale * 0.9)}
            className="w-10 h-10 rounded-full bg-white shadow-md border border-gray-200 hover:bg-gray-50 flex items-center justify-center"
            title="Uzaklaştır"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#111827" strokeWidth="2">
              <path d="M5 12h14"/>
            </svg>
          </button>
        </div>
        {/* Overlay Modal: mobilde tam ekran, masaüstünde haber ağacını kaplayacak genişlik */}
        {overlayReelId && (
          <div
            className="fixed inset-0 z-[1000]"
            aria-modal="true"
            role="dialog"
          >
            {/* Arka plan blur/karartma */}
            <div className="absolute inset-0 bg-black/50" onClick={closeOverlay} />
            {/* İçerik kapsayıcı */}
            <div
              className="absolute top-0 right-0 h-full w-full bg-black shadow-2xl"
            >
              <button
                onClick={closeOverlay}
                aria-label="Kapat"
                className="absolute top-3 right-3 z-[1001] text-white bg-white/20 hover:bg-white/30 rounded-full w-9 h-9 flex items-center justify-center"
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M18.3 5.71a1 1 0 00-1.41 0L12 10.59 7.11 5.7A1 1 0 105.7 7.11L10.59 12l-4.9 4.89a1 1 0 101.41 1.42L12 13.41l4.89 4.9a1 1 0 001.42-1.41L13.41 12l4.9-4.89a1 1 0 000-1.4z"/></svg>
              </button>
              {/* Reels sayfasını aynı yapı ile göstermek için iframe */}
              <iframe
                title="Reels"
                src={`/reels?openId=${encodeURIComponent(overlayReelId)}&embed=1`}
                className="w-full h-full border-0"
                allow="autoplay; fullscreen"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
