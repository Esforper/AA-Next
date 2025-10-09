// lib/widgets/subtitle_widget.dart
import 'package:flutter/material.dart';
import '../models/reel_model.dart';

class SubtitleWidget extends StatelessWidget {
  final List<SubtitleSegment> subtitles;
  final Duration currentPosition;
  final bool isVisible;

  const SubtitleWidget({
    super.key,
    required this.subtitles,
    required this.currentPosition,
    this.isVisible = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!isVisible || subtitles.isEmpty) return const SizedBox.shrink();

    final currentSub = _getCurrentSubtitle();
    if (currentSub == null) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      margin: const EdgeInsets.symmetric(horizontal: 32),
      decoration: BoxDecoration(
        color: Colors.black.withOpacity(0.7),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        currentSub.text,
        textAlign: TextAlign.center,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w500,
          height: 1.4,
        ),
      ),
    );
  }

  SubtitleSegment? _getCurrentSubtitle() {
    final currentSec = currentPosition.inMilliseconds / 1000.0;
    
    for (final sub in subtitles) {
      if (currentSec >= sub.startTime && currentSec <= sub.endTime) {
        return sub;
      }
    }
    return null;
  }
}