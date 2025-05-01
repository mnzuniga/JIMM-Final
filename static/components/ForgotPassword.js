import React, { useState } from 'react';
import axios from 'axios';  // Import axios for HTTP requests
// make the forget passwrd a security question instead 

const ForgotPassword = () => {
  const [emailOrPhone, setEmailOrPhone] = useState('');
  const [message, setMessage] = useState('');  // State to show the message after submission

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Send the email or phone number to the backend for recovery
      const response = await axios.post('/api/forgot-password', { email: emailOrPhone });

      // If successful, show the message returned by the backend
      setMessage(response.data.message);  
    } catch (error) {
      // If there's an error (e.g., user not found), show the error message
      setMessage('Error: ' + error.response.data.message || 'An unexpected error occurred');
    }
  };

  return (
    <div className="forgot-password-container">
      <h2>Forgot Password</h2>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          placeholder="Enter your email or phone number" 
          value={emailOrPhone} 
          onChange={(e) => setEmailOrPhone(e.target.value)} 
          required 
        />
        <button type="submit">Submit</button>
      </form>
      <p>{message}</p> {/* Display the response message from the backend */}
    </div>
  );
};

export default ForgotPassword;
