import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import Feed from './components/Feed';
import Profile from './components/Profile';
import EditProfile from './components/EditProfile';
import UploadPost from './components/UploadPost';
import Search from './components/Search';
import Discover from './components/Discover';
import Login from './components/Login';
import Register from './components/Register';
import RecoverAccount from './components/RecoverAccount';

import './styles/main.css';

function App() {
  return (
    <Router>
      <NavBar />
      <Routes>
        <Route path="/" element={<Feed />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/recover" element={<RecoverAccount />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/edit-profile" element={<EditProfile />} />
        <Route path="/upload" element={<UploadPost />} />
        <Route path="/search" element={<Search />} />
        <Route path="/discover" element={<Discover />} />
      </Routes>
    </Router>
  );
}

export default App;
