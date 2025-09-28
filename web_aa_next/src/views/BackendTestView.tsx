import React, { useState, useEffect } from 'react';
import { ReelsApi } from '../api/reelsApi';

export const BackendTestView: React.FC = () => {
  const [testResults, setTestResults] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const runTests = async () => {
    setLoading(true);
    const results: any = {};

    try {
      // Test scraped news
      console.log('Testing scraped news...');
      const scrapedNews = await ReelsApi.fetchScrapedNews(2);
      results.scrapedNews = { success: true, data: scrapedNews };
    } catch (error) {
      results.scrapedNews = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test generate reels
      console.log('Testing generate reels...');
      const generateReels = await ReelsApi.generateReels(2, 'alloy');
      results.generateReels = { success: true, data: generateReels };
    } catch (error) {
      results.generateReels = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test categories
      console.log('Testing categories...');
      const categories = await ReelsApi.fetchCategories();
      results.categories = { success: true, data: categories };
    } catch (error) {
      results.categories = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test stats
      console.log('Testing stats...');
      const stats = await ReelsApi.fetchStats();
      results.stats = { success: true, data: stats };
    } catch (error) {
      results.stats = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test legacy compatibility
      console.log('Testing legacy reels...');
      const legacyReels = await ReelsApi.fetchReelsMix(2);
      results.legacyReels = { success: true, data: legacyReels };
    } catch (error) {
      results.legacyReels = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    setTestResults(results);
    setLoading(false);
  };

  useEffect(() => {
    runTests();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Backend API Integration Test
        </h1>
        
        <div className="mb-6">
          <button
            onClick={runTests}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Running Tests...' : 'Run Tests Again'}
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(testResults).map(([testName, result]: [string, any]) => (
            <div key={testName} className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-lg font-semibold mb-2 capitalize">
                {testName.replace(/([A-Z])/g, ' $1').trim()}
              </h3>
              <div className={`p-3 rounded ${result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                <p className="font-medium">
                  {result.success ? '✅ Success' : '❌ Failed'}
                </p>
                {result.error && (
                  <p className="text-sm mt-1">Error: {result.error}</p>
                )}
                {result.data && (
                  <div className="mt-2">
                    <p className="text-sm">
                      <strong>Response:</strong> {JSON.stringify(result.data, null, 2).substring(0, 200)}...
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {Object.keys(testResults).length === 0 && !loading && (
          <div className="text-center text-gray-500">
            No test results yet. Click "Run Tests" to start.
          </div>
        )}
      </div>
    </div>
  );
};

