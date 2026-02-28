import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { GlobalProvider } from './contexts/GlobalContext';
import { BrowserRouter } from 'react-router-dom';

// Global API Unwrapper (Fixing 44 Sidebar Menus)
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  const response = await originalFetch(...args);

  // Clone the response to override json() method safely
  const responseClone = response.clone();
  responseClone.json = async () => {
    const data = await response.json();
    if (data && typeof data === 'object' && 'success' in data && 'data' in data && 'request_id' in data) {
      // It's the standard backend envelope, unwrap it for the frontend components
      return data.data;
    }
    return data;
  };

  return responseClone;
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <GlobalProvider>
        <App />
      </GlobalProvider>
    </BrowserRouter>
  </StrictMode>,
);

