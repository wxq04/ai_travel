/**
 * AI Travel Planner - AI Chat JavaScript
 * 
 * Implements:
 * - SSE receiving streaming AI output with typewriter effect
 * - Multi-turn conversation history maintenance
 * - "Apply changes" button to apply AI suggestions to editor
 */

// Conversation history
let conversationHistory = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initChatInput();
});

// Initialize chat input
function initChatInput() {
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        // Send message on Enter key
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }
}

// Send chat message to AI
function sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add user message to UI
    addMessageToChat('user', message);
    
    // Add to conversation history
    conversationHistory.push({
        role: 'user',
        content: message
    });
    
    // Send to server and get streaming response
    sendToAI(message);
}

// Add message to chat UI
function addMessageToChat(role, content, withApplyButton = false) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    if (role === 'bot') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Typewriter effect for bot message
        typewriterEffect(messageDiv.querySelector('.message-content'), content, () => {
            // Add apply button if needed
            if (withApplyButton) {
                const applyBtn = document.createElement('button');
                applyBtn.className = 'btn btn-success btn-sm mt-2';
                applyBtn.innerHTML = '<i class="fas fa-check me-1"></i>应用修改';
                applyBtn.onclick = () => applyChangesToEditor(content);
                messageDiv.querySelector('.message-content').appendChild(applyBtn);
            }
        });
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">${escapeHtml(content)}</div>
        `;
        chatMessages.insertBefore(messageDiv, chatMessages.lastElementChild);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Typewriter effect for streaming output
function typewriterEffect(element, text, callback) {
    // Remove typing indicator
    const typingIndicator = element.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
    
    let index = 0;
    const cursor = document.createElement('span');
    cursor.className = 'typewriter-cursor';
    cursor.textContent = '|';
    
    element.innerHTML = '';
    element.appendChild(cursor);
    
    function type() {
        if (index < text.length) {
            cursor.insertAdjacentText('beforebegin', text.charAt(index));
            index++;
            setTimeout(type, 30); // Adjust speed here
        } else {
            cursor.remove();
            if (callback) callback();
        }
    }
    
    type();
}

// Send message to AI via SSE
function sendToAI(message) {
    // Get current itinerary data
    const itineraryData = window.serializeFormData ? window.serializeFormData() : null;
    
    // Create SSE connection
    const eventSource = new EventSource(`/ai/chat?message=${encodeURIComponent(message)}&history=${encodeURIComponent(JSON.stringify(conversationHistory))}`);
    
    // Create placeholder for bot response
    const chatMessages = document.getElementById('chatMessages');
    const botMessageDiv = document.createElement('div');
    botMessageDiv.className = 'message bot-message';
    botMessageDiv.innerHTML = '<div class="message-content"></div>';
    chatMessages.appendChild(botMessageDiv);
    
    const contentDiv = botMessageDiv.querySelector('.message-content');
    let fullResponse = '';
    
    // Handle incoming messages
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'content') {
            fullResponse += data.content;
            // Update content with cursor
            const cursor = contentDiv.querySelector('.typewriter-cursor') || document.createElement('span');
            if (!contentDiv.contains(cursor)) {
                cursor.className = 'typewriter-cursor';
                cursor.textContent = '|';
                contentDiv.appendChild(cursor);
            }
            cursor.insertAdjacentText('beforebegin', data.content);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else if (data.type === 'done') {
            eventSource.close();
            
            // Remove cursor
            const cursor = contentDiv.querySelector('.typewriter-cursor');
            if (cursor) cursor.remove();
            
            // Add to conversation history
            conversationHistory.push({
                role: 'assistant',
                content: fullResponse
            });
            
            // Check if AI suggests changes
            if (fullResponse.includes('建议') || fullResponse.includes('修改') || fullResponse.includes('调整')) {
                const applyBtn = document.createElement('button');
                applyBtn.className = 'btn btn-success btn-sm mt-2';
                applyBtn.innerHTML = '<i class="fas fa-check me-1"></i>应用修改';
                applyBtn.onclick = () => applyChangesToEditor(fullResponse);
                contentDiv.appendChild(applyBtn);
            }
        } else if (data.type === 'error') {
            eventSource.close();
            contentDiv.innerHTML = `<div class="text-danger">错误: ${data.message}</div>`;
        }
    };
    
    eventSource.onerror = function() {
        eventSource.close();
        contentDiv.innerHTML = '<div class="text-danger">连接失败，请重试</div>';
    };
}

// Apply AI-suggested changes to editor DOM
function applyChangesToEditor(aiResponse) {
    try {
        // Try to parse AI response for suggested changes
        // This is a simplified implementation
        const changes = parseAIResponse(aiResponse);
        
        if (changes && changes.length > 0) {
            // Apply each suggested change
            changes.forEach(change => {
                if (change.type === 'add_activity') {
                    // Add new activity to specific day
                    const dayIndex = change.day - 1;
                    if (window.addActivity) {
                        window.addActivity(dayIndex);
                        
                        // Fill in the new activity details
                        setTimeout(() => {
                            const dayPanel = document.querySelectorAll('.accordion-item')[dayIndex];
                            if (dayPanel) {
                                const lastActivity = dayPanel.querySelectorAll('.activity-card').length - 1;
                                const activityCard = dayPanel.querySelectorAll('.activity-card')[lastActivity];
                                if (activityCard) {
                                    if (change.name) activityCard.querySelector('.activity-name').value = change.name;
                                    if (change.type) activityCard.querySelector('.activity-type').value = change.type;
                                    if (change.duration) activityCard.querySelector('.activity-duration').value = change.duration;
                                    if (change.cost) activityCard.querySelector('.activity-cost').value = change.cost;
                                    if (change.tips) activityCard.querySelector('.activity-tips').value = change.tips;
                                }
                            }
                        }, 100);
                    }
                } else if (change.type === 'modify_activity') {
                    // Modify existing activity
                    const dayPanel = document.querySelectorAll('.accordion-item')[change.day - 1];
                    if (dayPanel) {
                        const activityCard = dayPanel.querySelectorAll('.activity-card')[change.activity - 1];
                        if (activityCard && change.field) {
                            const fieldMap = {
                                'name': '.activity-name',
                                'type': '.activity-type',
                                'duration': '.activity-duration',
                                'cost': '.activity-cost',
                                'tips': '.activity-tips'
                            };
                            const field = activityCard.querySelector(fieldMap[change.field]);
                            if (field) field.value = change.value;
                        }
                    }
                } else if (change.type === 'set_theme') {
                    // Set day theme
                    const dayPanel = document.querySelectorAll('.accordion-item')[change.day - 1];
                    if (dayPanel) {
                        const themeInput = dayPanel.querySelector('.day-theme');
                        if (themeInput) themeInput.value = change.theme;
                    }
                }
            });
            
            // Update cost display
            if (window.updateCostDisplay) {
                window.updateCostDisplay();
            }
            
            // Show success message
            alert('已成功应用 AI 修改建议！');
            
            // Close chat sidebar
            if (window.toggleAIChat) {
                window.toggleAIChat();
            }
        } else {
            alert('未能识别修改建议，请手动调整');
        }
    } catch (error) {
        console.error('Error applying changes:', error);
        alert('应用修改时出错：' + error.message);
    }
}

// Parse AI response to extract suggested changes
function parseAIResponse(response) {
    // This is a simplified parser - in production, you'd want more robust parsing
    const changes = [];
    
    // Try to find JSON-like structures in the response
    const jsonMatch = response.match(/```json\n([\s\S]*?)\n```/);
    if (jsonMatch) {
        try {
            const parsed = JSON.parse(jsonMatch[1]);
            if (Array.isArray(parsed.changes)) {
                return parsed.changes;
            }
        } catch (e) {
            // JSON parsing failed, continue with pattern matching
        }
    }
    
    // Pattern matching for common change patterns
    // e.g., "我建议在第2天添加一个景点：故宫"
    const addActivityPattern = /在第(\d+)天添加[一个]?(.+?)[：:](.+?)(?:\n|$)/g;
    let match;
    while ((match = addActivityPattern.exec(response)) !== null) {
        changes.push({
            type: 'add_activity',
            day: parseInt(match[1]),
            name: match[3]
        });
    }
    
    // e.g., "第3天的主题可以设为：历史文化探索"
    const themePattern = /第(\d+)天的主题可以设为[：:](.+?)(?:\n|$)/g;
    while ((match = themePattern.exec(response)) !== null) {
        changes.push({
            type: 'set_theme',
            day: parseInt(match[1]),
            theme: match[2]
        });
    }
    
    return changes;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Clear conversation history
function clearConversation() {
    conversationHistory = [];
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    对话已清空。请告诉我您想要如何调整行程？
                </div>
            </div>
        `;
    }
}

// Make functions globally available
window.sendChatMessage = sendChatMessage;
window.applyChangesToEditor = applyChangesToEditor;
window.clearConversation = clearConversation;
