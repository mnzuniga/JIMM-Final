import React from 'react';

function Feed() {
  return (
    <div className="feed-container">
      <h1>Feed</h1>
      <div className="feed-item">
        <img src="https://via.placeholder.com/300" alt="Post" />
        <p className="caption">This is a sample post!</p>
      </div>
      {/* Add more feed items here */}
    </div>
  );
}

export default Feed;
