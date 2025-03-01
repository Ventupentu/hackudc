// src/pages/Chat.js
import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import ReactMarkdown from 'react-markdown';
import '../styles/Chat.css';

function Chat({ userCredentials }) {
  // Estados para mensajes, input, etc.
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typedResponse, setTypedResponse] = useState('');
  const [typingInProgress, setTypingInProgress] = useState(false);

  // Referencias para auto-scroll y auto-resize del textarea
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Parámetro de velocidad de tipeo (ms por carácter)
  const TYPING_SPEED = 20;

  // Cargar la conversación previa
  useEffect(() => {
    const fetchConversation = async () => {
      try {
        const response = await api.get('/start_chat', {
          params: { username: userCredentials.username }
        });
        if (response.data && response.data.conversation) {
          setMessages(response.data.conversation);
        }
      } catch (error) {
        console.error('Error al obtener el chat:', error);
      }
    };
    fetchConversation();
  }, [userCredentials.username]);

  // Auto-scroll al final del área de mensajes cuando se actualicen
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typedResponse]);

  // Auto-resize del textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  // Simulación de escritura progresiva (typing effect)
  const simulateTyping = (fullText) => {
    setTypedResponse('');
    setTypingInProgress(true);
    let index = 0;
    const interval = setInterval(() => {
      setTypedResponse((prev) => prev + fullText[index]);
      index++;
      if (index >= fullText.length) {
        clearInterval(interval);
        setMessages((prev) => [...prev, { role: 'assistant', content: fullText }]);
        setTypedResponse('');
        setIsTyping(false);
        setTypingInProgress(false);
      }
    }, TYPING_SPEED);
  };

  // Enviar mensaje del usuario
  const sendMessage = async () => {
    if (!input.trim()) return;
    const newMessages = [...messages, { role: 'user', content: input }];
    setMessages(newMessages);
    setInput('');
    setIsTyping(true);
    try {
      const payload = { messages: newMessages, username: userCredentials.username };
      const response = await api.post('/chat', payload);
      const fullResponse = response.data.respuesta;
      simulateTyping(fullResponse);
    } catch (error) {
      console.error('Error al enviar el mensaje:', error);
      setIsTyping(false);
      setTypingInProgress(false);
    }
  };

  // Manejar teclas: Enter envía; Shift+Enter inserta salto de línea
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-page">
      {/* Área de mensajes scrollable (solo los mensajes se desplazan) */}
      <div className="chat-messages-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              <div className="chat-bubble">
                <span className="chat-author">
                  {msg.role === 'user' ? 'Tú' : 'Chatbot'}:
                </span>
                {msg.role === 'assistant' ? (
                  <div className="chat-text">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  <span className="chat-text">{msg.content}</span>
                )}
              </div>
            </div>
          ))}

          {/* Mensaje en proceso de tipeo */}
          {isTyping && (
            <div className="chat-message assistant typing">
              <div className="chat-bubble">
                <span className="chat-author">Chatbot:</span>
                <div className="chat-text">
                  {typedResponse ? (
                    <>
                      <ReactMarkdown>{typedResponse}</ReactMarkdown>
                      {typingInProgress && (
                        <div className="typing-indicator after-text">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef}></div>
        </div>
      </div>

      {/* Área de entrada fija (no se desplaza al hacer scroll en mensajes) */}
      <div className="chat-input-wrapper">
        <div className="chat-input">
          <textarea
            ref={textareaRef}
            placeholder="Pregunta lo que quieras"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            wrap="soft"
          />
          <button className="send-button" onClick={sendMessage}>
            <span className="arrow-up">&#9650;</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default Chat;
