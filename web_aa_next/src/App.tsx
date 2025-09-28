import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { HomeView, ReelsView, GamesView, ProfileView, NewsDetailView, TestView, SimpleHomeView, BackendTestView } from './views';
import { TabBar } from './components';
import { useNavigationViewModel } from './viewmodels';

const AppContent: React.FC = () => {
  const location = useLocation();
  const { activeTab, tabs, setActiveTab } = useNavigationViewModel();

  // Update active tab based on current route
  React.useEffect(() => {
    const currentPath = location.pathname;
    
    if (currentPath === '/' || currentPath.startsWith('/news')) {
      setActiveTab('home');
    } else if (currentPath === '/reels') {
      setActiveTab('reels');
    } else if (currentPath === '/games') {
      setActiveTab('games');
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

  // Don't show tab bar on news detail pages
  const showTabBar = !location.pathname.startsWith('/news/');

  return (
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<TestView />} />
            <Route path="/home" element={<SimpleHomeView />} />
            <Route path="/reels" element={<ReelsView />} />
            <Route path="/games" element={<GamesView />} />
            <Route path="/profile" element={<ProfileView />} />
            <Route path="/news/:id" element={<NewsDetailView />} />
            <Route path="/backend-test" element={<BackendTestView />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
      
      {showTabBar && (
        <TabBar
          tabs={tabs}
          activeTab={activeTab}
          onTabChange={handleTabChange}
        />
      )}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

export default App;