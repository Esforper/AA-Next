import React from 'react';

export const TestView: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Test Sayfası
        </h1>
        <p className="text-lg text-gray-600">
          Uygulama çalışıyor! 🎉
        </p>
        <div className="mt-8 p-4 bg-green-100 rounded-lg">
          <p className="text-green-800">
            React, TypeScript, TailwindCSS ve MSW başarıyla yüklendi.
          </p>
        </div>
      </div>
    </div>
  );
};