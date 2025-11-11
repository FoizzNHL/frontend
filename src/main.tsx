import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import LEDControllerTest from './pages/LEDControllerTest.tsx';
import NhlPage from './pages/NhlPage.tsx';
import { SoundProvider } from './providers/SoundProvider.tsx';

 const router = createBrowserRouter([
      {
        path: '/',
        element: <App />,
        children: [
          {
            index: true, // This makes Home the default child route for '/'
            element: <NhlPage />,
          },
          {
            path: '/tests', // This makes Home the default child route for '/'
            element: <LEDControllerTest />,
          }
        ],
      },
      // You can add more top-level routes here
    ]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SoundProvider
      sounds={{
        horn: "/sounds/horn.mp3",
        buuu: "/sounds/buuu.mp3",
      }}
    >
    <RouterProvider router={router} />
    </SoundProvider>
  </StrictMode>,
)
