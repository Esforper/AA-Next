// lib/mobile_platform/widgets/home/category_bubble_menu.dart
// 🫧 Animated Category Bubble Menu

import 'package:flutter/material.dart';
import '../../../core/theme/aa_colors.dart';

class CategoryBubbleMenu extends StatefulWidget {
  final Function(String categoryId) onCategorySelected;

  const CategoryBubbleMenu({
    Key? key,
    required this.onCategorySelected,
  }) : super(key: key);

  @override
  State<CategoryBubbleMenu> createState() => _CategoryBubbleMenuState();
}

class _CategoryBubbleMenuState extends State<CategoryBubbleMenu>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _animController;

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
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  void _toggleMenu() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animController.forward();
      } else {
        _animController.reverse();
      }
    });
  }

  void _selectCategory(String categoryId) {
    _toggleMenu();
    Future.delayed(const Duration(milliseconds: 200), () {
      widget.onCategorySelected(categoryId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Backdrop (karartma)
        if (_isExpanded)
          GestureDetector(
            onTap: _toggleMenu,
            child: AnimatedOpacity(
              duration: const Duration(milliseconds: 300),
              opacity: _isExpanded ? 1.0 : 0.0,
              child: Container(
                color: Colors.black.withOpacity(0.5),
              ),
            ),
          ),

        // Kategori Bubble'ları
        if (_isExpanded)
          Center(
            child: Wrap(
              spacing: 12,
              runSpacing: 12,
              alignment: WrapAlignment.center,
              children: List.generate(_categories.length, (index) {
                return _buildCategoryBubble(
                  category: _categories[index],
                  delay: index * 30,
                );
              }),
            ),
          ),

        // Ana Buton
        Positioned(
          bottom: 24,
          child: _buildMainButton(),
        ),
      ],
    );
  }

  Widget _buildMainButton() {
    return GestureDetector(
      onTap: _toggleMenu,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        width: _isExpanded ? 60 : 160,
        height: 60,
        decoration: BoxDecoration(
          gradient: AAColors.redGradient,
          borderRadius: BorderRadius.circular(30),
          boxShadow: AAColors.buttonShadow,
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 200),
          child: _isExpanded
              ? const Icon(
                  Icons.close,
                  color: Colors.white,
                  size: 28,
                  key: ValueKey('close'),
                )
              : Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.apps, color: Colors.white, size: 24),
                    SizedBox(width: 8),
                    Text(
                      'Kategoriler',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                      key: ValueKey('text'),
                    ),
                  ],
                ),
        ),
      ),
    );
  }

  Widget _buildCategoryBubble({
    required Map<String, dynamic> category,
    required int delay,
  }) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.0, end: 1.0),
      duration: Duration(milliseconds: 300 + delay),
      curve: Curves.elasticOut,
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: Opacity(
            opacity: value,
            child: child,
          ),
        );
      },
      child: GestureDetector(
        onTap: () => _selectCategory(category['id']),
        child: Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: category['color'],
            shape: BoxShape.circle,
            boxShadow: [
              BoxShadow(
                color: (category['color'] as Color).withOpacity(0.4),
                blurRadius: 12,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                category['icon'],
                style: const TextStyle(fontSize: 32),
              ),
              const SizedBox(height: 4),
              Text(
                category['name'],
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// Kullanım için yardımcı widget
class CategorySelectorButton extends StatelessWidget {
  final VoidCallback onPressed;

  const CategorySelectorButton({
    Key? key,
    required this.onPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(16),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: AAColors.redGradient,
              borderRadius: BorderRadius.circular(16),
              boxShadow: AAColors.buttonShadow,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: const [
                Icon(Icons.apps, color: Colors.white, size: 24),
                SizedBox(width: 12),
                Text(
                  'Kategorilere Göz At',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Spacer(),
                Icon(Icons.arrow_forward_ios, color: Colors.white, size: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }
}