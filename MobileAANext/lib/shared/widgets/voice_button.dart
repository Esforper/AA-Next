import 'package:flutter/material.dart';

class VoiceButton extends StatelessWidget {
  final bool speaking;
  final VoidCallback onToggle;
  const VoiceButton(
      {super.key, required this.speaking, required this.onToggle});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.black.withOpacity(0.45),
      shape: const CircleBorder(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onToggle,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Icon(
            speaking ? Icons.volume_off_rounded : Icons.volume_up_rounded,
            color: Colors.white,
            size: 28,
          ),
        ),
      ),
    );
  }
}
