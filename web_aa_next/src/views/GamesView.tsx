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
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Oyunlar
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card padding="lg" shadow="lg" className="text-center">
          <div className="mb-6">
            <div className="text-6xl mb-4">🎮</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Oyunlar Çok Yakında!
            </h2>
            <p className="text-gray-600 text-lg">
              Bu sayfa yakında eğlenceli mini oyunlar ile dolu olacak
            </p>
          </div>

          <div className="text-left max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Planlanan Özellikler:
            </h3>
            <ul className="space-y-2">
              {plannedFeatures.map((feature, index) => (
                <li key={index} className="flex items-center text-gray-700">
                  <span className="text-green-500 mr-2">✓</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">
              <strong>Geliştirme sürecinde:</strong> Oyun özellikleri şu anda aktif olarak geliştirilmektedir. 
              Güncellemeler için takipte kalın!
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};