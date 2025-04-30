//creating a post -->
import React, { useState } from 'react';

function UploadPost() {
  const [postContent, setPostContent] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle the post upload logic
    console.log('Post uploaded:', postContent);
  };

  return (
    <div>
      <h1>Upload Post</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={postContent}
          onChange={(e) => setPostContent(e.target.value)}
          placeholder="What do you want to share?"
        ></textarea>
        <button type="submit">Upload</button>
      </form>
    </div>
  );
}

export default UploadPost;
