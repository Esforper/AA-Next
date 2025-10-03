// src/components/race/NewsNode.tsx

/**
 * NewsNode Component
 * Yol üzerindeki haber node'ları
 * Renk: Yeşil (0-24h), Sarı (24h+), Gri (izlenmedi)
 * Zoom'da haber başlığı görünür
 */

import React, { useState } from 'react';
import {
  NewsNodeData,
  RacePlayer,
  WatchStatus,
  getNodeColor,
  NODE_COLORS
} from '../../types/raceGameTypes';

interface NewsNodeProps {
  node: NewsNodeData;
  position: { x: number; y: number };
  currentPlayer: RacePlayer;
  allPlayers: RacePlayer[];
  zoomLevel: 'far' | 'medium' | 'close';
  isSelected: boolean;
  isHovered: boolean;
  onClick: (nodeId: string) => void;
  onHover: (nodeId: string | null) => void;
}

export const NewsNode: React.FC<NewsNodeProps> = ({
  node,
  position,
  currentPlayer,
  allPlayers,
  zoomLevel,
  isSelected,
  isHovered,
  onClick,
  onHover
}) => {
  
  // ============ STATE ============
  
  const [showOtherPlayers, setShowOtherPlayers] = useState(false);
  
  // ============ CURRENT PLAYER STATUS ============
  
  const currentPlayerView = node.player_views[currentPlayer.id];
  const nodeColor = getNodeColor(currentPlayerView);
  const isWatched = currentPlayerView.watched;
  
  // ============ SIZE CALCULATIONS ============
  
  const getNodeSize = (): number => {
    if (isSelected) return 24;
    if (isHovered) return 20;
    
    switch (zoomLevel) {
      case 'close': return 16;
      case 'medium': return 12;
      case 'far': return 8;
      default: return 12;
    }
  };
  
  const nodeSize = getNodeSize();
  const shouldShowTitle = zoomLevel === 'close' || isHovered || isSelected;
  const shouldShowOtherPlayersIndicator = zoomLevel !== 'far';
  
  // ============ OTHER PLAYERS STATUS ============
  
  const otherPlayersStatus = allPlayers
    .filter(p => p.id !== currentPlayer.id)
    .map(player => ({
      player,
      view: node.player_views[player.id],
      color: getNodeColor(node.player_views[player.id])
    }));
  
  const watchedByOthersCount = otherPlayersStatus.filter(p => p.view.watched).length;
  
  // ============ RENDER ============
  
  return (
    <g
      className="news-node"
      transform={`translate(${position.x}, ${position.y})`}
      onClick={() => onClick(node.id)}
      onMouseEnter={() => onHover(node.id)}
      onMouseLeave={() => onHover(null)}
      style={{ cursor: 'pointer' }}
    >
      {/* Main Node Circle */}
      <circle
        cx={0}
        cy={0}
        r={nodeSize}
        fill={nodeColor}
        stroke={isSelected ? '#1e293b' : isHovered ? '#475569' : '#94a3b8'}
        strokeWidth={isSelected ? 3 : isHovered ? 2 : 1}
        opacity={isWatched ? 1.0 : 0.6}
        className="transition-all duration-200"
      />
      
      {/* Pulse animation for unwatched */}
      {!isWatched && zoomLevel !== 'far' && (
        <circle
          cx={0}
          cy={0}
          r={nodeSize}
          fill="none"
          stroke={NODE_COLORS.unwatched}
          strokeWidth="2"
          opacity="0.4"
        >
          <animate
            attributeName="r"
            from={nodeSize}
            to={nodeSize + 8}
            dur="2s"
            repeatCount="indefinite"
          />
          <animate
            attributeName="opacity"
            from="0.4"
            to="0"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      )}
      
      {/* Watched checkmark icon */}
      {isWatched && zoomLevel !== 'far' && (
        <g transform="scale(0.6)">
          <path
            d="M -4 0 L -1 3 L 5 -4"
            stroke="white"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      )}
      
      {/* Node number (order in week) */}
      {!isWatched && zoomLevel !== 'far' && (
        <text
          x={0}
          y={4}
          fontSize="8"
          fill="white"
          textAnchor="middle"
          fontWeight="600"
        >
          {node.order_in_week + 1}
        </text>
      )}
      
      {/* Other players indicator (small dots) */}
      {shouldShowOtherPlayersIndicator && watchedByOthersCount > 0 && (
        <g
          className="other-players-indicator"
          onMouseEnter={() => setShowOtherPlayers(true)}
          onMouseLeave={() => setShowOtherPlayers(false)}
        >
          {/* Badge circle */}
          <circle
            cx={nodeSize * 0.7}
            cy={-nodeSize * 0.7}
            r={6}
            fill="white"
            stroke="#64748b"
            strokeWidth="1"
          />
          <text
            x={nodeSize * 0.7}
            y={-nodeSize * 0.7 + 3}
            fontSize="8"
            fill="#64748b"
            textAnchor="middle"
            fontWeight="600"
          >
            {watchedByOthersCount}
          </text>
          
          {/* Tooltip on hover */}
          {showOtherPlayers && (
            <g transform={`translate(${nodeSize + 10}, ${-nodeSize})`}>
              <rect
                width="120"
                height={otherPlayersStatus.length * 20 + 10}
                rx="4"
                fill="white"
                stroke="#e2e8f0"
                strokeWidth="1"
                filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))"
              />
              {otherPlayersStatus.map((status, idx) => (
                <g key={status.player.id} transform={`translate(5, ${idx * 20 + 15})`}>
                  <circle
                    cx={5}
                    cy={0}
                    r={4}
                    fill={status.color}
                    opacity={status.view.watched ? 1.0 : 0.3}
                  />
                  <text
                    x={15}
                    y={4}
                    fontSize="10"
                    fill="#1e293b"
                    fontWeight={status.view.watched ? '600' : '400'}
                  >
                    {status.player.name} {status.view.watched ? '✓' : '○'}
                  </text>
                </g>
              ))}
            </g>
          )}
        </g>
      )}
      
      {/* News Title (visible on close zoom) */}
      {shouldShowTitle && (
        <g className="node-title">
          {/* Background box */}
          <rect
            x={nodeSize + 5}
            y={-12}
            width={Math.min(node.title.length * 5.5, 200)}
            height="24"
            rx="4"
            fill="white"
            stroke={nodeColor}
            strokeWidth="2"
            opacity="0.95"
            filter="drop-shadow(0 2px 4px rgba(0,0,0,0.1))"
          />
          
          {/* Title text */}
          <text
            x={nodeSize + 10}
            y={4}
            fontSize="11"
            fill="#1e293b"
            fontWeight="500"
            style={{
              maxWidth: '200px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {node.title.length > 35 
              ? node.title.substring(0, 35) + '...' 
              : node.title}
          </text>
        </g>
      )}
      
      {/* Watch status badge (immediate/late) */}
      {isWatched && (zoomLevel === 'close' || isHovered) && (
        <g transform={`translate(0, ${nodeSize + 15})`}>
          <rect
            x={-25}
            y={0}
            width="50"
            height="16"
            rx="8"
            fill={currentPlayerView.watch_status === WatchStatus.WATCHED_IMMEDIATE 
              ? '#dcfce7' 
              : '#fef9c3'}
            stroke={currentPlayerView.watch_status === WatchStatus.WATCHED_IMMEDIATE 
              ? '#10b981' 
              : '#f59e0b'}
            strokeWidth="1"
          />
          <text
            x={0}
            y={11}
            fontSize="9"
            fill={currentPlayerView.watch_status === WatchStatus.WATCHED_IMMEDIATE 
              ? '#059669' 
              : '#d97706'}
            textAnchor="middle"
            fontWeight="600"
          >
            {currentPlayerView.watch_status === WatchStatus.WATCHED_IMMEDIATE 
              ? '⚡ Hızlı' 
              : '🕐 Geç'}
          </text>
        </g>
      )}
      
      {/* Selection ring */}
      {isSelected && (
        <circle
          cx={0}
          cy={0}
          r={nodeSize + 4}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="2"
          strokeDasharray="4,2"
          opacity="0.8"
        >
          <animateTransform
            attributeName="transform"
            type="rotate"
            from="0 0 0"
            to="360 0 0"
            dur="3s"
            repeatCount="indefinite"
          />
        </circle>
      )}
      
      {/* Hover glow effect */}
      {isHovered && (
        <circle
          cx={0}
          cy={0}
          r={nodeSize + 2}
          fill="none"
          stroke={nodeColor}
          strokeWidth="3"
          opacity="0.3"
        />
      )}
    </g>
  );
};

// ============ MINI NODE (for detail modal) ============

interface MiniNodeProps {
  node: NewsNodeData;
  currentPlayer: RacePlayer;
  size?: number;
}

export const MiniNode: React.FC<MiniNodeProps> = ({
  node,
  currentPlayer,
  size = 12
}) => {
  const playerView = node.player_views[currentPlayer.id];
  const nodeColor = getNodeColor(playerView);
  
  return (
    <svg width={size * 2} height={size * 2}>
      <circle
        cx={size}
        cy={size}
        r={size}
        fill={nodeColor}
        stroke="#94a3b8"
        strokeWidth="1"
        opacity={playerView.watched ? 1.0 : 0.6}
      />
      {playerView.watched && (
        <g transform={`translate(${size}, ${size}) scale(0.5)`}>
          <path
            d="M -4 0 L -1 3 L 5 -4"
            stroke="white"
            strokeWidth="2"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      )}
    </svg>
  );
};

// ============ EXPORTS ============

export default NewsNode;