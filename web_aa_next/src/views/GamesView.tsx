import React from 'react';
import { Card } from '../components';

export const GamesView: React.FC = () => {
  const plannedFeatures = [
    'Mini kelime oyunları',
    'Haber bilgi yarışması',
    'Puan kazanma sistemi',
    'Liderlik tablosu',
    'Günlük görevler',
    'Başarım rozetleri'
  ];

  return (
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Header - Responsive */}
      <div className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">
            Oyunlar
          </h1>
        </div>
      </div>

      {/* Content - Responsive */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <Card padding="lg" shadow="lg" className="text-center">
          <div className="mb-6 sm:mb-8">
            <div className="text-4xl sm:text-6xl mb-4">🎮</div>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-2 sm:mb-4">
              Oyunlar Çok Yakında!
            </h2>
            <p className="text-gray-600 text-base sm:text-lg leading-relaxed">
              Bu sayfa yakında eğlenceli mini oyunlar ile dolu olacak
            </p>
          </div>

          <div className="text-left max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Planlanan Özellikler:
            </h3>
            <ul className="space-y-2 sm:space-y-3">
              {plannedFeatures.map((feature, index) => (
                <li key={index} className="flex items-center text-gray-700 text-sm sm:text-base">
                  <span className="text-green-500 mr-2 text-lg">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-6 sm:mt-8 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm sm:text-base leading-relaxed">
              <strong>Geliştirme sürecinde:</strong> Oyun özellikleri şu anda aktif olarak geliştirilmektedir. 
              Güncellemeler için takipte kalın!
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};