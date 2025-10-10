// lib/shared/widgets/error_view.dart
// Hata durumu gösterimi

import 'package:flutter/material.dart';
import '../../core/constants/app_constants.dart';

class ErrorView extends StatelessWidget {
  final String message;
  final String? details;
  final VoidCallback? onRetry;
  final IconData icon;
  
  const ErrorView({
    Key? key,
    required this.message,
    this.details,
    this.onRetry,
    this.icon = Icons.error_outline,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: AppSpacing.pagePadding,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 64, color: AppColors.error),
            const SizedBox(height: 16),
            Text(message, style: AppTextStyles.h4, textAlign: TextAlign.center),
            if (details != null) ...[
              const SizedBox(height: 8),
              Text(details!, style: AppTextStyles.bodySmall, textAlign: TextAlign.center),
            ],
            if (onRetry != null) ...[
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: const Text('Tekrar Dene'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}