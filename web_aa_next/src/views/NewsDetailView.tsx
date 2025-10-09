import React from 'react';
import { useParams } from 'react-router-dom';
import { useReelsViewModel } from '../viewmodels';
import { ArticleContent } from '../components/ArticleContent';

export const NewsDetailView: React.FC = () => {
  const { id } = useParams();
  const { reels } = useReelsViewModel();
  const item = reels.find(r => String(r.id) === String(id));

  if (!item) return <div className="mx-auto max-w-3xl px-4 py-8 text-gray-200">Haber bulunamadı.</div>;

  return (
    <article className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="text-2xl font-extrabold mb-3 text-white">{item.title}</h1>
      <div className="text-sm text-gray-400 mb-6">
        {new Date(item.published_at || Date.now()).toLocaleString('tr-TR')}
      </div>

      <ArticleContent content={item.content || ''} images={item.images || []} imageEvery={2} />
    </article>
  );
};

export default NewsDetailView;