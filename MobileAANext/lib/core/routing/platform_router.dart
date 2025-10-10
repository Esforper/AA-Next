// lib/core/routing/platform_router.dart
// Platform-aware widget routing sistemi
// Mobile kodları olduğu gibi kullanır, web için override varsa onu yükler

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';

/// Platform-specific widget loader
/// 
/// Kullanım:
/// ```dart
/// PlatformRouter.load(
///   mobile: () => MobileHomeView(),
///   web: () => WebHomeView(), // Opsiyonel, yoksa mobile kullanılır
/// )
/// ```
class PlatformRouter {
  
  /// Widget yükleyici (lazy loading)
  static Widget load({
    required Widget Function() mobile,
    Widget Function()? web,
  }) {
    if (kIsWeb && web != null) {
      return web();
    }
    return mobile();
  }

  /// Page route oluşturucu
  static Route<T> route<T>({
    required Widget Function() mobile,
    Widget Function()? web,
    RouteSettings? settings,
  }) {
    return MaterialPageRoute<T>(
      builder: (_) => load(mobile: mobile, web: web),
      settings: settings,
    );
  }

  /// Named route için builder
  static WidgetBuilder builder({
    required Widget Function() mobile,
    Widget Function()? web,
  }) {
    return (_) => load(mobile: mobile, web: web);
  }
}

/// Responsive wrapper - Layout için
class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;
  
  const ResponsiveLayout({
    Key? key,
    required this.mobile,
    this.tablet,
    this.desktop,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < 600) {
          return mobile;
        } else if (constraints.maxWidth < 1024) {
          return tablet ?? mobile;
        } else {
          return desktop ?? tablet ?? mobile;
        }
      },
    );
  }
}

/// Web için maksimum genişlik wrapper
class WebConstrainedWidth extends StatelessWidget {
  final Widget child;
  final double maxWidth;
  final Color? backgroundColor;
  
  const WebConstrainedWidth({
    Key? key,
    required this.child,
    this.maxWidth = 1200,
    this.backgroundColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (!kIsWeb) return child;
    
    return Container(
      color: backgroundColor ?? Colors.grey[100],
      child: Center(
        child: Container(
          constraints: BoxConstraints(maxWidth: maxWidth),
          color: Colors.white,
          child: child,
        ),
      ),
    );
  }
}

/// Platform-aware scaffold
class PlatformScaffold extends StatelessWidget {
  final Widget body;
  final PreferredSizeWidget? appBar;
  final Widget? bottomNavigationBar;
  final Widget? floatingActionButton;
  final bool useWebLayout;
  
  const PlatformScaffold({
    Key? key,
    required this.body,
    this.appBar,
    this.bottomNavigationBar,
    this.floatingActionButton,
    this.useWebLayout = true,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final scaffold = Scaffold(
      appBar: appBar,
      body: body,
      bottomNavigationBar: bottomNavigationBar,
      floatingActionButton: floatingActionButton,
    );
    
    // Web'de constrained layout
    if (kIsWeb && useWebLayout) {
      return WebConstrainedWidth(child: scaffold);
    }
    
    return scaffold;
  }
}

/// Conditional widget builder
class PlatformBuilder extends StatelessWidget {
  final Widget mobile;
  final Widget? web;
  
  const PlatformBuilder({
    Key? key,
    required this.mobile,
    this.web,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return PlatformRouter.load(
      mobile: () => mobile,
      web: web != null ? () => web! : null,
    );
  }
}