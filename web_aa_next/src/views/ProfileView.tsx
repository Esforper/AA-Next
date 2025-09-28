import React from 'react';
import { Card, Button } from '../components';

export const ProfileView: React.FC = () => {
  const profileFeatures = [
    'Kullanıcı hesap yönetimi',
    'Okuma geçmişi',
    'Favori haberler',
    'Bildirim ayarları',
    'Tema seçimi',
    'Dil seçimi'
  ];

  const handleLogin = () => {
    // TODO: Implement login logic
    console.log('Login clicked');
  };

  const handleRegister = () => {
    // TODO: Implement register logic
    console.log('Register clicked');
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20 sm:pb-24">
      {/* Header - Responsive */}
      <div className="bg-white/95 backdrop-blur-md shadow-sm sticky top-0 z-40 border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900">
            Profil
          </h1>
        </div>
      </div>

      {/* Content - Responsive */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <Card padding="lg" shadow="lg" className="text-center">
          <div className="mb-6 sm:mb-8">
            <div className="text-4xl sm:text-6xl mb-4">👤</div>
            <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 mb-2 sm:mb-4">
              Profil Özelikleri Geliştiriliyor
            </h2>
            <p className="text-gray-600 text-base sm:text-lg leading-relaxed">
              Kullanıcı profili ve hesap yönetimi özellikleri yakında eklenecek
            </p>
          </div>

          {/* Auth Buttons - Responsive */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center mb-6 sm:mb-8">
            <Button onClick={handleLogin} variant="primary" size="lg" className="w-full sm:w-auto">
              Giriş Yap
            </Button>
            <Button onClick={handleRegister} variant="outline" size="lg" className="w-full sm:w-auto">
              Kayıt Ol
            </Button>
          </div>

          <div className="text-left max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Planlanan Özellikler:
            </h3>
            <ul className="space-y-2 sm:space-y-3">
              {profileFeatures.map((feature, index) => (
                <li key={index} className="flex items-center text-gray-700 text-sm sm:text-base">
                  <span className="text-blue-500 mr-2 text-lg">🔧</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-6 sm:mt-8 p-4 bg-orange-50 rounded-lg">
            <p className="text-orange-800 text-sm sm:text-base leading-relaxed">
              <strong>Geliştirme aşamasında:</strong> Kullanıcı profili özellikleri aktif olarak kodlanmaktadır. 
              Kimlik doğrulama ve kişiselleştirme seçenekleri yakında kullanıma sunulacak.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};