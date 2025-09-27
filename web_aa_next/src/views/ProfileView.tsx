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
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Profil
          </h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card padding="lg" shadow="lg" className="text-center">
          <div className="mb-6">
            <div className="text-6xl mb-4">👤</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Profil Özelikleri Geliştiriliyor
            </h2>
            <p className="text-gray-600 text-lg">
              Kullanıcı profili ve hesap yönetimi özellikleri yakında eklenecek
            </p>
          </div>

          {/* Auth Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Button onClick={handleLogin} variant="primary" size="lg">
              Giriş Yap
            </Button>
            <Button onClick={handleRegister} variant="outline" size="lg">
              Kayıt Ol
            </Button>
          </div>

          <div className="text-left max-w-md mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Planlanan Özellikler:
            </h3>
            <ul className="space-y-2">
              {profileFeatures.map((feature, index) => (
                <li key={index} className="flex items-center text-gray-700">
                  <span className="text-blue-500 mr-2">🔧</span>
                  {feature}
                </li>
              ))}
            </ul>
          </div>

          <div className="mt-8 p-4 bg-orange-50 rounded-lg">
            <p className="text-orange-800 text-sm">
              <strong>Geliştirme aşamasında:</strong> Kullanıcı profili özellikleri aktif olarak kodlanmaktadır. 
              Kimlik doğrulama ve kişiselleştirme seçenekleri yakında kullanıma sunulacak.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};