import React from 'react';
import { NewsSection } from './NewsSection';

export const TestView: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Bar (Mobile only, desktop üst bar App'te) */}
      <header className="sticky top-0 z-40 shadow-lg sm:hidden" style={{ backgroundColor: '#005799' }}>
        <div className="w-full">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
            <h1 className="text-xl font-bold text-white">
              AA Haber
            </h1>
            <span className="text-sm text-white/90 font-medium">Güvenilir Haber</span>
          </div>
        </div>
      </header>

      {/* Latest News Section */}
      <main>
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl sm:text-2xl font-bold" style={{ color: '#0C2340' }}>Son Haberler</h2>
          </div>
          <div className="rounded-xl overflow-hidden ring-1 ring-gray-200 bg-white">
            <NewsSection hideHeader />
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-gradient-to-r from-gray-50 to-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-sm text-gray-600 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span className="font-medium">© {new Date().getFullYear()} AA Haber</span>
          <div className="flex items-center gap-4">
            <a href="#" className="hover:underline hover:text-blue-600 transition-colors" style={{ color: '#005799' }}>
              İletişim
            </a>
            <a href="#" className="hover:underline hover:text-blue-600 transition-colors" style={{ color: '#005799' }}>
              Hakkımızda
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};