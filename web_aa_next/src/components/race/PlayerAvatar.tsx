// src/components/race/PlayerAvatar.tsx

/**
 * PlayerAvatar Component
 * Oyuncu avatarları - yol üzerinde konumlandırılır
 * Animasyonlu hareket, sıralama badge, ilerleme göstergesi
 */

import React from 'react';
import { RacePlayer } from '../../types/raceGameTypes';

interface PlayerAvatarProps {
  player: RacePlayer;
  position: { x: number; y: number };
  isCurrentUser: boolean;
  size?: number;
  showDetails?: boolean;
  zoomLevel: 'far' | 'medium' | 'close';
}

export const PlayerAvatar: React.FC<PlayerAvatarProps> = ({
  player,
  position,
  isCurrentUser,
  size = 40,
  showDetails = true,
  zoomLevel
}) => {
  
  // ============ SIZE CALCULATIONS ============
  
  const getAvatarSize = (): number => {
    if (isCurrentUser) return size * 1.2;
    
    switch (zoomLevel) {
      case 'close': return size;
      case 'medium': return size * 0.8;
      case 'far': return size * 0.6;
      default: return size;
    }
  };
  
  const avatarSize = getAvatarSize();
  const shouldShowName = zoomLevel !== 'far' || isCurrentUser;
  const shouldShowStats = (zoomLevel === 'close' || isCurrentUser) && showDetails;
  
  // ============ RANK COLORS ============
  
  const getRankColor = (): string => {
    switch (player.rank) {
      case 1: return '#fbbf24'; // Gold
      case 2: return '#94a3b8'; // Silver
      case 3: return '#fb923c'; // Bronze
      default: return '#64748b'; // Default
    }
  };
  
  const getRankEmoji = (): string => {
    switch (player.rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return `#${player.rank}`;
    }
  };
  
  // ============ RENDER ============
  
  return (
    <g
      className={`player-avatar ${isCurrentUser ? 'current-user' : ''}`}
      transform={`translate(${position.x}, ${position.y})`}
      style={{
        transition: 'transform 0.5s ease-out',
        cursor: 'pointer'
      }}
    >
      {/* Outer glow ring (current user) */}
      {isCurrentUser && (
        <circle
          cx={0}
          cy={0}
          r={avatarSize / 2 + 6}
          fill="none"
          stroke={player.color}
          strokeWidth="3"
          opacity="0.3"
        >
          <animate
            attributeName="r"
            from={avatarSize / 2 + 6}
            to={avatarSize / 2 + 10}
            dur="2s"
            repeatCount="indefinite"
            values={`${avatarSize / 2 + 6}; ${avatarSize / 2 + 10}; ${avatarSize / 2 + 6}`}
          />
          <animate
            attributeName="opacity"
            from="0.3"
            to="0.1"
            dur="2s"
            repeatCount="indefinite"
            values="0.3; 0.1; 0.3"
          />
        </circle>
      )}
      
      {/* Avatar background circle */}
      <circle
        cx={0}
        cy={0}
        r={avatarSize / 2}
        fill="white"
        stroke={player.color}
        strokeWidth={isCurrentUser ? 4 : 3}
        filter="drop-shadow(0 4px 6px rgba(0,0,0,0.1))"
      />
      
      {/* Avatar image */}
      <clipPath id={`clip-avatar-${player.id}`}>
        <circle cx={0} cy={0} r={avatarSize / 2 - 4} />
      </clipPath>
      <image
        href={player.avatar_url}
        x={-(avatarSize / 2 - 4)}
        y={-(avatarSize / 2 - 4)}
        width={avatarSize - 8}
        height={avatarSize - 8}
        clipPath={`url(#clip-avatar-${player.id})`}
        preserveAspectRatio="xMidYMid slice"
      />
      
      {/* Rank badge (top right) */}
      <g transform={`translate(${avatarSize / 2 - 8}, ${-avatarSize / 2 + 8})`}>
        <circle
          cx={0}
          cy={0}
          r={12}
          fill={getRankColor()}
          stroke="white"
          strokeWidth="2"
          filter="drop-shadow(0 2px 4px rgba(0,0,0,0.2))"
        />
        <text
          x={0}
          y={4}
          fontSize="10"
          fill="white"
          textAnchor="middle"
          fontWeight="bold"
        >
          {player.rank <= 3 ? getRankEmoji() : player.rank}
        </text>
      </g>
      
      {/* Player name (below avatar) */}
      {shouldShowName && (
        <g transform={`translate(0, ${avatarSize / 2 + 20})`}>
          {/* Name background */}
          <rect
            x={-(player.name.length * 3.5)}
            y={-10}
            width={player.name.length * 7}
            height="18"
            rx="9"
            fill="white"
            stroke={player.color}
            strokeWidth={isCurrentUser ? 2 : 1}
            opacity="0.95"
          />
          
          {/* Name text */}
          <text
            x={0}
            y={3}
            fontSize={isCurrentUser ? "13" : "11"}
            fill={player.color}
            textAnchor="middle"
            fontWeight={isCurrentUser ? "700" : "600"}
          >
            {player.name}
            {isCurrentUser && ' 👤'}
          </text>
        </g>
      )}
      
      {/* Stats card (detailed view) */}
      {shouldShowStats && (
        <g transform={`translate(${avatarSize / 2 + 15}, ${-avatarSize / 2})`}>
          {/* Card background */}
          <rect
            width="140"
            height="85"
            rx="8"
            fill="white"
            stroke={player.color}
            strokeWidth="2"
            opacity="0.98"
            filter="drop-shadow(0 4px 8px rgba(0,0,0,0.15))"
          />
          
          {/* Stats content */}
          <g transform="translate(10, 15)">
            {/* Progress bar */}
            <text x={0} y={0} fontSize="10" fill="#64748b" fontWeight="600">
              İlerleme
            </text>
            <rect
              x={0}
              y={5}
              width="120"
              height="6"
              rx="3"
              fill="#e2e8f0"
            />
            <rect
              x={0}
              y={5}
              width={`${player.progress_percentage * 1.2}`}
              height="6"
              rx="3"
              fill={player.color}
            >
              <animate
                attributeName="width"
                from="0"
                to={`${player.progress_percentage * 1.2}`}
                dur="1s"
                fill="freeze"
              />
            </rect>
            <text x={125} y={10} fontSize="9" fill="#64748b" textAnchor="end">
              {Math.round(player.progress_percentage)}%
            </text>
            
            {/* Stats grid */}
            <g transform="translate(0, 25)">
              {/* Watched count */}
              <text x={0} y={0} fontSize="9" fill="#64748b">
                İzlenen:
              </text>
              <text x={120} y={0} fontSize="10" fill="#1e293b" fontWeight="600" textAnchor="end">
                {player.total_watched}
              </text>
              
              {/* Immediate watch */}
              <text x={0} y={15} fontSize="9" fill="#10b981">
                ⚡ Hızlı:
              </text>
              <text x={120} y={15} fontSize="10" fill="#10b981" fontWeight="600" textAnchor="end">
                {player.immediate_watch_count}
              </text>
              
              {/* Late watch */}
              <text x={0} y={30} fontSize="9" fill="#f59e0b">
                🕐 Geç:
              </text>
              <text x={120} y={30} fontSize="10" fill="#f59e0b" fontWeight="600" textAnchor="end">
                {player.late_watch_count}
              </text>
              
              {/* Points */}
              <line x1={0} y1={37} x2={120} y2={37} stroke="#e2e8f0" strokeWidth="1" />
              <text x={0} y={50} fontSize="9" fill="#64748b">
                Toplam Puan:
              </text>
              <text x={120} y={50} fontSize="11" fill={player.color} fontWeight="700" textAnchor="end">
                {player.points.toLocaleString('tr-TR')}
              </text>
            </g>
          </g>
        </g>
      )}
      
      {/* Movement indicator (arrow) */}
      {player.total_watched > 0 && zoomLevel !== 'far' && (
        <g transform={`translate(${avatarSize / 2 + 8}, 0)`}>
          <path
            d="M 0 -5 L 8 0 L 0 5 Z"
            fill={player.color}
            opacity="0.6"
          >
            <animateTransform
              attributeName="transform"
              type="translate"
              values="0 0; 5 0; 0 0"
              dur="1.5s"
              repeatCount="indefinite"
            />
          </path>
        </g>
      )}
      
      {/* Current user crown */}
      {isCurrentUser && player.rank === 1 && (
        <g transform={`translate(0, ${-avatarSize / 2 - 10})`}>
          <text
            x={0}
            y={0}
            fontSize="20"
            textAnchor="middle"
          >
            👑
          </text>
        </g>
      )}
    </g>
  );
};

// ============ MINI AVATAR (for leaderboard) ============

interface MiniAvatarProps {
  player: RacePlayer;
  size?: number;
  showRank?: boolean;
}

export const MiniAvatar: React.FC<MiniAvatarProps> = ({
  player,
  size = 32,
  showRank = true
}) => {
  return (
    <div className="inline-flex items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <img
          src={player.avatar_url}
          alt={player.name}
          className="rounded-full"
          style={{
            width: size,
            height: size,
            border: `2px solid ${player.color}`
          }}
        />
        {showRank && (
          <div
            className="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold text-white"
            style={{
              backgroundColor: player.rank <= 3 
                ? (player.rank === 1 ? '#fbbf24' : player.rank === 2 ? '#94a3b8' : '#fb923c')
                : '#64748b'
            }}
          >
            {player.rank}
          </div>
        )}
      </div>
      <div className="flex flex-col">
        <span className="text-sm font-semibold" style={{ color: player.color }}>
          {player.name}
        </span>
        <span className="text-xs text-gray-500">
          {player.points.toLocaleString('tr-TR')} puan
        </span>
      </div>
    </div>
  );
};

// ============ AVATAR TRAIL (movement history) ============

interface AvatarTrailProps {
  positions: { x: number; y: number }[];
  color: string;
  opacity?: number;
}

export const AvatarTrail: React.FC<AvatarTrailProps> = ({
  positions,
  color,
  opacity = 0.2
}) => {
  if (positions.length < 2) return null;
  
  const pathData = positions
    .map((pos, idx) => `${idx === 0 ? 'M' : 'L'} ${pos.x} ${pos.y}`)
    .join(' ');
  
  return (
    <path
      d={pathData}
      fill="none"
      stroke={color}
      strokeWidth="2"
      strokeDasharray="5,3"
      opacity={opacity}
      strokeLinecap="round"
    />
  );
};

// ============ EXPORTS ============

export default PlayerAvatar;