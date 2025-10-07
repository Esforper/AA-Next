// Models for Haber Ağacı (Reels Tree)

export interface ReelTreeNode {
  id: string;
  title: string;
  thumbnailUrl: string;
  articleId?: string; // must reference articleId when available
  publishedAt?: string; // ISO date string for sorting
}

export interface ReelTreeEdge {
  fromId: string; // previous
  toId: string;   // next
}

export interface ReelsTreePayload {
  nodes: ReelTreeNode[];
  edges: ReelTreeEdge[];
}

export interface ReelsTreeResponse {
  success: boolean;
  message?: string;
  data: ReelsTreePayload;
}


