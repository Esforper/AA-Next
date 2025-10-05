import { useCallback, useMemo, useRef, useState } from 'react';
import { ReelTreeNode, ReelTreeEdge } from '../models/ReelsTreeModels';
import { ReelsApi } from '../api/reelsApi';

export interface ReelsTreeViewModel {
  nodes: ReelTreeNode[];
  edges: ReelTreeEdge[];
  loading: boolean;
  error?: string;
  scale: number;
  translate: { x: number; y: number };
  fetchTree: () => Promise<void>;
  setScale: (s: number) => void;
  setTranslate: (t: { x: number; y: number }) => void;
  resetView: () => void;
}

const MIN_SCALE = 0.4;
const MAX_SCALE = 2.4;

export function useReelsTreeViewModel(): ReelsTreeViewModel {
  const [nodes, setNodes] = useState<ReelTreeNode[]>([]);
  const [edges, setEdges] = useState<ReelTreeEdge[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | undefined>();

  // Start a bit smaller by default
  const [scale, setScaleState] = useState<number>(0.7);
  const [translate, setTranslateState] = useState<{ x: number; y: number }>({ x: -60, y: 0 });

  const lastFetchRef = useRef<number>(0);

  const fetchTree = useCallback(async (): Promise<void> => {
    // simple SWR: 5s cache window
    const now = Date.now();
    if (now - lastFetchRef.current < 5000 && nodes.length > 0) return;
    setLoading(true);
    setError(undefined);
    try {
      const feed = await ReelsApi.fetchInfiniteFeed({ limit: 30 });
      const reels = feed.reels || [];

      // Build nodes from existing reels data
      const nodesBuilt: ReelTreeNode[] = reels.map((r: any) => ({
        id: String(r.id),
        title: r.title || r.summary || 'Reel',
        thumbnailUrl: r.main_image || (Array.isArray(r.images) && r.images[0]) || '',
        articleId: (r as any).articleId,
        publishedAt: (r as any).published_at
      }));

      // Sort: newest first (top)
      nodesBuilt.sort((a, b) => {
        const ta = a.publishedAt ? Date.parse(a.publishedAt) : 0;
        const tb = b.publishedAt ? Date.parse(b.publishedAt) : 0;
        return tb - ta;
      });

      // Edges: from older → newer (so arrows go upward)
      const edgesBuilt: ReelTreeEdge[] = [];
      for (let i = nodesBuilt.length - 1; i > 0; i--) {
        edgesBuilt.push({ fromId: nodesBuilt[i].id, toId: nodesBuilt[i - 1].id });
      }

      setNodes(nodesBuilt);
      setEdges(edgesBuilt);
      lastFetchRef.current = now;
    } catch (e: any) {
      setError(e?.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [nodes.length]);

  const setScale = useCallback((s: number) => {
    const clamped = Math.max(MIN_SCALE, Math.min(MAX_SCALE, s));
    setScaleState(clamped);
  }, []);

  const setTranslate = useCallback((t: { x: number; y: number }) => {
    setTranslateState(t);
  }, []);

  const resetView = useCallback(() => {
    setScaleState(1);
    setTranslateState({ x: 0, y: 0 });
  }, []);

  return useMemo(() => ({
    nodes,
    edges,
    loading,
    error,
    scale,
    translate,
    fetchTree,
    setScale,
    setTranslate,
    resetView
  }), [nodes, edges, loading, error, scale, translate, fetchTree, setScale, setTranslate, resetView]);
}


