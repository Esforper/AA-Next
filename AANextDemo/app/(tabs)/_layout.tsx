import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#007AFF',
        headerShown: false,
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Haberler',
          tabBarIcon: ({ color, focused }: { color: string; focused: boolean }) => (
            <Ionicons 
              name={focused ? 'newspaper' : 'newspaper-outline'} 
              color={color} 
              size={24} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="reels"
        options={{
          title: 'Reels',
          tabBarIcon: ({ color, focused }: { color: string; focused: boolean }) => (
            <Ionicons 
              name={focused ? 'play-circle' : 'play-circle-outline'} 
              color={color} 
              size={24} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="games"
        options={{
          title: 'Oyunlar',
          tabBarIcon: ({ color, focused }: { color: string; focused: boolean }) => (
            <Ionicons 
              name={focused ? 'game-controller' : 'game-controller-outline'} 
              color={color} 
              size={24} 
            />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profil',
          tabBarIcon: ({ color, focused }: { color: string; focused: boolean }) => (
            <Ionicons 
              name={focused ? 'person' : 'person-outline'} 
              color={color} 
              size={24} 
            />
          ),
        }}
      />
    </Tabs>
  );
}