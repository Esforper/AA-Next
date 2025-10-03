// src/components/race/RaceTrack.tsx

/**
 * RaceTrack Component
 * 5 paralel şerit ile kıvrımlı yol çizimi
 * SVG path kullanarak smooth Bezier curves
 */

import React, { useMemo } from 'react';
import {
  WeeklyRaceData,
  PathPoint,
  LaneInfo,
  PlayerLane,
  PLAYER_COLORS
} from '../../types/raceGameTypes';

interface RaceTrackProps {
  raceData: WeeklyRaceData;
  width: number;
  height: number;
  viewportScale: number;
}

export const RaceTrack: React.FC<RaceTrackProps> = ({
  raceData,
  width,
  height,
  viewportScale
}) => {
  
  // ============ LANE CONFIGURATION ============
  
  const LANE_CONFIG = useMemo(() => {
    const laneHeight = height / 6; // 5 şerit + padding
    const startY = laneHeight;
    
    const lanes: LaneInfo[] = [
      { lane_id: PlayerLane.LANE_1, y_offset: startY, color: PLAYER_COLORS[0].light, player: raceData.players[0] },
      { lane_id: PlayerLane.LANE_2, y_offset: startY + laneHeight, color: PLAYER_COLORS[1].light, player: raceData.players[1] },
      { lane_id: PlayerLane.LANE_3, y_offset: startY + laneHeight * 2, color: PLAYER_COLORS[2].light, player: raceData.players[2] },
      { lane_id: PlayerLane.LANE_4, y_offset: startY + laneHeight * 3, color: PLAYER_COLORS[3].light, player: raceData.players[3] },
      { lane_id: PlayerLane.LANE_5, y_offset: startY + laneHeight * 4, color: PLAYER_COLORS[4].light, player: raceData.players[4] }
    ];
    
    return lanes;
  }, [height, raceData.players]);
  
  // ============ PATH GENERATION ============
  
  /**
   * Her node için X pozisyonunu hesapla (kıvrımlı yol için)
   */
  const calculateNodePositions = useMemo(() => {
    const totalNodes = raceData.news_nodes.length;
    const padding = 100;
    const usableWidth = width - padding * 2;
    
    const positions: PathPoint[] = [];
    
    raceData.news_nodes.forEach((node, index) => {
      // X pozisyonu: soldan sağa lineer ilerle
      const baseX = padding + (index / (totalNodes - 1)) * usableWidth;
      
      // Kıvrım efekti: Her 5 node'da bir yukarı/aşağı dalga
      const waveAmplitude = 30;
      const waveFrequency = 0.3;
      const waveOffset = Math.sin(index * waveFrequency) * waveAmplitude;
      
      positions.push({
        x: baseX,
        y: waveOffset, // Base Y'ye eklenecek (her şerit için)
        node_index: index
      });
    });
    
    return positions;
  }, [raceData.news_nodes, width]);
  
  /**
   * SVG path string oluştur (Bezier curves)
   */
  const generateSmoothPath = (laneYOffset: number): string => {
    if (calculateNodePositions.length < 2) return '';
    
    let path = `M ${calculateNodePositions[0].x} ${laneYOffset + calculateNodePositions[0].y}`;
    
    for (let i = 1; i < calculateNodePositions.length; i++) {
      const prevPoint = calculateNodePositions[i - 1];
      const currentPoint = calculateNodePositions[i];
      
      // Control points for smooth curve
      const cpX1 = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5;
      const cpY1 = laneYOffset + prevPoint.y;
      const cpX2 = prevPoint.x + (currentPoint.x - prevPoint.x) * 0.5;
      const cpY2 = laneYOffset + currentPoint.y;
      
      // Cubic Bezier curve
      path += ` C ${cpX1} ${cpY1}, ${cpX2} ${cpY2}, ${currentPoint.x} ${laneYOffset + currentPoint.y}`;
    }
    
    return path;
  };
  
  // ============ RENDER ============
  
  return (
    <svg
      width={width}
      height={height}
      className="race-track"
      style={{ background: 'linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%)' }}
    >
      {/* Grid lines (subtle background) */}
      <defs>
        <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
          <path
            d="M 50 0 L 0 0 0 50"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="0.5"
            opacity="0.3"
          />
        </pattern>
      </defs>
      <rect width={width} height={height} fill="url(#grid)" />
      
      {/* Week Labels */}
      <g className="week-labels">
        <text x={50} y={30} fontSize="16" fontWeight="bold" fill="#1e293b">
          {raceData.category_display_name} - Hafta {raceData.week_id}
        </text>
        <text x={50} y={50} fontSize="12" fill="#64748b">
          {raceData.week_start} → {raceData.week_end} ({raceData.time_remaining_hours}h kaldı)
        </text>
      </g>
      
      {/* Lane Background Tracks */}
      {LANE_CONFIG.map((lane) => (
        <g key={lane.lane_id} className="lane-track">
          {/* Lane background path */}
          <path
            d={generateSmoothPath(lane.y_offset)}
            fill="none"
            stroke={lane.color}
            strokeWidth="40"
            strokeLinecap="round"
            opacity="0.15"
          />
          
          {/* Lane center line */}
          <path
            d={generateSmoothPath(lane.y_offset)}
            fill="none"
            stroke={lane.color}
            strokeWidth="2"
            strokeDasharray="5,5"
            opacity="0.4"
          />
          
          {/* Lane label (player name) */}
          {lane.player && (
            <text
              x={20}
              y={lane.y_offset + 5}
              fontSize="12"
              fontWeight="600"
              fill={lane.player.color}
            >
              #{lane.player.rank} {lane.player.name}
            </text>
          )}
        </g>
      ))}
      
      {/* Start/Finish markers */}
      <g className="markers">
        {/* Start Line */}
        <line
          x1={calculateNodePositions[0]?.x || 100}
          y1={LANE_CONFIG[0].y_offset - 50}
          x2={calculateNodePositions[0]?.x || 100}
          y2={LANE_CONFIG[4].y_offset + 50}
          stroke="#10b981"
          strokeWidth="3"
          strokeDasharray="10,5"
        />
        <text
          x={(calculateNodePositions[0]?.x || 100) - 30}
          y={LANE_CONFIG[0].y_offset - 60}
          fontSize="14"
          fontWeight="bold"
          fill="#10b981"
        >
          🏁 BAŞLANGIÇ
        </text>
        
        {/* Finish Line */}
        {calculateNodePositions.length > 0 && (
          <>
            <line
              x1={calculateNodePositions[calculateNodePositions.length - 1].x}
              y1={LANE_CONFIG[0].y_offset - 50}
              x2={calculateNodePositions[calculateNodePositions.length - 1].x}
              y2={LANE_CONFIG[4].y_offset + 50}
              stroke="#ef4444"
              strokeWidth="3"
              strokeDasharray="10,5"
            />
            <text
              x={calculateNodePositions[calculateNodePositions.length - 1].x - 20}
              y={LANE_CONFIG[0].y_offset - 60}
              fontSize="14"
              fontWeight="bold"
              fill="#ef4444"
            >
              🏆 BİTİŞ
            </text>
          </>
        )}
      </g>
      
      {/* Day separators (Pazartesi, Salı, etc.) */}
      <g className="day-separators">
        {[1, 2, 3, 4, 5, 6, 7].map((day) => {
          // Her günün ilk haberini bul
          const dayFirstNode = raceData.news_nodes.find(n => n.week_day === day);
          if (!dayFirstNode) return null;
          
          const nodePos = calculateNodePositions[dayFirstNode.position.index];
          if (!nodePos) return null;
          
          const dayNames = ['', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
          
          return (
            <g key={day}>
              <line
                x1={nodePos.x}
                y1={LANE_CONFIG[0].y_offset - 40}
                x2={nodePos.x}
                y2={LANE_CONFIG[4].y_offset + 40}
                stroke="#cbd5e1"
                strokeWidth="1"
                strokeDasharray="3,3"
                opacity="0.5"
              />
              <text
                x={nodePos.x}
                y={LANE_CONFIG[0].y_offset - 45}
                fontSize="10"
                fill="#64748b"
                textAnchor="middle"
              >
                {dayNames[day]}
              </text>
            </g>
          );
        })}
      </g>
      
      {/* Progress indicators (her şerit için) */}
      {LANE_CONFIG.map((lane) => {
        if (!lane.player) return null;
        
        const playerProgress = lane.player.current_node_index;
        const progressNodePos = calculateNodePositions[playerProgress - 1];
        
        if (!progressNodePos) return null;
        
        return (
          <g key={`progress-${lane.lane_id}`}>
            {/* Progress line (gölge efekti) */}
            <path
              d={generateSmoothPath(lane.y_offset)}
              fill="none"
              stroke={lane.player.color}
              strokeWidth="6"
              strokeLinecap="round"
              opacity="0.3"
              strokeDasharray={`${progressNodePos.x - 100} 10000`}
            />
          </g>
        );
      })}
      
      {/* Zoom level indicator */}
      <g className="zoom-indicator" transform={`translate(${width - 100}, 30)`}>
        <rect width="80" height="30" rx="5" fill="white" opacity="0.8" />
        <text x="10" y="20" fontSize="12" fill="#64748b">
          Zoom: {viewportScale.toFixed(1)}x
        </text>
      </g>
    </svg>
  );
};

// ============ UTILITY FUNCTIONS ============

/**
 * Node pozisyonunu lane'e göre hesapla
 */
export function getNodePositionInLane(
  nodeIndex: number,
  laneYOffset: number,
  nodePositions: PathPoint[]
): { x: number; y: number } {
  const pos = nodePositions[nodeIndex];
  if (!pos) return { x: 0, y: 0 };
  
  return {
    x: pos.x,
    y: laneYOffset + pos.y
  };
}

/**
 * Avatar pozisyonunu hesapla (node index'e göre)
 */
export function getAvatarPosition(
  currentNodeIndex: number,
  laneYOffset: number,
  nodePositions: PathPoint[]
): { x: number; y: number } {
  // Avatar bir sonraki node'a doğru ilerliyor
  const targetIndex = Math.min(currentNodeIndex, nodePositions.length - 1);
  return getNodePositionInLane(targetIndex, laneYOffset, nodePositions);
}

// ============ EXPORTS ============

export default RaceTrack;