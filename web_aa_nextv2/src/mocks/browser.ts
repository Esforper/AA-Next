import { setupWorker } from 'msw';
import { handlers } from './handlers';

// Setup MSW browser worker for development
export const worker = setupWorker(...handlers);

// Start the worker in development mode
if (process.env.NODE_ENV === 'development') {
  worker.start({
    onUnhandledRequest: 'bypass'
  });
}