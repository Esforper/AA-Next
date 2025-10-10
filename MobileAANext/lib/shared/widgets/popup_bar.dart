import 'package:flutter/material.dart';

class PopupBar extends StatelessWidget implements PreferredSizeWidget {
  const PopupBar({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(48);

  @override
  Widget build(BuildContext context) {
    return AppBar(
      scrolledUnderElevation: 0,
      titleSpacing: 12,
      title:
          const Text('AA-Next', style: TextStyle(fontWeight: FontWeight.w700)),
      actions: const [
        _IconBtn(icon: Icons.notifications_none),
        _IconBtn(icon: Icons.tune),
        SizedBox(width: 8),
      ],
    );
  }
}

class _IconBtn extends StatelessWidget {
  final IconData icon;
  const _IconBtn({required this.icon});
  @override
  Widget build(BuildContext context) {
    return IconButton(onPressed: () {}, icon: Icon(icon));
  }
}
