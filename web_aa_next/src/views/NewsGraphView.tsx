// src/views/NewsGraphView.tsx

import React, { useMemo } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
  Node,
  Edge,
  MarkerType,
} from 'reactflow';

import 'reactflow/dist/style.css';

import { ArticleNode } from '../components/ArticleNode';
import { ArticleData } from '../models';
import { Card } from '../components';

// 1. Gelişmiş Mock (Sahte) Veri Senaryosu
// Senaryo: İki ana haber akışı var.
// A) UZUN VADELİ GÜNDEM: Hükümetin "Dijital Lira" projesi.
// B) ANİ GELİŞME: Bu projede çalışan önemli bir mühendisin öldürülmesi.
// KESİŞİM NOKTASI: Cinayet haberi, Dijital Lira projesini doğrudan etkiliyor ve iki akış birleşiyor.

const mockArticles: ArticleData[] = [
  // --- AKIŞ A: Dijital Lira Projesi (Ana Gündem) ---
  {
    id: 'dl-1',
    title: "MegaCorp 'Dijital Lira' Projesini Duyurdu",
    summary: 'Türkiye\'nin önde gelen teknoloji firması MegaCorp, Merkez Bankası ile ortaklaşa yürütülecek Dijital Lira projesinin startını verdi.',
    category: 'Ekonomi',
    published_date: '2023-11-01T10:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1639755243888-8041d576a4a6?q=80&w=1600',
    tags: ['Ekonomi', 'Teknoloji', 'DijitalLira'],
    content: '', images: [],
  },
  {
    id: 'dl-2',
    title: "Meclis'ten Dijital Lira İçin Yasal Düzenleme Sinyali",
    summary: 'Meclis Plan ve Bütçe Komisyonu, Dijital Lira\'nın yasal altyapısını oluşturacak yeni kanun teklifi üzerinde çalışmalara başladı.',
    category: 'Siyaset',
    published_date: '2023-11-05T14:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1588699201399-2c9c3315a4e6?q=80&w=1600',
    tags: ['Meclis', 'Yasa', 'Siyaset'],
    content: '', images: [],
  },

  // --- KESİŞİM NOKTASI: Cinayet haberi iki akışı birbirine bağlıyor ---
  {
    id: 'event-murder',
    title: 'Dijital Lira Projesinin Kilit İsmi Öldürüldü',
    summary: 'Projenin baş mühendisi Ali Vural, Beşiktaş\'taki evinde ölü bulundu. Polis, olayın cinayet olduğunu ve proje belgelerinin çalındığını açıkladı.',
    category: 'Gündem',
    published_date: '2023-11-10T09:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1580753497689-8a24731c385b?q=80&w=1600',
    tags: ['Cinayet', 'Skandal', 'Gündem'],
    content: '', images: [],
  },
  
  // --- AKIŞ B: Cinayet Soruşturması (Yan Dal) ---
  {
    id: 'cm-1',
    title: 'Cinayet Soruşturmasında İlk Şüpheli Gözaltında',
    summary: 'Polis, mühendis Ali Vural\'ın eski bir iş ortağı olan Burak Sönmez\'i sorgulamak üzere gözaltına aldı. Sönmez suçlamaları reddetti.',
    category: 'Asayiş',
    published_date: '2023-11-11T18:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1599494252327-248e9323c10a?q=80&w=1600',
    tags: ['Polis', 'Soruşturma', 'Asayiş'],
    content: '', images: [],
  },
  {
    id: 'cm-2',
    title: "Kayıp Veri Diski Cinayetin Kilit Kanıtı Olabilir",
    summary: 'Emniyet, Ali Vural\'a ait olduğu düşünülen ve kritik proje verilerini içeren bir hard diskin peşine düştü. Diskin cinayetin sebebini aydınlatacağı düşünülüyor.',
    category: 'Asayiş',
    published_date: '2023-11-14T11:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1593111244799-35b6443c5b4e?q=80&w=1600',
    tags: ['Kanıt', 'Operasyon'],
    content: '', images: [],
  },

  // --- AKIŞ A'nın Devamı: Cinayetin Projeye Etkisi ---
  {
    id: 'dl-3',
    title: "Skandal Sonrası MegaCorp Hisseleri Çakıldı",
    summary: 'Baş mühendisin öldürülmesi ve proje verilerinin çalındığı iddiaları üzerine MegaCorp hisseleri Borsa İstanbul\'da gün içinde %15 değer kaybetti.',
    category: 'Ekonomi',
    published_date: '2023-11-10T13:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?q=80&w=1600',
    tags: ['Borsa', 'Ekonomi', 'Kriz'],
    content: '', images: [],
  },
  {
    id: 'dl-4',
    title: "MegaCorp Projeyi Geçici Olarak Askıya Aldığını Açıkladı",
    summary: 'Yaşanan güvenlik açığı ve kriz nedeniyle MegaCorp, Dijital Lira projesinin soruşturma tamamlanana kadar askıya alındığını duyurdu.',
    category: 'Ekonomi',
    published_date: '2023-11-15T17:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1605152276399-5266c1be7b0a?q=80&w=1600',
    tags: ['Durdurma', 'Güvenlik'],
    content: '', images: [],
  },
    
  // --- BİRLEŞME NOKTASI: İki akışın sonucunu özetleyen haber ---
  {
    id: 'summary-1',
    title: "Cinayet Çözüldü, Proje Yeniden Başlıyor",
    summary: 'Polisin kayıp diski bulup şüpheliyi yakalamasının ardından, MegaCorp güçlendirilmiş güvenlik önlemleriyle Dijital Lira projesine yeniden başlayacağını açıkladı.',
    category: 'Gündem',
    published_date: '2023-11-20T15:00:00Z',
    main_image: 'https://images.unsplash.com/photo-1642139436885-307a011a7a0b?q=80&w=1600',
    tags: ['Gündem', 'Çözüm', 'Gelecek'],
    content: '', images: [],
  }
];

// 2. Yeni Senaryoya Göre Düğümlerin ve Bağlantıların Konumlandırılması
const initialNodes: Node[] = [
  { id: 'dl-1', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'dl-1') }, position: { x: 250, y: 0 } },
  { id: 'dl-2', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'dl-2') }, position: { x: 250, y: 250 } },
  { id: 'event-murder', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'event-murder') }, position: { x: 250, y: 500 } },
  { id: 'dl-3', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'dl-3') }, position: { x: 0, y: 750 } },
  { id: 'cm-1', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'cm-1') }, position: { x: 500, y: 750 } },
  { id: 'cm-2', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'cm-2') }, position: { x: 500, y: 1000 } },
  { id: 'dl-4', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'dl-4') }, position: { x: 0, y: 1000 } },
  { id: 'summary-1', type: 'articleNode', data: { article: mockArticles.find(a => a.id === 'summary-1') }, position: { x: 250, y: 1250 } },
];

const initialEdges: Edge[] = [
  // Ana Akış (Dijital Lira)
  { id: 'e-dl1-dl2', source: 'dl-1', target: 'dl-2', type: 'smoothstep', animated: true },
  { id: 'e-dl2-murder', source: 'dl-2', target: 'event-murder', type: 'smoothstep', animated: true },
  
  // Kesişim Sonrası Dallanma
  { id: 'e-murder-dl3', source: 'event-murder', target: 'dl-3', type: 'smoothstep', label: 'Ekonomik Etki', animated: true },
  { id: 'e-murder-cm1', source: 'event-murder', target: 'cm-1', type: 'smoothstep', label: 'Soruşturma Başladı', animated: true },
  
  // Yan Dal (Cinayet Soruşturması)
  { id: 'e-cm1-cm2', source: 'cm-1', target: 'cm-2', type: 'smoothstep', animated: true },
  
  // Ana Akışın Devamı
  { id: 'e-dl3-dl4', source: 'dl-3', target: 'dl-4', type: 'smoothstep', animated: true },
  
  // Dalların Birleşmesi
  { id: 'e-dl4-summary', source: 'dl-4', target: 'summary-1', type: 'smoothstep', animated: true },
  { id: 'e-cm2-summary', source: 'cm-2', target: 'summary-1', type: 'smoothstep', animated: true },
];

const edgeOptions = {
    markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#A0A0A0',
    },
    style: {
        strokeWidth: 2,
        stroke: '#A0A0A0',
    },
};

export const NewsGraphView: React.FC = () => {
  const nodeTypes = useMemo(() => ({ articleNode: ArticleNode }), []);

  return (
    <Card padding="lg" shadow="lg" className="w-full">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Haber Akış Grafiği (Demo)</h2>
        <p className="text-gray-600 mt-2 max-w-2xl mx-auto">
          Bu özellik, birbiriyle ilişkili haberleri kronolojik ve tematik bir ağaç yapısında görselleştirir. 
          Farklı haber akışlarının nasıl birleşip ayrıldığını görebilirsiniz.
        </p>
      </div>

      <div className="w-full h-[70vh] rounded-lg overflow-hidden border border-gray-200 bg-gray-50">
        <ReactFlow
          nodes={initialNodes}
          edges={initialEdges}
          nodeTypes={nodeTypes}
          defaultEdgeOptions={edgeOptions}
          fitView
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={true}
          attributionPosition="bottom-right"
        >
          <Controls />
          <MiniMap nodeStrokeWidth={3} zoomable pannable />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
    </Card>
  );
};