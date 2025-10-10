// lib/widgets/reading_settings_panel.dart

import 'package:flutter/material.dart';
import '../../models/reading_preferences.dart';
import '../../services/reading_preferences_service.dart';

/// Kullanıcının okuma ayarlarını (font boyutu, ailesi, satır aralığı)
/// değiştirebileceği bir bottom sheet paneli.
class ReadingSettingsPanel extends StatefulWidget {
  /// Panelin başlangıçta göstereceği ayarlar.
  final ReadingPreferences initialPreferences;

  /// Ayarlardan biri değiştiğinde tetiklenir ve yeni ayarları döner.
  final ValueChanged<ReadingPreferences> onChanged;

  const ReadingSettingsPanel({
    super.key,
    required this.initialPreferences,
    required this.onChanged,
  });

  @override
  State<ReadingSettingsPanel> createState() => _ReadingSettingsPanelState();
}

class _ReadingSettingsPanelState extends State<ReadingSettingsPanel> {
  late ReadingPreferences _currentPreferences;
  final _prefsService = ReadingPreferencesService.instance;

  @override
  void initState() {
    super.initState();
    _currentPreferences = widget.initialPreferences;
  }

  // Ayarları güncelleyen, kaydeden ve parent widget'ı bilgilendiren merkezi fonksiyon.
  void _updatePreferences(ReadingPreferences newPrefs) {
    // State'i güncelleyerek UI'ın yeniden çizilmesini sağla
    setState(() {
      _currentPreferences = newPrefs;
    });

    // Değişikliği anında ArticleReaderSheet'e bildir
    widget.onChanged(newPrefs);

    // Yeni ayarları kalıcı olarak cihaza kaydet
    _prefsService.savePreferences(newPrefs);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          _buildSectionTitle('Yazı Tipi Boyutu'),
          const SizedBox(height: 12),
          _buildFontSizeSelector(),
          const SizedBox(height: 24),
          _buildSectionTitle('Font Ailesi'),
          const SizedBox(height: 12),
          _buildFontFamilySelector(),
          const SizedBox(height: 24),
          _buildSectionTitle('Satır Aralığı'),
          const SizedBox(height: 12),
          _buildLineHeightSelector(),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Center(
      child: Container(
        width: 48,
        height: 5,
        decoration: BoxDecoration(
          color: Colors.grey[300],
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: Colors.grey[700],
      ),
    );
  }

  Widget _buildFontSizeSelector() {
    return SegmentedButton<AppFontSize>(
      segments: const [
        ButtonSegment(
          value: AppFontSize.small,
          label: Text('Küçük'),
          icon: Icon(Icons.text_fields_sharp, size: 16),
        ),
        ButtonSegment(
          value: AppFontSize.medium,
          label: Text('Orta'),
          icon: Icon(Icons.text_fields_sharp, size: 20),
        ),
        ButtonSegment(
          value: AppFontSize.large,
          label: Text('Büyük'),
          icon: Icon(Icons.text_fields_sharp, size: 24),
        ),
      ],
      selected: <AppFontSize>{_currentPreferences.fontSize},
      onSelectionChanged: (newSelection) {
        _updatePreferences(
          _currentPreferences.copyWith(fontSize: newSelection.first),
        );
      },
      style: SegmentedButton.styleFrom(
        selectedBackgroundColor: Theme.of(context).primaryColor.withOpacity(0.15),
        selectedForegroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.grey[600],
      ),
    );
  }

  Widget _buildFontFamilySelector() {
    return SegmentedButton<AppFontFamily>(
      segments: const [
        ButtonSegment(value: AppFontFamily.system, label: Text('Sistem')),
        ButtonSegment(value: AppFontFamily.serif, label: Text('Serif')),
        ButtonSegment(value: AppFontFamily.sansSerif, label: Text('Sans-Serif')),
      ],
      selected: <AppFontFamily>{_currentPreferences.fontFamily},
      onSelectionChanged: (newSelection) {
        _updatePreferences(
          _currentPreferences.copyWith(fontFamily: newSelection.first),
        );
      },
      style: SegmentedButton.styleFrom(
        selectedBackgroundColor: Theme.of(context).primaryColor.withOpacity(0.15),
        selectedForegroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.grey[600],
      ),
    );
  }

  Widget _buildLineHeightSelector() {
    return SegmentedButton<AppLineHeight>(
      segments: const [
        ButtonSegment(
            value: AppLineHeight.compact,
            label: Text('Sıkı'),
            icon: Icon(Icons.format_line_spacing_rounded)),
        ButtonSegment(
            value: AppLineHeight.normal,
            label: Text('Normal'),
            icon: Icon(Icons.format_line_spacing_rounded)),
        ButtonSegment(
            value: AppLineHeight.relaxed,
            label: Text('Geniş'),
            icon: Icon(Icons.format_line_spacing_rounded)),
      ],
      selected: <AppLineHeight>{_currentPreferences.lineHeight},
      onSelectionChanged: (newSelection) {
        _updatePreferences(
          _currentPreferences.copyWith(lineHeight: newSelection.first),
        );
      },
      style: SegmentedButton.styleFrom(
        selectedBackgroundColor: Theme.of(context).primaryColor.withOpacity(0.15),
        selectedForegroundColor: Theme.of(context).primaryColor,
        foregroundColor: Colors.grey[600],
      ),
    );
  }
}