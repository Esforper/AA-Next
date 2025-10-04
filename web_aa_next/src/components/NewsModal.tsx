import React, { useEffect } from 'react';
import clsx from 'clsx';
import { useNewsDetailViewModel } from '../viewmodels/useNewsDetailViewModel';

const palette = {
  navy: '#0C2340',
  red: '#E10600',
  white: '#FFFFFF',
  gray: '#F4F4F4',
  blue: '#005799'
};

export interface NewsModalProps {
  newsId: string | null;
  onClose: () => void;
}

export const NewsModal: React.FC<NewsModalProps> = ({ newsId, onClose }) => {
  const vm = useNewsDetailViewModel();

  useEffect(() => {
    if (newsId) {
      void vm.open(newsId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [newsId]);

  if (!vm.isOpen) return null;

  return (
    <div
      className={clsx(
        'fixed inset-0 z-[100] flex items-center justify-center p-4',
        'bg-black/40 backdrop-blur-sm'
      )}
      onClick={() => {
        vm.close();
        onClose();
      }}
    >
      <div
        className={clsx(
          'w-full max-w-3xl rounded-xl shadow-xl overflow-hidden',
          'transform transition-all duration-300',
          'bg-white'
        )}
        style={{ backgroundColor: palette.white }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: '#e5e7eb' }}>
          <h3 className="text-lg font-semibold" style={{ color: palette.navy }}>Haber Detayı</h3>
          <button 
            onClick={() => {
              vm.close();
              onClose();
            }} 
            className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full p-2 transition-colors duration-200 text-xl font-bold"
            aria-label="Kapat"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {vm.loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin h-6 w-6 border-2 border-gray-300 border-t-transparent rounded-full" />
              <span className="ml-3 text-gray-600">Yükleniyor…</span>
            </div>
          ) : vm.error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md">
              {vm.error}
            </div>
          ) : vm.data ? (
            <div>
              {vm.data.imageUrl ? (
                <img src={vm.data.imageUrl} alt={vm.data.title} className="w-full h-64 object-cover rounded-md" />
              ) : null}
              <h4 className="mt-4 text-xl font-bold" style={{ color: palette.navy }}>{vm.data.title}</h4>
              {vm.data.publishedAt || vm.data.author ? (
                <div className="mt-1 text-sm text-gray-500">
                  {vm.data.author ? <span>{vm.data.author} • </span> : null}
                  {vm.data.publishedAt ? <span>{new Date(vm.data.publishedAt).toLocaleString()}</span> : null}
                </div>
              ) : null}
              <p className="mt-3 whitespace-pre-wrap text-gray-800">{vm.data.content}</p>
            </div>
          ) : null}
        </div>

      </div>
    </div>
  );
};

export default NewsModal;



