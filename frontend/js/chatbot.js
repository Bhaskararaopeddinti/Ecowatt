// EcoWatt AI - Chatbot JavaScript

import { chatbotAPI, authAPI } from './api.js';

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const clearChatBtn = document.getElementById('clearChatBtn');
const logoutBtn = document.getElementById('logoutBtn');
const quickQuestions = document.querySelectorAll('.quick-question');

// Format time
function formatTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Add message to chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
    
    // Convert newlines to line breaks
    const formattedContent = content.replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `
        <p>${formattedContent}</p>
        <div class="message-time">${formatTime(new Date())}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show/hide typing indicator
function showTyping(show) {
    if (show) {
        typingIndicator.classList.add('active');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } else {
        typingIndicator.classList.remove('active');
    }
}

// Send message
async function sendMessage(question) {
    if (!question || question.trim() === '') {
        return;
    }
    
    // Add user message
    addMessage(question, true);
    
    // Clear input
    chatInput.value = '';
    sendBtn.disabled = true;
    
    // Show typing indicator
    showTyping(true);
    
    try {
        const response = await chatbotAPI.ask(question);
        
        // Hide typing indicator
        showTyping(false);
        
        // Add bot response
        addMessage(response.answer, false);
        
    } catch (error) {
        console.error('Error sending message:', error);
        showTyping(false);
        addMessage('Sorry, I encountered an error. Please try again.', false);
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// Clear chat history
async function clearChatHistory() {
    if (!confirm('Are you sure you want to clear all chat history?')) {
        return;
    }
    
    try {
        await chatbotAPI.clearChatHistory();
        
        // Clear messages except the welcome message
        chatMessages.innerHTML = `
            <div class="message bot">
                <p>Hello! I'm your AI energy assistant. I can help you understand your electricity usage, identify energy-saving opportunities, and answer questions about your consumption patterns. What would you like to know?</p>
                <div class="message-time">Just now</div>
            </div>
        `;
        
        alert('Chat history cleared successfully!');
        
    } catch (error) {
        console.error('Error clearing chat history:', error);
        alert('Failed to clear chat history. Please try again.');
    }
}

// Handle Enter key in textarea
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(chatInput.value);
    }
});

// Send button click
sendBtn.addEventListener('click', () => {
    sendMessage(chatInput.value);
});

// Clear chat button
clearChatBtn.addEventListener('click', clearChatHistory);

// Quick questions
quickQuestions.forEach(question => {
    question.addEventListener('click', () => {
        const questionText = question.dataset.question;
        chatInput.value = questionText;
        sendMessage(questionText);
    });
});

// Logout
logoutBtn.addEventListener('click', authAPI.logout);

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Focus input on load
chatInput.focus();
