// lib/web_platform/widgets/web_audio_player.dart
// WEB İÇİN SES OYNATICI KONTROL WIDGET'I
// Mobile SubtitleWidget + AudioService entegrasyonu

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../services/audio_service.dart';
import '../../models/reel_model.dart';
import '../../shared/widgets/subtitle_widget.dart';

class WebAudioPlayer extends StatefulWidget {
  final Reel reel;
  final VoidCallback? onPlaybackComplete;

  const WebAudioPlayer({
    super.key,
    required this.reel,
    this.onPlaybackComplete,
  });

  @override
  State<WebAudioPlayer> createState() => _WebAudioPlayerState();
}

class _WebAudioPlayerState extends State<WebAudioPlayer> {
  bool _subtitlesEnabled = true;

  @override
  void initState() {
    super.initState();
    
    // Otomatik başlat
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final audioService = context.read<AudioService>();
      
      if (widget.reel.audioUrl.isNotEmpty) {
        debugPrint('🎵 Web: Starting audio for ${widget.reel.id}');
        audioService.play(widget.reel.audioUrl, widget.reel.id);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<AudioService>(
      builder: (context, audioService, _) {
        final isPlaying = audioService.isPlaying;
        final position = audioService.position;
        final duration = audioService.duration;
        final hasAudio = widget.reel.audioUrl.isNotEmpty;

        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Altyazı overlay (subtitle)
            if (_subtitlesEnabled && 
                widget.reel.subtitles != null && 
                widget.reel.subtitles!.isNotEmpty)
              Container(
                height: 80,
                alignment: Alignment.center,
                child: SubtitleWidget(
                  subtitles: widget.reel.subtitles!,
                  currentPosition: position,
                  isVisible: _subtitlesEnabled,
                ),
              ),

            const SizedBox(height: 16),

            // Player kontrolü
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.1),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Progress bar
                  if (hasAudio && duration.inMilliseconds > 0)
                    Column(
                      children: [
                        // Slider
                        SliderTheme(
                          data: SliderThemeData(
                            trackHeight: 4,
                            thumbShape: const RoundSliderThumbShape(
                              enabledThumbRadius: 8,
                            ),
                            overlayShape: const RoundSliderOverlayShape(
                              overlayRadius: 16,
                            ),
                          ),
                          child: Slider(
                            value: position.inMilliseconds.toDouble(),
                            max: duration.inMilliseconds.toDouble(),
                            activeColor: const Color(0xFF003D82),
                            inactiveColor: Colors.grey[300],
                            onChanged: (value) {
                              audioService.seek(
                                Duration(milliseconds: value.toInt()),
                              );
                            },
                          ),
                        ),

                        // Time labels
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 8),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                _formatDuration(position),
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                              Text(
                                _formatDuration(duration),
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                  const SizedBox(height: 16),

                  // Kontrol butonları
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Geri sar (-10s)
                      IconButton(
                        onPressed: hasAudio
                            ? () {
                                final newPos = position - const Duration(seconds: 10);
                                audioService.seek(
                                  newPos < Duration.zero ? Duration.zero : newPos,
                                );
                              }
                            : null,
                        icon: const Icon(Icons.replay_10),
                        iconSize: 28,
                        color: const Color(0xFF003D82),
                        tooltip: '10 saniye geri',
                      ),

                      const SizedBox(width: 16),

                      // Play/Pause butonu (BÜYÜK)
                      Container(
                        width: 64,
                        height: 64,
                        decoration: BoxDecoration(
                          color: const Color(0xFF003D82),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF003D82).withValues(alpha: 0.3),
                              blurRadius: 12,
                              offset: const Offset(0, 4),
                            ),
                          ],
                        ),
                        child: IconButton(
                          onPressed: hasAudio
                              ? () {
                                  if (isPlaying) {
                                    audioService.pause();
                                  } else {
                                    audioService.resume();
                                  }
                                }
                              : null,
                          icon: Icon(
                            isPlaying ? Icons.pause : Icons.play_arrow,
                            color: Colors.white,
                            size: 36,
                          ),
                          tooltip: isPlaying ? 'Duraklat' : 'Oynat',
                        ),
                      ),

                      const SizedBox(width: 16),

                      // İleri sar (+10s)
                      IconButton(
                        onPressed: hasAudio
                            ? () {
                                final newPos = position + const Duration(seconds: 10);
                                audioService.seek(
                                  newPos > duration ? duration : newPos,
                                );
                              }
                            : null,
                        icon: const Icon(Icons.forward_10),
                        iconSize: 28,
                        color: const Color(0xFF003D82),
                        tooltip: '10 saniye ileri',
                      ),

                      const SizedBox(width: 24),

                      // Altyazı toggle
                      if (widget.reel.subtitles != null && 
                          widget.reel.subtitles!.isNotEmpty)
                        IconButton(
                          onPressed: () {
                            setState(() => _subtitlesEnabled = !_subtitlesEnabled);
                          },
                          icon: Icon(
                            _subtitlesEnabled
                                ? Icons.closed_caption
                                : Icons.closed_caption_disabled,
                            color: _subtitlesEnabled
                                ? const Color(0xFF003D82)
                                : Colors.grey,
                          ),
                          iconSize: 28,
                          tooltip: _subtitlesEnabled
                              ? 'Altyazıları gizle'
                              : 'Altyazıları göster',
                        ),
                    ],
                  ),

                  // Ses uyarısı (eğer ses yoksa)
                  if (!hasAudio)
                    Padding(
                      padding: const EdgeInsets.only(top: 16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.volume_off, color: Colors.grey[400], size: 20),
                          const SizedBox(width: 8),
                          Text(
                            'Bu haber için ses dosyası yok',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 13,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  String _formatDuration(Duration duration) {
    final minutes = duration.inMinutes;
    final seconds = duration.inSeconds % 60;
    return '${minutes.toString().padLeft(1, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    // Ses durdur
    final audioService = context.read<AudioService>();
    audioService.stop();
    super.dispose();
  }
}