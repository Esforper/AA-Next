import React from 'react';
import { useReelsViewModel } from '../viewmodels';
import { ReelItem } from '../components';

export const HomeView: React.FC = () => {
  const { reels, loading, error } = useReelsViewModel();

  const topNine = reels.slice(0, 9);

  if (loading && reels.length === 0) return (
    <div className="mx-auto max-w-6xl px-4 py-8 text-center text-gray-700">Yükleniyor...</div>
  );
  if (error && reels.length === 0) return (
    <div className="mx-auto max-w-6xl px-4 py-8 text-center text-red-600">{error}</div>
  );

  const goDetail = (id: string) => {
    window.location.assign(`/news/${id}`);
  };

  return (
    <div className="mx-auto max-w-6xl px-4 py-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {topNine.map((reel) => (
          <div key={reel.id} onClick={() => goDetail(reel.id)} className="cursor-pointer">
            <ReelItem
              reel={reel}
              isActive={false}
              onImageClick={() => goDetail(reel.id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomeView;