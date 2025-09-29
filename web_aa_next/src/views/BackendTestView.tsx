// src/views/BackendTestView.tsx - Updated for Real API

import React, { useState, useEffect } from 'react';
import { ReelsApi } from '../api/reelsApi';

export const BackendTestView: React.FC = () => {
  const [testResults, setTestResults] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const runTests = async () => {
    setLoading(true);
    const results: any = {};

    try {
      // Test infinite feed
      console.log('Testing infinite feed...');
      const feedResult = await ReelsApi.fetchInfiniteFeed({ limit: 3 });
      results.infiniteFeed = { success: true, data: feedResult };
    } catch (error) {
      results.infiniteFeed = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test trending reels
      console.log('Testing trending reels...');
      const trending = await ReelsApi.fetchTrendingReels({ limit: 3 });
      results.trending = { success: true, data: trending };
    } catch (error) {
      results.trending = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test user progress
      console.log('Testing user progress...');
      const progress = await ReelsApi.fetchUserProgress();
      results.userProgress = { success: true, data: progress };
    } catch (error) {
      results.userProgress = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test view tracking
      console.log('Testing view tracking...');
      const trackResult = await ReelsApi.trackReelView({
        reel_id: 'test_reel_123',
        duration_ms: 5000,
        completed: true,
        category: 'test'
      });
      results.tracking = { success: true, data: trackResult };
    } catch (error) {
      results.tracking = { success: false, error: error instanceof Error ? error.message : String(error) };
    }

    try {
      // Test legacy compatibility
      console.log('Testing legacy reels mix...');
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

  const renderTestResult = (testName: string, result: any) => {
    const isSuccess = result?.success;
    
    return (
      <div key={testName} className="border rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold capitalize">
            {testName.replace(/([A-Z])/g, ' $1').trim()}
          </h3>
          <span className={`px-2 py-1 rounded text-sm ${
            isSuccess ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isSuccess ? 'Success' : 'Failed'}
          </span>
        </div>
        
        <div className="bg-gray-50 rounded p-3 text-sm">
          {isSuccess ? (
            <div>
              <div className="text-green-600 mb-2">✅ Test passed</div>
              {result.data && (
                <details>
                  <summary className="cursor-pointer text-blue-600">View Response</summary>
                  <pre className="mt-2 text-xs overflow-x-auto bg-white p-2 rounded">
                    {JSON.stringify(result.data, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          ) : (
            <div>
              <div className="text-red-600 mb-2">❌ Test failed</div>
              <div className="text-red-700 font-mono text-xs">
                {result?.error || 'Unknown error'}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Real Backend API Integration Test
        </h1>
        
        <div className="mb-6">
          <button
            onClick={runTests}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Run Tests'}
          </button>
          
          <div className="mt-2 text-sm text-gray-600">
            Testing real RSS-based backend APIs
          </div>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">Running API tests...</span>
          </div>
        )}

        <div className="space-y-4">
          {Object.entries(testResults).map(([testName, result]) => 
            renderTestResult(testName, result)
          )}
        </div>

        {Object.keys(testResults).length > 0 && (
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">API Endpoints Tested:</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• GET /api/reels/feed - Infinite scroll feed</li>
              <li>• GET /api/reels/trending - Trending reels</li>
              <li>• GET /api/reels/user/[id]/daily-progress - User progress</li>
              <li>• POST /api/reels/track-view - View tracking</li>
              <li>• Legacy compatibility endpoints</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};