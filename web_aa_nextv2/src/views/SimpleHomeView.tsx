import React from 'react';

export const SimpleHomeView: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Haberler
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Mock Articles */}
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Görsel {item}</span>
              </div>
              <div className="p-4">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">
                  Örnek Haber Başlığı {item}
                </h2>
                <p className="text-sm text-gray-600 mb-3">
                  Bu bir örnek haber açıklamasıdır. Gerçek içerik API'den gelecektir.
                </p>
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Yazar</span>
                  <span>2 saat önce</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};