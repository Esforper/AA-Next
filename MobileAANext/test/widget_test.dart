import 'package:flutter_test/flutter_test.dart';
import 'package:mobile_aanext/main.dart';

void main() {
  testWidgets('AA-Next app loads successfully', (WidgetTester tester) async {
    // Uygulamayı başlat
    await tester.pumpWidget(const AanextApp());

    // Başlık veya text içerik kontrolü
    expect(find.text('AA-Next'), findsOneWidget);
  });
}
