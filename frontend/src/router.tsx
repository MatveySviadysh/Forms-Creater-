import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home/Home';
import CreateForm from './pages/CreateForm/index';

const AppRouter: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/create-form" element={<CreateForm />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;