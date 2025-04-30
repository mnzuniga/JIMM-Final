import React, { useState } from 'react';

const ForgotPassword = () => {
  const [emailOrPhone, setEmailOrPhone] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Logic for sending recovery info would go here
    console.log('Recovery request sent for:', emailOrPhone);
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
    </div>
  );
};

export default ForgotPassword;
