rimport React, { useMemo } from 'react';
import clsx from 'clsx';
import { useNewsViewModel } from '../viewmodels/useNewsViewModel';
import NewsModal from '../components/NewsModal';
import NewsCard from '../components/NewsCard.jsx';
import { LoadingSpinner } from '../components';

const palette = {
  navy: '#0C2340',
  red: '#E10600',
  white: '#FFFFFF',
  gray: '#F4F4F4',
  blue: '#005799'
};

const categories = ['All', 'Politics', 'Economy', 'Sports', 'Technology'];

export const NewsSection = ({ hideHeader = false }) => {
  const { news, loading, error, hasMore, category, setCategory, refresh, loadMore } = useNewsViewModel();
  const [selectedId, setSelectedId] = React.useState(null);

  const topNews = useMemo(() => news.slice(0, 5), [news]);
  const restNews = useMemo(() => news.slice(5), [news]);

  return (
    <div className="w-full" style={{ backgroundColor: palette.gray }}>
      {/* Headline banner */}
      {hideHeader ? null : (
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
                      'px-5 py-2.5 rounded-full border-2 text-sm font-semibold whitespace-nowrap transition-all duration-200',
                      'hover:scale-105 active:scale-95 shadow-sm hover:shadow-md',
                      c === (category || 'All') 
                        ? 'text-white shadow-lg' 
                        : 'text-gray-700 hover:text-gray-900'
                    )}
                    style={{
                      backgroundColor: c === (category || 'All') ? palette.navy : palette.white,
                      borderColor: c === (category || 'All') ? palette.navy : palette.navy
                    }}
                  >
                    {c === (category || 'All') && (
                      <span className="mr-2">●</span>
                    )}
                    {c}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top news carousel (mobile-first) */}
      <div className="sm:hidden">
        <div className="flex gap-4 overflow-x-auto no-scrollbar px-4 pb-4">
          {topNews.map((n) => (
            <div key={n.id} className="min-w-[85%]">
              <NewsCard
                id={n.id}
                title={n.title}
                description={n.description}
                imageUrl={n.imageUrl}
                onReadMore={() => setSelectedId(n.id)}
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
                  onClick={() => setSelectedId(topNews[0].id)}
                  className="mt-4 px-4 py-2 rounded-full text-sm font-medium shadow hover:opacity-90 transition-opacity"
                  style={{ 
                    background: `linear-gradient(135deg, ${palette.blue} 0%, #003d73 100%)`, 
                    color: palette.white 
                  }}
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
              id={n.id}
              title={n.title}
              description={n.description}
              imageUrl={n.imageUrl}
              onReadMore={() => setSelectedId(n.id)}
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
              className="px-6 py-3 rounded-full font-semibold border-2 hover:scale-105 active:scale-95 transition-all duration-200 shadow-md hover:shadow-lg"
              style={{ 
                borderColor: palette.navy, 
                color: palette.navy, 
                backgroundColor: palette.white,
                '&:hover': {
                  backgroundColor: palette.navy,
                  color: palette.white
                }
              }}
            >
              <span className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Daha Fazla Yükle
              </span>
            </button>
          ) : null}
        </div>
      </div>

      {/* Modal */}
      <NewsModal newsId={selectedId} onClose={() => setSelectedId(null)} />
    </div>
  );
};

export default NewsSection;



