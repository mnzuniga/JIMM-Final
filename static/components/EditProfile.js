// page to edit your username, pfp, and bio 
import React, { useState } from 'react';

function EditProfile() {
  const [username, setUsername] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Add the logic for updating the profile here
    console.log('Profile updated:', username);
  };

  return (
    <div>
      <h1>Edit Profile</h1>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={username} 
          onChange={(e) => setUsername(e.target.value)} 
          placeholder="New Username" 
        />
        <button type="submit">Save</button>
      </form>
    </div>
  );
}

export default EditProfile;
