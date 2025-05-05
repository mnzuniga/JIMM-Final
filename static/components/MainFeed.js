import React, { useEffect, useState } from 'react';

function MainFeed() {
  // State to store posts
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);  // For loading state
  const [error, setError] = useState(null);  // For error handling

  // Fetch posts when the component is mounted
  useEffect(() => {
    // Replace with our actual API endpoint
    const fetchPosts = async () => {
      try {
        const response = await fetch('/api/posts');  // add our API endpoint for posts
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const data = await response.json();
        setPosts(data);  // Set the posts data in state
      } catch (err) {
        setError(err.message);  // Set error if the API call fails
      } finally {
        setLoading(false);  // Set loading state to false
      }
    };

    fetchPosts();
  }, []);  // Empty dependency array ensures this effect runs once when component mounts

  // Render loading state or error message if necessary
  if (loading) {
    return <p>Loading posts...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div>
      <h1>Main Feed</h1>
      {/* Display posts */}
      {posts.length === 0 ? (
        <p>No posts available.</p>
      ) : (
        <div className="post-list">
          {posts.map(post => (
            <div key={post.id} className="post-item">
              <h2>{post.title}</h2>
              <p>{post.description}</p>
              <img src={post.photo_url} alt={post.title} />
              {/* If you have tags or links, you can display them here */}
              {post.tags && <p>Tags: {post.tags.join(', ')}</p>}
              {post.link && <a href={post.link} target="_blank" rel="noopener noreferrer">View more</a>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default MainFeed;
