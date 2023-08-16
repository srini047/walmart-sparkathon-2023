import React, { useState } from 'react';
import "./App.css";
import ChatBox from './components/ChatBox';
import Form from './components/Form';

const App = () => {
  const [messages, setMessages] = useState([]);

  const handleNewMessage = (message) => {
    const newMessage = { text: message, isUser: true };
    setMessages([...messages, newMessage]);
  
    // Simulate a bot response after a delay
    setTimeout(() => {
      const botResponse = { text: 'Hi from the bot!', isUser: false };
      setMessages([...messages, newMessage, botResponse]);
  
      // Log the bot's response to the console
      console.log('Bot:', botResponse.text);
    }, 1000); // Delay in milliseconds before the bot responds
  };

  return (
    <div className="flex flex-col h-screen">
      <ChatBox messages={messages} />
      <Form onNewMessage={handleNewMessage} />
    </div>
  );
};

export default App;
