import { View, Text, StyleSheet, Dimensions, TouchableOpacity, StatusBar, Platform } from 'react-native';
import { useState, useEffect, useRef } from 'react';
import { Audio } from 'expo-av';
import { Image } from 'expo-image';
import { Ionicons } from '@expo/vector-icons';
import { FlatList } from 'react-native';
import Animated, { 
  useSharedValue, 
  useAnimatedStyle, 
  withTiming,
} from 'react-native-reanimated';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const API_BASE_URL = 'http://192.168.0.21:8000'; // Local network IP - Update this!

interface SubtitleData {
  start: number;
  end: number;
  text: string;
}

interface ReelData {
  id: string;
  title: string;
  content: string;
  category: string;
  images: string[];
  main_image: string;
  audio_url: string;
  subtitles: SubtitleData[];
  estimated_duration: number;
  tags: string[];
  author?: string;
  location?: string;
  summary?: string; // Bu satırı ekle
}

export default function ReelsScreen() {
  const [reels, setReels] = useState<ReelData[]>([]);
  const [currentReelIndex, setCurrentReelIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [audioPosition, setAudioPosition] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  
  const flatListRef = useRef<FlatList>(null);
  const soundRef = useRef<Audio.Sound | null>(null);
  const progressOpacity = useSharedValue(0);

  useEffect(() => {
    fetchReels();
    if (Platform.OS !== 'web') {
      setupAudio();
    }
    
    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync();
      }
    };
  }, []);

  const setupAudio = async () => {
    try {
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: false,
        staysActiveInBackground: true,
        playsInSilentModeIOS: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });
    } catch (error) {
      console.log('Audio setup error:', error);
    }
  };

const fetchReels = async () => {
    try {
        setLoading(true);
        
        console.log('🔍 API çağrısı başlatılıyor...');
        const response = await fetch(`${API_BASE_URL}/api/agenda/ready?limit=15`);
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response ok:', response.ok);
        
        const data = await response.json();
        console.log('📦 API Response:', JSON.stringify(data, null, 2));
        
        if (data.success && data.reels) {
        console.log(`✅ ${data.reels.length} reel yüklendi`);
        console.log('🎬 İlk reel:', data.reels[0]);
        
        setReels(data.reels);
        
        if (data.reels.length > 0 && Platform.OS !== 'web') {
            console.log('🎵 İlk ses yükleniyor...');
            loadAudio(data.reels[0]);
        }
        } else {
        console.warn('❌ API başarısız:', data.message);
        console.log('🔄 Fallback kullanılıyor');
        setReels(getFallbackReels());
        }
    } catch (error) {
        console.error('💥 API hatası:', error);
        setReels(getFallbackReels());
    } finally {
        setLoading(false);
    }
    };
    // getFallbackReels ekle
const getFallbackReels = (): ReelData[] => {
  return [
    {
      id: 'fallback_1',
      title: 'Test Haberi - Bağlantı Sorunu',
      content: 'API bağlantısında sorun var. Fallback veri gösteriliyor.',
      category: 'guncel',
      images: [
        'https://picsum.photos/400/600?random=100',
        'https://picsum.photos/400/600?random=101'
      ],
      main_image: 'https://picsum.photos/400/600?random=100',
      audio_url: '', // Ses yok
      subtitles: [
        { start: 0, end: 3, text: 'Test verisi gösteriliyor.' },
        { start: 3, end: 6, text: 'API bağlantısını kontrol edin.' }
      ],
      estimated_duration: 10,
      tags: ['test', 'fallback'],
      author: 'Sistem',
      location: 'Test',
      summary: 'Fallback test verisi'
    }
  ];
};
    // 1. Audio yükleme düzeltmesi (loadAudio fonksiyonunda)
    const loadAudio = async (reel: ReelData) => {
    if (Platform.OS === 'web') return;
    
    try {
        if (soundRef.current) {
        await soundRef.current.unloadAsync();
        }

        // SES URL'SİNİ DÜZELT
        const audioUrl = reel.audio_url.startsWith('http') 
        ? reel.audio_url 
        : `${API_BASE_URL}/${reel.audio_url.replace(/^\/+/, '')}`;

        const { sound } = await Audio.Sound.createAsync(
        { uri: audioUrl },
        { 
            shouldPlay: true, // Otomatik çalma için
            isLooping: false,
            progressUpdateIntervalMillis: 100
        }
        );

        soundRef.current = sound;
        
        sound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded) {
            setAudioPosition(status.positionMillis || 0);
            setIsPlaying(status.isPlaying || false);
        }
        });

    } catch (error) {
        console.log('Audio load error:', error);
    }
    };
    const onViewableItemsChanged = useRef(({ viewableItems }: any) => {
    if (viewableItems.length > 0) {
        const newIndex = viewableItems[0].index;
        setCurrentReelIndex(newIndex);
        
        if (reels[newIndex] && Platform.OS !== 'web') {
        loadAudio(reels[newIndex]); // Bu zaten otomatik çalacak (shouldPlay: true)
        }
    }
    }).current;

  const playAudio = async () => {
    if (Platform.OS === 'web') return;
    
    try {
      if (soundRef.current) {
        await soundRef.current.playAsync();
        progressOpacity.value = withTiming(1, { duration: 300 });
      }
    } catch (error) {
      console.log('Play error:', error);
    }
  };

  const pauseAudio = async () => {
    if (Platform.OS === 'web') return;
    
    try {
      if (soundRef.current) {
        await soundRef.current.pauseAsync();
        progressOpacity.value = withTiming(0.3, { duration: 300 });
      }
    } catch (error) {
      console.log('Pause error:', error);
    }
  };

  const getCurrentSubtitle = (reel: ReelData): string => {
    if (Platform.OS === 'web') return reel.content.split('.')[0] + '.'; // Web fallback
    
    const currentTimeSeconds = audioPosition / 1000;
    const currentSubtitle = reel.subtitles.find(
      sub => currentTimeSeconds >= sub.start && currentTimeSeconds <= sub.end
    );
    return currentSubtitle?.text || '';
  };

  const getAudioProgress = (reel: ReelData): number => {
    if (Platform.OS === 'web') return 0.5; // Web fallback
    
    const totalDuration = reel.estimated_duration * 1000;
    return totalDuration > 0 ? audioPosition / totalDuration : 0;
  };

  const progressBarStyle = useAnimatedStyle(() => ({
    opacity: progressOpacity.value,
  }));

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Reels yükleniyor...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="black" />
      
      <FlatList
        ref={flatListRef}
        data={reels}
        keyExtractor={(item) => item.id}
        renderItem={({ item, index }) => (
          <ReelItem
            reel={item}
            isActive={index === currentReelIndex}
            currentSubtitle={getCurrentSubtitle(item)}
            audioProgress={getAudioProgress(item)}
            isPlaying={isPlaying}
            onPlayPause={() => isPlaying ? pauseAudio() : playAudio()}
          />
        )}
        pagingEnabled
        showsVerticalScrollIndicator={false}
        snapToInterval={SCREEN_HEIGHT}
        snapToAlignment="start"
        decelerationRate="fast"
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={{
          itemVisiblePercentThreshold: 50
        }}
      />

      {Platform.OS !== 'web' && (
        <Animated.View style={[styles.progressContainer, progressBarStyle]}>
          {reels[currentReelIndex] && (
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${getAudioProgress(reels[currentReelIndex]) * 100}%` }
                ]} 
              />
            </View>
          )}
        </Animated.View>
      )}
    </View>
  );
}

interface ReelItemProps {
  reel: ReelData;
  isActive: boolean;
  currentSubtitle: string;
  audioProgress: number;
  isPlaying: boolean;
  onPlayPause: () => void;
}

function ReelItem({ reel, isActive, currentSubtitle, isPlaying, onPlayPause }: ReelItemProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const scaleValue = useSharedValue(1);

  useEffect(() => {
    if (isActive) {
      scaleValue.value = withTiming(1.05, { duration: 300 });
    } else {
      scaleValue.value = withTiming(1, { duration: 300 });
    }
  }, [isActive]);

  const imageStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scaleValue.value }],
  }));

  const nextImage = () => {
    if (currentImageIndex < reel.images.length - 1) {
      setCurrentImageIndex(prev => prev + 1);
    } else {
      setCurrentImageIndex(0);
    }
  };

  const prevImage = () => {
    if (currentImageIndex > 0) {
      setCurrentImageIndex(prev => prev - 1);
    } else {
      setCurrentImageIndex(reel.images.length - 1);
    }
  };

  const getCategoryColor = (category: string): string => {
    const colors = {
      'guncel': '#EF4444',
      'ekonomi': '#F59E0B', 
      'spor': '#10B981',
      'teknoloji': '#3B82F6',
      'kultur': '#8B5CF6'
    };
    return colors[category as keyof typeof colors] || '#6B7280';
  };

  return (
    <View style={styles.reelContainer}>
      {/* Background Image */}
        {reel.images.length > 0 && (
        <Animated.View style={[styles.imageContainer, imageStyle]}>
            <Image
            source={{ uri: reel.images[currentImageIndex] }} // SOURCE EKLE
            style={styles.backgroundImage}
            contentFit="cover"
            transition={300}
            />
          
          {/* Image Navigation */}
          {reel.images.length > 1 && (
            <>
              <TouchableOpacity 
                style={[styles.imageNav, styles.imageNavLeft]}
                onPress={prevImage}
              >
                <Ionicons name="chevron-back" size={24} color="rgba(255,255,255,0.8)" />
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.imageNav, styles.imageNavRight]}
                onPress={nextImage}
              >
                <Ionicons name="chevron-forward" size={24} color="rgba(255,255,255,0.8)" />
              </TouchableOpacity>
              
              {/* Image Indicators */}
              <View style={styles.imageIndicators}>
                {reel.images.map((_, index) => (
                  <View
                    key={index}
                    style={[
                      styles.indicator,
                      index === currentImageIndex && styles.activeIndicator
                    ]}
                  />
                ))}
              </View>
            </>
          )}
        </Animated.View>
      )}

      {/* Gradient Overlay */}
      <View style={styles.gradientOverlay} />

      {/* Content */}
      <View style={styles.contentContainer}>
        {/* Top Info */}
        <View style={styles.topInfo}>
          <View style={[styles.categoryBadge, { backgroundColor: getCategoryColor(reel.category) }]}>
            <Text style={styles.categoryText}>{reel.category.toUpperCase()}</Text>
          </View>
          
          <TouchableOpacity style={styles.playButton} onPress={onPlayPause}>
            <Ionicons 
              name={isPlaying ? "pause" : "play"} 
              size={24} 
              color="white" 
            />
          </TouchableOpacity>
        </View>

        {/* Bottom Content */}
        <View style={styles.bottomContent}>
          {/* Subtitle - Sesle senkronize */}
          {currentSubtitle && (
            <View style={styles.subtitleContainer}>
              <Text style={styles.subtitleText}>{currentSubtitle}</Text>
            </View>
          )}

          {/* Title - Her zaman görünür */}
          <View style={styles.titleContainer}>
            <Text style={styles.title}>{reel.title}</Text>
          </View>

          {/* Summary - Başlık altında */}
          {reel.summary && (
            <View style={styles.summaryContainer}>
              <Text style={styles.summaryText}>{reel.summary}</Text>
            </View>
          )}
          
          {/* Author & Location */}
          {(reel.author || reel.location) && (
            <Text style={styles.authorInfo}>
              {reel.author && reel.location 
                ? `${reel.author} • ${reel.location}`
                : reel.author || reel.location
              }
            </Text>
          )}

          {/* Tags */}
          {reel.tags && reel.tags.length > 0 && (
            <View style={styles.tagsContainer}>
              {reel.tags.slice(0, 3).map((tag, index) => (
                <Text key={index} style={styles.tag}>#{tag}</Text>
              ))}
            </View>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'black',
  },
  loadingText: {
    color: 'white',
    fontSize: 16,
  },
  reelContainer: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    position: 'relative',
  },
  imageContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  backgroundImage: {
    width: '100%',
    height: '100%',
  },
  imageNav: {
    position: 'absolute',
    top: '50%',
    width: 50,
    height: 100,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.3)',
    zIndex: 2,
  },
  imageNavLeft: {
    left: 0,
    borderTopRightRadius: 25,
    borderBottomRightRadius: 25,
  },
  imageNavRight: {
    right: 0,
    borderTopLeftRadius: 25,
    borderBottomLeftRadius: 25,
  },
  imageIndicators: {
    position: 'absolute',
    top: 60,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 6,
    zIndex: 2,
  },
  indicator: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: 'rgba(255,255,255,0.4)',
  },
  activeIndicator: {
    backgroundColor: 'white',
    width: 20,
  },
  gradientOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.3)',
  },
  contentContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'space-between',
    padding: 20,
    paddingTop: 60,
    paddingBottom: 100,
  },
  topInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  categoryBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
  },
  categoryText: {
    color: 'white',
    fontSize: 12,
    fontWeight: '600',
  },
  playButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomContent: {
    gap: 12,
  },
  subtitleContainer: {
    backgroundColor: 'rgba(0,0,0,0.8)',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    alignSelf: 'flex-start',
    maxWidth: '90%',
    marginBottom: 8,
  },
  subtitleText: {
    color: '#FFD700', // Altın renk - sesle senkronize
    fontSize: 16,
    fontWeight: '600',
    lineHeight: 22,
  },
  titleContainer: {
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 10,
    marginBottom: 8,
  },
  title: {
    color: 'white',
    fontSize: 22,
    fontWeight: 'bold',
    lineHeight: 28,
  },
  summaryContainer: {
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    marginBottom: 8,
  },
  summaryText: {
    color: 'rgba(255,255,255,0.9)',
    fontSize: 16,
    lineHeight: 22,
    fontStyle: 'italic',
  },
  authorInfo: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 14,
  },
  tagsContainer: {
    flexDirection: 'row',
    gap: 8,
    flexWrap: 'wrap',
  },
  tag: {
    color: '#3B82F6',
    fontSize: 14,
    fontWeight: '500',
  },
  progressContainer: {
    position: 'absolute',
    bottom: 40,
    left: 20,
    right: 20,
    zIndex: 10,
  },
  progressBar: {
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.3)',
    borderRadius: 2,
  },
  progressFill: {
    height: '100%',
    backgroundColor: 'white',
    borderRadius: 2,
  },
});