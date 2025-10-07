import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { 
  HomeView, 
  ReelsView, 
  GamesView, 
  ProfileView, 
  NewsDetailView, 
  TestView, 
  SimpleHomeView, 
  BackendTestView,
  GameRaceView  // ✅ Import ekle
} from './views';
import { TabBar } from './components';
import { useNavigationViewModel } from './viewmodels';

const AppContent: React.FC = () => {
  const location = useLocation();
  const { activeTab, tabs, setActiveTab } = useNavigationViewModel();

  // Update active tab based on current route
  React.useEffect(() => {
    const currentPath = location.pathname;
    
    if (currentPath === '/' || currentPath === '/home' || currentPath.startsWith('/news')) {
      setActiveTab('home');
    } else if (currentPath === '/reels') {
      setActiveTab('reels');
    } else if (currentPath === '/games') {
      setActiveTab('games');
    } else if (currentPath === '/race') {  // ✅ Race route
      setActiveTab('games');  // Race'i games tab'ı altında göster
    } else if (currentPath === '/profile') {
      setActiveTab('profile');
    }
  }, [location.pathname, setActiveTab]);

  const navigate = useNavigate();
  
  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    
    // Navigate to the corresponding route
    switch (tabId) {
      case 'home':
        navigate('/');
        break;
      case 'reels':
        navigate('/reels');
        break;
      case 'games':
        navigate('/games');
        break;
      case 'profile':
        navigate('/profile');
        break;
    }
  };

  const isReels = location.pathname === '/reels';
  const isEmbed = new URLSearchParams(location.search).get('embed') === '1';
  // Don't show tab bar on news detail pages or race view; hide in embed mode
  const showTabBar = !location.pathname.startsWith('/news/') && 
                     !location.pathname.startsWith('/race') &&
                     !isEmbed;

  return (
    <div className="min-h-screen bg-gray-50 relative">
      {/* Top Navigation - Desktop/Web Only */}
      {!isEmbed && (
      <div className="hidden sm:block shadow-lg sticky top-0 z-40" style={{ backgroundColor: '#005799' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 grid grid-cols-3 items-center">
          <div className="flex items-center">
            <span className="text-xl font-bold text-white">AA Haber</span>
          </div>
          <div className="flex items-center justify-center gap-2">
            <button 
              onClick={() => handleTabChange('home')} 
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab==='home' 
                  ? 'bg-white text-blue-600 shadow-md' 
                  : 'text-white hover:bg-white/20 hover:text-white'
              }`}
            >
              Haberler
            </button>
            <button 
              onClick={() => handleTabChange('reels')} 
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab==='reels' 
                  ? 'bg-white text-blue-600 shadow-md' 
                  : 'text-white hover:bg-white/20 hover:text-white'
              }`}
            >
              Reels
            </button>
            <button 
              onClick={() => handleTabChange('games')} 
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab==='games' 
                  ? 'bg-white text-blue-600 shadow-md' 
                  : 'text-white hover:bg-white/20 hover:text-white'
              }`}
            >
              Oyunlar
            </button>
            <button 
              onClick={() => handleTabChange('profile')} 
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                activeTab==='profile' 
                  ? 'bg-white text-blue-600 shadow-md' 
                  : 'text-white hover:bg-white/20 hover:text-white'
              }`}
            >
              Profil
            </button>
          </div>
          <div />
        </div>
      </div>
      )}
      {/* Main Content Area */}
      <div className={isReels ? 'pb-16 sm:pb-0 overflow-hidden' : 'pb-16 sm:pb-20'}>
        <Routes>
          <Route path="/" element={<TestView />} />
          <Route path="/home" element={<SimpleHomeView />} />
          <Route path="/reels" element={<ReelsView />} />
          <Route path="/games" element={<GamesView />} />
          <Route path="/race" element={<GameRaceView />} />  {/* ✅ Yeni route */}
          <Route path="/profile" element={<ProfileView />} />
          <Route path="/news/:id" element={<NewsDetailView />} />
          <Route path="/backend-test" element={<BackendTestView />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
      
      {/* Bottom Tab Bar - Mobile Only */}
      {showTabBar && (
        <TabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={handleTabChange}
          className="sm:hidden"
        />
      )}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true } as any}>
      <AppContent />
    </Router>
  );
};

export default App;