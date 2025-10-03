// src/views/GameRaceView.tsx

/**
 * GameRaceView - Ana Yarış Ekranı
 * 5 paralel şerit, kıvrımlı yol, node'lar, avatarlar
 * Zoom/Pan kontrolleri, node detay modal
 */

import React, { useState, useRef, useEffect, useMemo } from 'react';
import RaceTrack, { getNodePositionInLane, getAvatarPosition } from '../components/race/RaceTrack';
import NewsNode from '../components/race/NewsNode';
import PlayerAvatar from '../components/race/PlayerAvatar';
import NodeDetailModal from '../components/race/NodeDetailModal';
import {
  WeeklyRaceData,
  ViewportState,
  PathPoint,
  PlayerLane,
  RacePlayer
} from '../types/raceGameTypes';
import { mockWeeklyRaceData, getMockNodeDetail } from '../data/mockRaceData';

export const GameRaceView: React.FC = () => {
  
  // ============ STATE ============
  
  const [raceData] = useState<WeeklyRaceData>(mockWeeklyRaceData);
  const [viewport, setViewport] = useState<ViewportState>({
    scale: 1.0,
    offset_x: 0,
    offset_y: 0,
    zoom_level: 'medium'
  });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number } | null>(null);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  
  // ============ DIMENSIONS ============
  
  const SVG_WIDTH = 3000;
  const SVG_HEIGHT = 800;
  const CONTAINER_WIDTH = typeof window !== 'undefined' ? window.innerWidth : 1200;
  const CONTAINER_HEIGHT = typeof window !== 'undefined' ? window.innerHeight - 100 : 700;
  
  // ============ CURRENT PLAYER ============
  
  const currentPlayer = useMemo(
    () => raceData.players.find(p => p.id === raceData.current_user_id)!,
    [raceData]
  );
  
  // ============ NODE POSITIONS ============
  
  const nodePositions = useMemo((): PathPoint[] => {
    const totalNodes = raceData.news_nodes.length;
    const padding = 100;
    const usableWidth = SVG_WIDTH - padding * 2;
    
    return raceData.news_nodes.map((node, index) => {
      const baseX = padding + (index / (totalNodes - 1)) * usableWidth;
      const waveAmplitude = 30;
      const waveFrequency = 0.3;
      const waveOffset = Math.sin(index * waveFrequency) * waveAmplitude;
      
      return {
        x: baseX,
        y: waveOffset,
        node_index: index
      };
    });
  }, [raceData.news_nodes]);
  
  // ============ LANE CONFIGURATION ============
  
  const laneOffsets = useMemo(() => {
    const laneHeight = SVG_HEIGHT / 6;
    const startY = laneHeight;
    
    return [
      startY,
      startY + laneHeight,
      startY + laneHeight * 2,
      startY + laneHeight * 3,
      startY + laneHeight * 4
    ];
  }, []);
  
  // ============ ZOOM LEVEL CALCULATION ============
  
  const getZoomLevel = (scale: number): 'far' | 'medium' | 'close' => {
    if (scale < 0.8) return 'far';
    if (scale > 1.5) return 'close';
    return 'medium';
  };
  
  // ============ ZOOM HANDLERS ============
  
  const handleZoomIn = () => {
    setViewport(prev => {
      const newScale = Math.min(prev.scale * 1.2, 3.0);
      return {
        ...prev,
        scale: newScale,
        zoom_level: getZoomLevel(newScale)
      };
    });
  };
  
  const handleZoomOut = () => {
    setViewport(prev => {
      const newScale = Math.max(prev.scale / 1.2, 0.5);
      return {
        ...prev,
        scale: newScale,
        zoom_level: getZoomLevel(newScale)
      };
    });
  };
  
  const handleZoomReset = () => {
    setViewport({
      scale: 1.0,
      offset_x: 0,
      offset_y: 0,
      zoom_level: 'medium'
    });
  };
  
  // ============ PAN HANDLERS ============
  
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsPanning(true);
    setPanStart({ x: e.clientX - viewport.offset_x, y: e.clientY - viewport.offset_y });
  };
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isPanning || !panStart) return;
    
    setViewport(prev => ({
      ...prev,
      offset_x: e.clientX - panStart.x,
      offset_y: e.clientY - panStart.y
    }));
  };
  
  const handleMouseUp = () => {
    setIsPanning(false);
    setPanStart(null);
  };
  
  // ============ WHEEL ZOOM ============
  
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(0.5, Math.min(3.0, viewport.scale * delta));
    
    setViewport(prev => ({
      ...prev,
      scale: newScale,
      zoom_level: getZoomLevel(newScale)
    }));
  };
  
  // ============ NODE HANDLERS ============
  
  const handleNodeClick = (nodeId: string) => {
    setSelectedNodeId(nodeId);
  };
  
  const handleNodeHover = (nodeId: string | null) => {
    setHoveredNodeId(nodeId);
  };
  
  const handleCloseModal = () => {
    setSelectedNodeId(null);
  };
  
  // ============ AUTO CENTER ON CURRENT PLAYER ============
  
  useEffect(() => {
    if (currentPlayer && nodePositions.length > 0) {
      const playerPos = getAvatarPosition(
        currentPlayer.current_node_index,
        laneOffsets[currentPlayer.lane],
        nodePositions
      );
      
      // Center viewport on player
      const centerX = CONTAINER_WIDTH / 2 - playerPos.x * viewport.scale;
      const centerY = CONTAINER_HEIGHT / 2 - playerPos.y * viewport.scale;
      
      setViewport(prev => ({
        ...prev,
        offset_x: centerX,
        offset_y: centerY
      }));
    }
  }, []); // Only on mount
  
  // ============ KEYBOARD SHORTCUTS ============
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case '+':
        case '=':
          handleZoomIn();
          break;
        case '-':
        case '_':
          handleZoomOut();
          break;
        case '0':
          handleZoomReset();
          break;
        case 'Escape':
          setSelectedNodeId(null);
          break;
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  // ============ RENDER ============
  
  return (
    <div className="game-race-view w-full h-screen overflow-hidden bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Title */}
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-900">
              🏁 {raceData.category_display_name} Yarışı
            </h1>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full font-semibold">
                Hafta {raceData.week_id}
              </span>
              <span className="text-gray-400">•</span>
              <span>⏰ {raceData.time_remaining_hours}h kaldı</span>
            </div>
          </div>
          
          {/* Current Player Stats */}
          <div className="flex items-center gap-6">
            <div className="text-right">
              <div className="text-sm text-gray-500">Sıralaman</div>
              <div className="text-2xl font-bold" style={{ color: currentPlayer.color }}>
                #{currentPlayer.rank}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Puanın</div>
              <div className="text-2xl font-bold text-gray-900">
                {currentPlayer.points.toLocaleString('tr-TR')}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">İlerleme</div>
              <div className="text-2xl font-bold text-green-600">
                {Math.round(currentPlayer.progress_percentage)}%
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Race Canvas */}
      <div
        ref={containerRef}
        className="absolute inset-0 top-20 cursor-grab active:cursor-grabbing"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        style={{
          overflow: 'hidden',
          touchAction: 'none'
        }}
      >
        <svg
          ref={svgRef}
          width={CONTAINER_WIDTH}
          height={CONTAINER_HEIGHT}
          style={{
            transform: `translate(${viewport.offset_x}px, ${viewport.offset_y}px) scale(${viewport.scale})`,
            transformOrigin: '0 0',
            transition: isPanning ? 'none' : 'transform 0.3s ease-out'
          }}
        >
          {/* Race Track */}
          <RaceTrack
            raceData={raceData}
            width={SVG_WIDTH}
            height={SVG_HEIGHT}
            viewportScale={viewport.scale}
          />
          
          {/* News Nodes (all lanes) */}
          {raceData.news_nodes.map((node) => {
            // Her şerit için node'u çiz
            return raceData.players.map((player) => {
              const laneOffset = laneOffsets[player.lane];
              const nodePos = getNodePositionInLane(
                node.position.index,
                laneOffset,
                nodePositions
              );
              
              return (
                <NewsNode
                  key={`${node.id}-lane-${player.lane}`}
                  node={node}
                  position={nodePos}
                  currentPlayer={player}
                  allPlayers={raceData.players}
                  zoomLevel={viewport.zoom_level}
                  isSelected={selectedNodeId === node.id}
                  isHovered={hoveredNodeId === node.id}
                  onClick={handleNodeClick}
                  onHover={handleNodeHover}
                />
              );
            });
          })}
          
          {/* Player Avatars */}
          {raceData.players.map((player) => {
            const laneOffset = laneOffsets[player.lane];
            const avatarPos = getAvatarPosition(
              player.current_node_index,
              laneOffset,
              nodePositions
            );
            
            return (
              <PlayerAvatar
                key={player.id}
                player={player}
                position={avatarPos}
                isCurrentUser={player.is_current_user}
                zoomLevel={viewport.zoom_level}
              />
            );
          })}
        </svg>
      </div>
      
      {/* Zoom Controls */}
      <div className="absolute bottom-8 right-8 z-40 flex flex-col gap-2">
        <button
          onClick={handleZoomIn}
          className="w-12 h-12 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center text-gray-700 hover:text-blue-600 font-bold text-xl"
          title="Yakınlaştır (+)"
        >
          +
        </button>
        <button
          onClick={handleZoomReset}
          className="w-12 h-12 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center text-gray-700 hover:text-blue-600 font-bold text-sm"
          title="Sıfırla (0)"
        >
          ↺
        </button>
        <button
          onClick={handleZoomOut}
          className="w-12 h-12 bg-white rounded-full shadow-lg hover:shadow-xl transition-shadow flex items-center justify-center text-gray-700 hover:text-blue-600 font-bold text-xl"
          title="Uzaklaştır (-)"
        >
          −
        </button>
      </div>
      
      {/* Leaderboard (Mini) */}
      <div className="absolute top-24 right-8 z-40 bg-white/95 backdrop-blur-md rounded-xl shadow-lg p-4 w-64">
        <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
          🏆 Liderlik Tablosu
        </h3>
        <div className="space-y-2">
          {raceData.players
            .sort((a, b) => a.rank - b.rank)
            .map((player, idx) => (
              <div
                key={player.id}
                className={`flex items-center gap-3 p-2 rounded-lg transition-colors ${
                  player.is_current_user ? 'bg-blue-50 ring-2 ring-blue-200' : 'hover:bg-gray-50'
                }`}
              >
                <div className="text-lg font-bold" style={{ color: player.color }}>
                  {idx < 3 ? ['🥇', '🥈', '🥉'][idx] : `#${player.rank}`}
                </div>
                <img
                  src={player.avatar_url}
                  alt={player.name}
                  className="w-8 h-8 rounded-full border-2"
                  style={{ borderColor: player.color }}
                />
                <div className="flex-1">
                  <div className="text-sm font-semibold text-gray-900">
                    {player.name} {player.is_current_user && '(Sen)'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {player.total_watched}/{raceData.total_news_count} haber
                  </div>
                </div>
                <div className="text-sm font-bold" style={{ color: player.color }}>
                  {player.points}
                </div>
              </div>
            ))}
        </div>
      </div>
      
      {/* Instructions (bottom left) */}
      <div className="absolute bottom-8 left-8 z-40 bg-white/90 backdrop-blur-md rounded-lg shadow-md p-3 text-xs text-gray-600 max-w-xs">
        <div className="font-semibold text-gray-700 mb-2">🎮 Kontroller:</div>
        <div className="space-y-1">
          <div>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">Mouse Wheel</kbd> - Zoom</div>
          <div>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">Sürükle</kbd> - Pan</div>
          <div>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">+/-</kbd> - Yakınlaştır/Uzaklaştır</div>
          <div>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">0</kbd> - Sıfırla</div>
          <div>• <kbd className="px-1 py-0.5 bg-gray-200 rounded">Node</kbd> tıkla - Detay</div>
        </div>
      </div>
      
      {/* Category Legend */}
      <div className="absolute bottom-8 left-96 z-40 bg-white/90 backdrop-blur-md rounded-lg shadow-md p-3">
        <div className="font-semibold text-gray-700 mb-2 text-xs">📊 Renk Açıklaması:</div>
        <div className="flex gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span className="text-gray-600">Hızlı (0-24h)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
            <span className="text-gray-600">Geç (24h+)</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-gray-300"></div>
            <span className="text-gray-600">İzlenmedi</span>
          </div>
        </div>
      </div>
      
      {/* Node Detail Modal */}
      {selectedNodeId && (
        <NodeDetailModal
          nodeDetail={getMockNodeDetail(selectedNodeId)!}
          onClose={handleCloseModal}
          onWatchNews={() => {
            // TODO: Implement watch news action
            console.log('Watch news:', selectedNodeId);
            handleCloseModal();
          }}
        />
      )}
    </div>
  );
};

export default GameRaceView;