// ChatBox.js
import React from "react";

const ChatBox = ({ messages }) => {
  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.map((message, index) => (
        <div
          key={index}
          className={`mb-2 ${message.isUser ? "text-right" : "text-left"}`}
        >
          <span
            className={`inline-block px-2 py-1 rounded-lg ${
              message.isUser ? "bg-blue-500 text-white" : "bg-gray-200"
            }`}
          >
            {message.text}
          </span>
        </div>
      ))}
    </div>
  );
};

export default ChatBox;
