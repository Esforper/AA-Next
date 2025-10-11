# Flutter-Inspired Button Components

React button bileşenleri **Flutter Mobile App** tasarımından ilham alınarak oluşturuldu. Material Design 3 prensiplerine uygun, responsive ve erişilebilir butonlar.

## 🎨 Tasarım Sistemi

### Renkler (AA Theme)
- **Primary**: `#0078D2` (AA Mavi)
- **Primary Dark**: `#006BB8`
- **Secondary**: `#36495A` (Koyu gri/mavi)

### Flutter'dan React'e Dönüşüm

| Flutter Widget | React Component | Açıklama |
|---------------|-----------------|----------|
| `ElevatedButton` | `<Button>` | Standard buton |
| `IconButton` | `<IconButton>` | Circular icon buton |
| `VoiceButton` | `<VoiceButton>` | Ses kontrol butonu |
| `CategoryBubbleMenu` | `<GradientButton>` | Gradient aksiyon butonu |
| `FloatingActionButton` | `<FloatingActionButton>` | FAB butonu |

## 📦 Bileşenler

### 1. Button (Standard)

Temel buton bileşeni - Flutter `ElevatedButton` ve `TextButton` gibi.

```tsx
import { Button } from '@/components';

// Variants
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="text">Text</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// With Icons
<Button 
  icon={<Icon />} 
  iconPosition="left"
>
  Click Me
</Button>

// States
<Button loading>Loading...</Button>
<Button disabled>Disabled</Button>
<Button fullWidth>Full Width</Button>
```

### 2. IconButton

Circular icon button - Flutter `IconButton` gibi.

```tsx
import { IconButton } from '@/components';

<IconButton
  variant="primary" // primary | secondary | ghost | danger
  size="md" // sm | md | lg
  icon={<Icon />}
  onClick={() => {}}
  tooltip="Click me"
/>
```

### 3. VoiceButton

Ses kontrolü için özel buton - Flutter `VoiceButton` gibi.

```tsx
import { VoiceButton } from '@/components';

const [speaking, setSpeaking] = useState(false);

<VoiceButton
  speaking={speaking}
  onToggle={() => setSpeaking(!speaking)}
  size="md" // sm | md | lg
/>
```

### 4. GradientButton

Gradient arka planlı aksiyon butonu - Flutter `CategoryBubbleMenu` gibi.

```tsx
import { GradientButton } from '@/components';

<GradientButton
  variant="primary" // primary | accent | success
  icon={<Icon />}
  trailingIcon={<ArrowIcon />}
  fullWidth
  onClick={() => {}}
>
  Kategorilere Göz At
</GradientButton>
```

### 5. FloatingActionButton (FAB)

Floating action button - Flutter `FloatingActionButton` gibi.

```tsx
import { FloatingActionButton } from '@/components';

// Basic FAB
<FloatingActionButton
  icon={<PlusIcon />}
  onClick={() => {}}
  position="bottom-right" // bottom-right | bottom-left | top-right | top-left
/>

// Extended FAB
<FloatingActionButton
  extended
  label="Yeni Ekle"
  icon={<PlusIcon />}
  onClick={() => {}}
/>
```

## 🎯 Props API

### Button Props

```typescript
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'text';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}
```

### IconButton Props

```typescript
interface IconButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
  tooltip?: string;
  'aria-label'?: string;
}
```

### VoiceButton Props

```typescript
interface VoiceButtonProps {
  speaking: boolean;
  onToggle: () => void;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
```

### GradientButton Props

```typescript
interface GradientButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  icon?: React.ReactNode;
  trailingIcon?: React.ReactNode;
  disabled?: boolean;
  className?: string;
  variant?: 'primary' | 'accent' | 'success';
  fullWidth?: boolean;
}
```

### FloatingActionButton Props

```typescript
interface FloatingActionButtonProps {
  icon: React.ReactNode;
  onClick?: () => void;
  size?: 'md' | 'lg';
  variant?: 'primary' | 'secondary';
  extended?: boolean;
  label?: string;
  className?: string;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
}
```

## ♿ Erişilebilirlik

Tüm butonlar WCAG 2.1 Level AA standartlarına uygun:

- ✅ Keyboard navigation (Tab, Enter, Space)
- ✅ Focus indicators (focus ring)
- ✅ ARIA labels ve tooltips
- ✅ Disabled state management
- ✅ Color contrast (4.5:1 minimum)

## 🎨 Özelleştirme

Tailwind CSS className prop'u ile özelleştirilebilir:

```tsx
<Button className="!bg-purple-600 hover:!bg-purple-700">
  Custom Color
</Button>

<IconButton className="!w-16 !h-16 !text-2xl">
  Custom Size
</IconButton>
```

## 📱 Responsive

Tüm butonlar mobil ve desktop için optimize edilmiştir:

- Touch-friendly minimum boyutlar (44x44px)
- Active state animasyonları
- Hover effects (desktop only)
- Scale animations

## 🧪 Test Etmek İçin

`ButtonShowcase` bileşeni tüm buton örneklerini içerir:

```tsx
import { ButtonShowcase } from '@/components/buttons/ButtonShowcase';

// App.tsx içinde
<ButtonShowcase />
```

## 📝 Notlar

- **Flutter kodlarına dokunulmadı** - Sadece React tarafı oluşturuldu
- **MVVM yapısına uygun** - Bileşenler state management ile entegre
- **Responsive** - Mobile-first tasarım
- **Mevcut sistemler korundu** - Backend'e hiç dokunulmadı

## 🚀 Kullanım Örnekleri

### Reels Page Actions

```tsx
<GradientButton
  icon={<AppsIcon />}
  onClick={() => navigate('/categories')}
>
  Kategorilere Göz At
</GradientButton>
```

### Audio Control

```tsx
<VoiceButton
  speaking={isPlaying}
  onToggle={() => toggleAudio()}
/>
```

### Header Actions

```tsx
<IconButton
  variant="ghost"
  icon={<ShareIcon />}
  onClick={() => handleShare()}
  tooltip="Paylaş"
/>
```

### Form Actions

```tsx
<Button
  type="submit"
  loading={isSubmitting}
  fullWidth
>
  Kaydet
</Button>
```

