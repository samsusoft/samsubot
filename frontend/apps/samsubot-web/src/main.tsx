import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css'; // If you're using Tailwind CSS styles

const root = ReactDOM.createRoot(document.getElementById('root') as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);