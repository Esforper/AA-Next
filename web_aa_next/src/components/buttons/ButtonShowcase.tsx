// src/components/buttons/ButtonShowcase.tsx
// Flutter button bileşenlerinin örnek kullanımları

import React, { useState } from 'react';
import { Button } from '../Button';
import { IconButton } from './IconButton';
import { VoiceButton } from './VoiceButton';
import { GradientButton } from './GradientButton';
import { FloatingActionButton } from './FloatingActionButton';

export const ButtonShowcase: React.FC = () => {
  const [speaking, setSpeaking] = useState(false);

  return (
    <div className="p-8 space-y-12 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Flutter-Inspired Button Components
        </h1>
        <p className="text-gray-600 mb-8">
          React button bileşenleri Flutter Mobile App tasarımından ilham alınarak oluşturuldu
        </p>

        {/* Standard Buttons */}
        <section className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Standard Buttons</h2>
          <div className="space-y-4">
            {/* Variants */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Variants</h3>
              <div className="flex flex-wrap gap-3">
                <Button variant="primary">Primary Button</Button>
                <Button variant="secondary">Secondary Button</Button>
                <Button variant="outline">Outline Button</Button>
                <Button variant="ghost">Ghost Button</Button>
                <Button variant="text">Text Button</Button>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Sizes</h3>
              <div className="flex flex-wrap items-center gap-3">
                <Button size="sm">Small</Button>
                <Button size="md">Medium</Button>
                <Button size="lg">Large</Button>
              </div>
            </div>

            {/* With Icons */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">With Icons</h3>
              <div className="flex flex-wrap gap-3">
                <Button
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  }
                  iconPosition="left"
                >
                  Add Item
                </Button>
                <Button
                  variant="outline"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                    </svg>
                  }
                  iconPosition="right"
                >
                  Share
                </Button>
              </div>
            </div>

            {/* States */}
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">States</h3>
              <div className="flex flex-wrap gap-3">
                <Button loading>Loading...</Button>
                <Button disabled>Disabled</Button>
                <Button fullWidth>Full Width Button</Button>
              </div>
            </div>
          </div>
        </section>

        {/* Icon Buttons */}
        <section className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Icon Buttons</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Variants</h3>
              <div className="flex flex-wrap items-center gap-3">
                <IconButton
                  variant="primary"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  }
                  tooltip="Primary"
                />
                <IconButton
                  variant="secondary"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                  }
                  tooltip="Secondary"
                />
                <IconButton
                  variant="ghost"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  }
                  tooltip="Ghost"
                />
                <IconButton
                  variant="danger"
                  icon={
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  }
                  tooltip="Danger"
                />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Sizes</h3>
              <div className="flex flex-wrap items-center gap-3">
                <IconButton
                  size="sm"
                  icon={<span>📱</span>}
                  tooltip="Small"
                />
                <IconButton
                  size="md"
                  icon={<span>📱</span>}
                  tooltip="Medium"
                />
                <IconButton
                  size="lg"
                  icon={<span>📱</span>}
                  tooltip="Large"
                />
              </div>
            </div>
          </div>
        </section>

        {/* Voice Button */}
        <section className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Voice Button</h2>
          <p className="text-sm text-gray-600 mb-4">
            Flutter VoiceButton gibi ses kontrol butonu
          </p>
          <div className="bg-gray-900 rounded-2xl p-8 inline-block">
            <VoiceButton
              speaking={speaking}
              onToggle={() => setSpeaking(!speaking)}
            />
          </div>
        </section>

        {/* Gradient Buttons */}
        <section className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Gradient Buttons</h2>
          <p className="text-sm text-gray-600 mb-4">
            Flutter CategoryBubbleMenu gibi gradient butonlar
          </p>
          <div className="space-y-3">
            <GradientButton
              variant="primary"
              icon={<span>📱</span>}
              onClick={() => alert('Kategorilere tıklandı!')}
            >
              Kategorilere Göz At
            </GradientButton>

            <GradientButton
              variant="accent"
              icon={<span>🎯</span>}
            >
              Premium Özellikleri Keşfet
            </GradientButton>

            <GradientButton
              variant="success"
              icon={<span>✅</span>}
              trailingIcon={null}
            >
              Görevi Tamamla
            </GradientButton>
          </div>
        </section>

        {/* Floating Action Buttons */}
        <section className="bg-white rounded-2xl p-6 shadow-sm mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Floating Action Buttons (FAB)</h2>
          <p className="text-sm text-gray-600 mb-4">
            Flutter FloatingActionButton gibi
          </p>
          <div className="space-y-4">
            <div className="bg-gray-100 rounded-xl p-12 relative h-48">
              <FloatingActionButton
                position={undefined}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                }
                className="absolute bottom-4 right-4"
              />
            </div>

            <div className="bg-gray-100 rounded-xl p-12 relative h-48">
              <FloatingActionButton
                position={undefined}
                extended
                label="Yeni Ekle"
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                }
                className="absolute bottom-4 right-4"
              />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

