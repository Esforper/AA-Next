// src/data/mockRaceData.ts

/**
 * Mock Race Data - Haftalık yarış için örnek veriler
 * 5 oyuncu, Ekonomi kategorisi, 20 haber node'u
 */

import {
  WeeklyRaceData,
  NewsNodeData,
  RacePlayer,
  PlayerNewsView,
  WatchStatus,
  NewsCategory,
  PlayerLane,
  PLAYER_COLORS,
  calculateWatchStatus
} from '../types/raceGameTypes';

// ============ MOCK PLAYERS ============

const mockPlayers: RacePlayer[] = [
  {
    id: "user_001",
    name: "Sen",
    avatar_url: "https://i.pravatar.cc/150?img=1",
    lane: PlayerLane.LANE_1,
    total_watched: 18,
    current_node_index: 18,
    progress_percentage: 90.0,
    rank: 1,
    points: 2850,
    immediate_watch_count: 15,
    late_watch_count: 3,
    color: PLAYER_COLORS[0].primary,
    is_current_user: true
  },
  {
    id: "user_002",
    name: "Ahmet_34",
    avatar_url: "https://i.pravatar.cc/150?img=12",
    lane: PlayerLane.LANE_2,
    total_watched: 16,
    current_node_index: 16,
    progress_percentage: 80.0,
    rank: 2,
    points: 2450,
    immediate_watch_count: 12,
    late_watch_count: 4,
    color: PLAYER_COLORS[1].primary,
    is_current_user: false
  },
  {
    id: "user_003",
    name: "Zeynep_TR",
    avatar_url: "https://i.pravatar.cc/150?img=5",
    lane: PlayerLane.LANE_3,
    total_watched: 14,
    current_node_index: 14,
    progress_percentage: 70.0,
    rank: 3,
    points: 2100,
    immediate_watch_count: 10,
    late_watch_count: 4,
    color: PLAYER_COLORS[2].primary,
    is_current_user: false
  },
  {
    id: "user_004",
    name: "Mehmet_67",
    avatar_url: "https://i.pravatar.cc/150?img=8",
    lane: PlayerLane.LANE_4,
    total_watched: 12,
    current_node_index: 12,
    progress_percentage: 60.0,
    rank: 4,
    points: 1800,
    immediate_watch_count: 7,
    late_watch_count: 5,
    color: PLAYER_COLORS[3].primary,
    is_current_user: false
  },
  {
    id: "user_005",
    name: "Ayşe_06",
    avatar_url: "https://i.pravatar.cc/150?img=9",
    lane: PlayerLane.LANE_5,
    total_watched: 10,
    current_node_index: 10,
    progress_percentage: 50.0,
    rank: 5,
    points: 1500,
    immediate_watch_count: 6,
    late_watch_count: 4,
    color: PLAYER_COLORS[4].primary,
    is_current_user: false
  }
];

// ============ MOCK NEWS TITLES ============

const mockNewsTitles = [
  "Merkez Bankası faiz kararını açıkladı: Yüzde 50'de sabit",
  "Dolar/TL 34.50 seviyesini gördü, piyasalar karışık",
  "Enflasyon rakamları beklentilerin üzerinde geldi",
  "İhracat rakamları ocak ayında rekor kırdı",
  "Bütçe açığı hedeflenen seviyenin altında",
  "Borsa İstanbul 10.000 puanı aştı",
  "Altın fiyatları yeni zirveye ulaştı",
  "Asgari ücret artışı gündemde: Uzmanlar ne diyor?",
  "KDV indirimi hangi ürünleri kapsayacak?",
  "Emekli maaşlarına zam açıklandı",
  "Elektrik ve doğalgaz zamları belli oldu",
  "Kredi faiz oranları düşüyor mu?",
  "Konut fiyatları yıllık yüzde 120 arttı",
  "Tarım sektöründe yeni teşvik paketi",
  "Otomotiv sektörü ihracatta zirvede",
  "E-ihracat platformu kullanıma açıldı",
  "Yatırım teşvik belgesi başvuruları arttı",
  "İşsizlik oranı yüzde 9.2'ye geriledi",
  "Turizm geliri 60 milyar doları aştı",
  "Yeni ekonomi programı detayları açıklandı"
];

// ============ HELPER: Generate Player Views ============

function generatePlayerViews(nodeIndex: number, publishedDate: Date): {
  [player_id: string]: PlayerNewsView;
} {
  const views: { [player_id: string]: PlayerNewsView } = {};
  
  mockPlayers.forEach((player) => {
    const hasWatched = nodeIndex < player.current_node_index;
    
    if (hasWatched) {
      // İzlenme zamanını hesapla (publish date'den 2-30 saat sonra)
      const hoursAfter = Math.random() * 48; // 0-48 saat arası
      const watchedDate = new Date(publishedDate.getTime() + hoursAfter * 60 * 60 * 1000);
      
      const watchStatus = calculateWatchStatus(
        publishedDate.toISOString(),
        watchedDate.toISOString()
      );
      
      views[player.id] = {
        watched: true,
        watched_at: watchedDate.toISOString(),
        watch_status: watchStatus,
        duration_seconds: Math.floor(Math.random() * 30) + 10 // 10-40 saniye
      };
    } else {
      views[player.id] = {
        watched: false,
        watch_status: WatchStatus.UNWATCHED
      };
    }
  });
  
  return views;
}

// ============ MOCK NEWS NODES ============

function generateMockNewsNodes(): NewsNodeData[] {
  const nodes: NewsNodeData[] = [];
  const weekStart = new Date("2025-01-06T00:00:00Z"); // Pazartesi
  
  mockNewsTitles.forEach((title, index) => {
    // Her haberi farklı günlere ve saatlere dağıt
    const dayOffset = Math.floor(index / 3); // Her gün 3 haber
    const hourOffset = (index % 3) * 8 + 9; // 09:00, 17:00, 01:00 (ertesi gün)
    
    const publishedDate = new Date(weekStart);
    publishedDate.setDate(publishedDate.getDate() + dayOffset);
    publishedDate.setHours(hourOffset, 0, 0, 0);
    
    const weekDay = publishedDate.getDay() || 7; // 1-7 (Pazartesi-Pazar)
    
    // İlişkili haberler (basit: bir önceki ve sonraki)
    const relatedIds: string[] = [];
    if (index > 0) relatedIds.push(`news_${index - 1}`);
    if (index < mockNewsTitles.length - 1) relatedIds.push(`news_${index + 1}`);
    
    // Bazı haberler için ekstra ilişkili (aynı konu)
    if (index === 2) relatedIds.push("news_0"); // Enflasyon + Faiz
    if (index === 7) relatedIds.push("news_9"); // Asgari ücret + Emekli maaşı
    
    nodes.push({
      id: `news_${index}`,
      reel_id: `reel_${1000 + index}`,
      title: title,
      summary: `${title.substring(0, 80)}... detaylar haberimizde.`,
      category: NewsCategory.EKONOMI,
      published_at: publishedDate.toISOString(),
      week_day: weekDay,
      order_in_week: index,
      position: {
        index: index,
        progress: index / (mockNewsTitles.length - 1) // 0.0 - 1.0
      },
      player_views: generatePlayerViews(index, publishedDate),
      related_news_ids: relatedIds,
      thumbnail_url: `https://picsum.photos/seed/news${index}/400/300`
    });
  });
  
  return nodes;
}

// ============ MOCK WEEKLY RACE DATA ============

export const mockWeeklyRaceData: WeeklyRaceData = {
  week_id: "2025-W02",
  week_start: "2025-01-06",
  week_end: "2025-01-12",
  current_day: 5, // Cuma
  
  category: NewsCategory.EKONOMI,
  category_display_name: "Ekonomi Haberleri",
  
  news_nodes: generateMockNewsNodes(),
  total_news_count: mockNewsTitles.length,
  
  players: mockPlayers,
  current_user_id: "user_001",
  
  is_active: true,
  time_remaining_hours: 60, // 2.5 gün kaldı
  
  created_at: "2025-01-06T00:00:00Z",
  last_updated: new Date().toISOString()
};

// ============ MOCK NODE DETAIL DATA ============

export function getMockNodeDetail(nodeId: string) {
  const node = mockWeeklyRaceData.news_nodes.find(n => n.id === nodeId);
  if (!node) return null;
  
  // İlişkili haberleri bul
  const relatedNodes = mockWeeklyRaceData.news_nodes.filter(
    n => node.related_news_ids.includes(n.id)
  );
  
  // NLP bağlantıları (mock)
  const nlpConnections = relatedNodes.map(relNode => ({
    from_news_id: node.id,
    to_news_id: relNode.id,
    connection_type: "same_topic" as const,
    similarity_score: 0.75 + Math.random() * 0.2, // 0.75-0.95
    explanation: `Her iki haber de "${NewsCategory.EKONOMI}" kategorisi ile ilgili`
  }));
  
  // Tüm oyuncuların bu haberi izleme durumu
  const allPlayerViews = mockPlayers.map(player => ({
    player: player,
    view_status: node.player_views[player.id]
  }));
  
  return {
    node: node,
    related_nodes: relatedNodes,
    nlp_connections: nlpConnections,
    all_player_views: allPlayerViews
  };
}

// ============ UTILITY FUNCTIONS ============

/**
 * Yeni haber ekle (hafta içinde dinamik ekleme simülasyonu)
 */
export function addNewMockNews(title: string): NewsNodeData {
  const currentNodes = mockWeeklyRaceData.news_nodes;
  const newIndex = currentNodes.length;
  
  const now = new Date();
  const weekDay = now.getDay() || 7;
  
  const newNode: NewsNodeData = {
    id: `news_${newIndex}`,
    reel_id: `reel_${1000 + newIndex}`,
    title: title,
    summary: `${title.substring(0, 80)}... detaylar haberimizde.`,
    category: NewsCategory.EKONOMI,
    published_at: now.toISOString(),
    week_day: weekDay,
    order_in_week: newIndex,
    position: {
      index: newIndex,
      progress: 1.0 // Son node
    },
    player_views: generatePlayerViews(newIndex, now),
    related_news_ids: [`news_${newIndex - 1}`], // Son haberle ilişkili
    thumbnail_url: `https://picsum.photos/seed/news${newIndex}/400/300`
  };
  
  mockWeeklyRaceData.news_nodes.push(newNode);
  mockWeeklyRaceData.total_news_count++;
  
  return newNode;
}

/**
 * Kullanıcının bir haberi izlediğini simüle et
 */
export function markNewsAsWatched(nodeId: string, userId: string = "user_001") {
  const node = mockWeeklyRaceData.news_nodes.find(n => n.id === nodeId);
  if (!node) return;
  
  const player = mockPlayers.find(p => p.id === userId);
  if (!player) return;
  
  const now = new Date();
  const watchStatus = calculateWatchStatus(node.published_at, now.toISOString());
  
  node.player_views[userId] = {
    watched: true,
    watched_at: now.toISOString(),
    watch_status: watchStatus,
    duration_seconds: 25
  };
  
  // Player stats güncelle
  player.total_watched++;
  player.current_node_index = Math.max(player.current_node_index, node.position.index + 1);
  player.progress_percentage = (player.total_watched / mockWeeklyRaceData.total_news_count) * 100;
  
  if (watchStatus === WatchStatus.WATCHED_IMMEDIATE) {
    player.immediate_watch_count++;
    player.points += 150;
  } else {
    player.late_watch_count++;
    player.points += 100;
  }
}

// ============ EXPORTS ============

export { mockPlayers };