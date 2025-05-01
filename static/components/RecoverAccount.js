import React, { useState } from 'react';

function RecoverAccount() {
  const [email, setEmail] = useState('');

  const handleRecover = (e) => {
    e.preventDefault();
    console.log('Recovering account for:', email);
    // Implement account recovery logic
  };

  return (
    <div>
      <h1>Recover Account</h1>
      <form onSubmit={handleRecover}>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
        />
        <button type="submit">Recover Account</button>
      </form>
    </div>
  );
}

export default RecoverAccount;
