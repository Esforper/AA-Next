import React, { useMemo } from 'react';
import clsx from 'clsx';
import { useNewsViewModel } from '../viewmodels/useNewsViewModel';
import NewsCard from '../components/NewsCard.jsx';
import { LoadingSpinner } from '../components';

const palette = {
  navy: '#0C2340',
  red: '#E10600',
  white: '#FFFFFF',
  gray: '#F4F4F4'
};

const categories = ['All', 'Politics', 'Economy', 'Sports', 'Technology'];

export const NewsSection = () => {
  const { news, loading, error, hasMore, category, setCategory, refresh, loadMore } = useNewsViewModel();

  const topNews = useMemo(() => news.slice(0, 5), [news]);
  const restNews = useMemo(() => news.slice(5), [news]);

  return (
    <div className="w-full" style={{ backgroundColor: palette.gray }}>
      {/* Headline banner */}
      <div className="w-full">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <h2 className="text-2xl sm:text-3xl font-bold" style={{ color: palette.navy }}>
              Gündem Haberleri
            </h2>
            <div className="flex items-center gap-2 overflow-x-auto">
              {categories.map((c) => (
                <button
                  key={c}
                  onClick={() => setCategory(c === 'All' ? '' : c)}
                  className={clsx(
                    'px-4 py-2 rounded-full border text-sm whitespace-nowrap transition-colors',
                    c === (category || 'All') ? 'text-white' : 'text-gray-700'
                  )}
                  style={{
                    backgroundColor: c === (category || 'All') ? palette.navy : palette.white,
                    borderColor: palette.navy
                  }}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Top news carousel (mobile-first) */}
      <div className="sm:hidden">
        <div className="flex gap-4 overflow-x-auto no-scrollbar px-4 pb-4">
          {topNews.map((n) => (
            <div key={n.id} className="min-w-[85%]">
              <NewsCard
                title={n.title}
                description={n.description}
                imageUrl={n.imageUrl}
                onReadMore={() => window.open(n.url || '#', '_blank')}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Desktop headline banner image style (optional) */}
      <div className="hidden sm:block">
        {topNews[0] ? (
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="relative w-full h-72 rounded-xl overflow-hidden shadow-md">
              {topNews[0].imageUrl ? (
                <img src={topNews[0].imageUrl} alt={topNews[0].title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full" style={{ backgroundColor: palette.gray }} />
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-0 p-6">
                <h3 className="text-2xl font-bold text-white drop-shadow">
                  {topNews[0].title}
                </h3>
                {topNews[0].description ? (
                  <p className="mt-2 text-white/90 line-clamp-2 max-w-3xl">{topNews[0].description}</p>
                ) : null}
                <button
                  onClick={() => window.open(topNews[0].url || '#', '_blank')}
                  className="mt-4 px-4 py-2 rounded-full text-sm font-medium shadow"
                  style={{ backgroundColor: palette.red, color: palette.white }}
                >
                  Daha Fazla Oku
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>

      {/* Grid list */}
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-6">
        {error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
            {error}
          </div>
        ) : null}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {restNews.map((n) => (
            <NewsCard
              key={n.id}
              title={n.title}
              description={n.description}
              imageUrl={n.imageUrl}
              onReadMore={() => window.open(n.url || '#', '_blank')}
            />
          ))}
        </div>

        {/* Loading & Load more */}
        <div className="flex items-center justify-center py-6">
          {loading ? (
            <div className="flex items-center gap-3">
              <LoadingSpinner />
              <span className="text-gray-600">Yükleniyor…</span>
            </div>
          ) : hasMore ? (
            <button
              onClick={loadMore}
              className="px-5 py-2 rounded-full font-medium border"
              style={{ borderColor: palette.navy, color: palette.navy, backgroundColor: palette.white }}
            >
              Daha Fazla Yükle
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default NewsSection;



