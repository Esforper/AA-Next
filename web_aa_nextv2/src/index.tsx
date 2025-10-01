import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Initialize MSW
async function initMocks() {
  if (process.env.NODE_ENV === 'development') {
    try {
      const { worker } = await import('./mocks/browser');
      await worker.start({
        onUnhandledRequest: 'bypass'
      });
      console.log('MSW started successfully');
    } catch (error) {
      console.warn('MSW failed to start:', error);
    }
  }
}

// Start the application
const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);

// Initialize mocks and render app
initMocks().finally(() => {
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
