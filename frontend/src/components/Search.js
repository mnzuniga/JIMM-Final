// takes input and displays usernames -->
import React, { useState } from 'react';

function Search() {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = () => {
    console.log('Search for:', searchTerm);
    // You can implement actual search functionality here
  };

  return (
    <div>
      <h1>Search</h1>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search for posts, users..."
      />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}

export default Search;
