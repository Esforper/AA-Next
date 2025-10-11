// lib/web_platform/widgets/web_category_dropdown.dart
// 📂 Web için Kategori Dropdown Widget

import 'package:flutter/material.dart';
import '../../core/theme/aa_colors.dart';

class WebCategoryDropdown extends StatefulWidget {
  final Function(String categoryId, String categoryName, String categoryIcon, Color categoryColor) onCategorySelected;

  const WebCategoryDropdown({
    Key? key,
    required this.onCategorySelected,
  }) : super(key: key);

  @override
  State<WebCategoryDropdown> createState() => _WebCategoryDropdownState();
}

class _WebCategoryDropdownState extends State<WebCategoryDropdown> {
  bool _isHovered = false;
  
  final List<Map<String, dynamic>> _categories = [
    {'id': 'guncel', 'name': 'Güncel', 'icon': '📰', 'color': AAColors.catGuncel},
    {'id': 'ekonomi', 'name': 'Ekonomi', 'icon': '💰', 'color': AAColors.catEkonomi},
    {'id': 'spor', 'name': 'Spor', 'icon': '⚽', 'color': AAColors.catSpor},
    {'id': 'teknoloji', 'name': 'Teknoloji', 'icon': '💻', 'color': AAColors.catTeknoloji},
    {'id': 'kultur', 'name': 'Kültür', 'icon': '🎨', 'color': AAColors.catKultur},
    {'id': 'dunya', 'name': 'Dünya', 'icon': '🌍', 'color': AAColors.catDunya},
    {'id': 'politika', 'name': 'Politika', 'icon': '🏛️', 'color': AAColors.catPolitika},
    {'id': 'saglik', 'name': 'Sağlık', 'icon': '🏥', 'color': AAColors.catSaglik},
  ];

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<Map<String, dynamic>>(
      offset: const Offset(0, 50),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: MouseRegion(
        onEnter: (_) => setState(() => _isHovered = true),
        onExit: (_) => setState(() => _isHovered = false),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: _isHovered 
                ? Colors.white.withOpacity(0.3)
                : Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(
                Icons.apps,
                color: Colors.white,
                size: 20,
              ),
              SizedBox(width: 8),
              Text(
                'Kategoriler',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(width: 4),
              Icon(
                Icons.arrow_drop_down,
                color: Colors.white,
                size: 20,
              ),
            ],
          ),
        ),
      ),
      itemBuilder: (context) {
        return _categories.map((category) {
          return PopupMenuItem<Map<String, dynamic>>(
            value: category,
            child: Row(
              children: [
                Text(
                  category['icon'],
                  style: const TextStyle(fontSize: 20),
                ),
                const SizedBox(width: 12),
                Text(
                  category['name'],
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          );
        }).toList();
      },
      onSelected: (category) {
        widget.onCategorySelected(
          category['id'],
          category['name'],
          category['icon'],
          category['color'],
        );
      },
    );
  }
}
