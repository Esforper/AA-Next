// src/components/race/NodeDetailModal.tsx

/**
 * NodeDetailModal Component
 * Node'a tıklandığında açılan detay modal
 * Merkez: Ana haber, Etrafında: İlişkili haberler (NLP bağlantılı)
 */

import React, { useState } from 'react';
import {
  NodeDetailData,
  NewsNodeData,
  getNodeColor,
  WatchStatus
} from '../../types/raceGameTypes';
import { MiniNode } from './NewsNode';

interface NodeDetailModalProps {
  nodeDetail: NodeDetailData;
  onClose: () => void;
  onWatchNews: (nodeId: string) => void;
}

export const NodeDetailModal: React.FC<NodeDetailModalProps> = ({
  nodeDetail,
  onClose,
  onWatchNews
}) => {
  
  const [selectedRelatedNode, setSelectedRelatedNode] = useState<NewsNodeData | null>(null);
  
  const { node, related_nodes, nlp_connections, all_player_views } = nodeDetail;
  
  // ============ HELPERS ============
  
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  const getConnectionExplanation = (relatedNodeId: string): string => {
    const connection = nlp_connections.find(c => c.to_news_id === relatedNodeId);
    return connection?.explanation || 'İlişkili haber';
  };
  
  const getSimilarityScore = (relatedNodeId: string): number => {
    const connection = nlp_connections.find(c => c.to_news_id === relatedNodeId);
    return connection?.similarity_score || 0;
  };
  
  // ============ RENDER ============
  
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="relative bg-white rounded-2xl shadow-2xl max-w-5xl w-full mx-4 max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 w-10 h-10 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-600 hover:text-gray-900 transition-colors"
          title="Kapat (ESC)"
        >
          ✕
        </button>
        
        {/* Scrollable Content */}
        <div className="overflow-y-auto max-h-[90vh] p-8">
          
          {/* Main News Card */}
          <div className="mb-8">
            <div className="flex items-start gap-6">
              {/* Thumbnail */}
              {node.thumbnail_url && (
                <img
                  src={node.thumbnail_url}
                  alt={node.title}
                  className="w-48 h-32 object-cover rounded-lg shadow-md flex-shrink-0"
                />
              )}
              
              {/* Content */}
              <div className="flex-1">
                {/* Category Badge */}
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold mb-3">
                  <span>{node.category}</span>
                  <span className="text-blue-400">•</span>
                  <span className="text-xs text-blue-600">{formatDate(node.published_at)}</span>
                </div>
                
                {/* Title */}
                <h2 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">
                  {node.title}
                </h2>
                
                {/* Summary */}
                <p className="text-gray-600 text-lg leading-relaxed mb-6">
                  {node.summary}
                </p>
                
                {/* Action Buttons */}
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => onWatchNews(node.id)}
                    className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-semibold shadow-md hover:shadow-lg transition-all flex items-center gap-2"
                  >
                    <span>▶</span>
                    <span>Haberi İzle</span>
                  </button>
                  
                  <button
                    className="px-6 py-3 bg-white border-2 border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
                  >
                    <span>🔖</span>
                    <span>Favorilere Ekle</span>
                  </button>
                  
                  <button
                    className="px-6 py-3 bg-white border-2 border-gray-300 hover:border-gray-400 text-gray-700 rounded-lg font-semibold transition-colors flex items-center gap-2"
                  >
                    <span>📤</span>
                    <span>Paylaş</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Divider */}
          <div className="border-t border-gray-200 my-8"></div>
          
          {/* All Players Status */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              👥 Oyuncuların Durumu
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {all_player_views.map(({ player, view_status }) => {
                const nodeColor = getNodeColor(view_status);
                const isWatched = view_status.watched;
                
                return (
                  <div
                    key={player.id}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      isWatched 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <img
                        src={player.avatar_url}
                        alt={player.name}
                        className="w-8 h-8 rounded-full border-2"
                        style={{ borderColor: player.color }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-semibold text-gray-900 truncate">
                          {player.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          #{player.rank}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: nodeColor }}
                      ></div>
                      <span className="text-xs font-medium text-gray-600">
                        {isWatched 
                          ? view_status.watch_status === WatchStatus.WATCHED_IMMEDIATE
                            ? '⚡ Hızlı izledi'
                            : '🕐 Geç izledi'
                          : '○ İzlemedi'}
                      </span>
                    </div>
                    
                    {isWatched && view_status.watched_at && (
                      <div className="text-xs text-gray-400 mt-1">
                        {formatDate(view_status.watched_at)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Divider */}
          <div className="border-t border-gray-200 my-8"></div>
          
          {/* Related News (NLP Connections) */}
          {related_nodes.length > 0 && (
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                🔗 İlişkili Haberler
                <span className="text-sm font-normal text-gray-500">
                  (NLP analizi ile bağlantılı)
                </span>
              </h3>
              
              {/* Related News Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {related_nodes.map((relatedNode) => {
                  const similarity = getSimilarityScore(relatedNode.id);
                  const explanation = getConnectionExplanation(relatedNode.id);
                  const isSelected = selectedRelatedNode?.id === relatedNode.id;
                  
                  return (
                    <div
                      key={relatedNode.id}
                      className={`p-4 rounded-lg border-2 transition-all cursor-pointer hover:shadow-md ${
                        isSelected 
                          ? 'border-blue-400 bg-blue-50' 
                          : 'border-gray-200 bg-white hover:border-gray-300'
                      }`}
                      onClick={() => setSelectedRelatedNode(isSelected ? null : relatedNode)}
                    >
                      <div className="flex items-start gap-3">
                        {/* Mini Node Icon */}
                        <div className="flex-shrink-0 mt-1">
                          <MiniNode
                            node={relatedNode}
                            currentPlayer={all_player_views[0].player}
                            size={10}
                          />
                        </div>
                        
                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {/* Similarity Badge */}
                          <div className="flex items-center gap-2 mb-2">
                            <div className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs font-semibold">
                              {Math.round(similarity * 100)}% benzerlik
                            </div>
                            <div className="text-xs text-gray-400">
                              {relatedNode.category}
                            </div>
                          </div>
                          
                          {/* Title */}
                          <h4 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2">
                            {relatedNode.title}
                          </h4>
                          
                          {/* NLP Explanation */}
                          <p className="text-xs text-gray-600 mb-3 italic">
                            💡 {explanation}
                          </p>
                          
                          {/* Summary (collapsed by default) */}
                          {isSelected && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <p className="text-sm text-gray-700 leading-relaxed">
                                {relatedNode.summary}
                              </p>
                              
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onWatchNews(relatedNode.id);
                                }}
                                className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-semibold transition-colors"
                              >
                                Bu Haberi İzle →
                              </button>
                            </div>
                          )}
                          
                          {/* Date */}
                          <div className="text-xs text-gray-400 mt-2">
                            {formatDate(relatedNode.published_at)}
                          </div>
                        </div>
                        
                        {/* Thumbnail (small) */}
                        {relatedNode.thumbnail_url && (
                          <img
                            src={relatedNode.thumbnail_url}
                            alt={relatedNode.title}
                            className="w-20 h-14 object-cover rounded flex-shrink-0"
                          />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* Connection Visualization (Optional) */}
              <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-purple-600 font-semibold text-sm">
                    🧠 NLP Analizi
                  </span>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed">
                  Bu haberler, içerik benzerliği, ortak varlıklar (kişi, yer, kurum) ve 
                  zaman çizelgesi analizi ile otomatik olarak ilişkilendirilmiştir. 
                  Benzerlik skorları {Math.round(Math.min(...nlp_connections.map(c => c.similarity_score)) * 100)}% 
                  ile {Math.round(Math.max(...nlp_connections.map(c => c.similarity_score)) * 100)}% arasında değişmektedir.
                </p>
              </div>
            </div>
          )}
          
          {/* No Related News */}
          {related_nodes.length === 0 && (
            <div className="text-center py-8">
              <div className="text-4xl mb-2">🔍</div>
              <p className="text-gray-500">Bu haber için henüz ilişkili haber bulunamadı.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NodeDetailModal;