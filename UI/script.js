// DOM elements
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const welcomeScreen = document.getElementById('welcome-screen');
const chatContainer = document.getElementById('chat-container');
const chatMessages = document.getElementById('chat-messages');
const helpButton = document.getElementById('help-button');
const userName = document.getElementById('user-name');

// API configuration
const API_BASE_URL = 'http://localhost:8000';

// Day mapping for converting API response to display format
const DAY_ORDER = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7'];
const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

// Initialize chat
function init() {
    // Get or set user name
    const savedName = localStorage.getItem('loaf_userName') || 'User';
    userName.textContent = savedName;
    
    // Event listeners
    sendButton.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    helpButton.addEventListener('click', showHelp);
    
    // Focus input on load
    userInput.focus();
}

// Add message to chat
function addChatMessage(message, isUser = false, isHTML = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    
    if (isHTML) {
        messageDiv.innerHTML = message;
    } else {
        messageDiv.textContent = message;
    }
    
    chatMessages.appendChild(messageDiv);
    scrollChatToBottom();
    return messageDiv; // Return the element so it can be removed if needed
}

// Scroll chat to bottom
function scrollChatToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Convert API meal plan format to display format
function convertMealPlanFormat(mealPlan) {
    const converted = [];
    
    // Handle nested format (e.g., {"2025-11-20": {"day_1": {...}}})
    let actualPlan = mealPlan;
    if (typeof mealPlan === 'object' && mealPlan !== null) {
        // Check if it's nested with a date key
        const keys = Object.keys(mealPlan);
        if (keys.length > 0 && typeof mealPlan[keys[0]] === 'object' && mealPlan[keys[0]] !== null) {
            // Check if the nested object has day_1, day_2, etc.
            const nestedKeys = Object.keys(mealPlan[keys[0]]);
            if (nestedKeys.some(k => k.startsWith('day_'))) {
                actualPlan = mealPlan[keys[0]];
            }
        }
    }
    
    // Handle different possible formats from the API
    for (let i = 0; i < DAY_ORDER.length; i++) {
        const dayKey = DAY_ORDER[i];
        const dayName = DAY_NAMES[i];
        const altKey = `day_${i + 1}`;
        
        let dayData = null;
        
        // Try "Day 1", "Day 2", etc.
        if (actualPlan[dayKey]) {
            dayData = actualPlan[dayKey];
        }
        // Try "day_1", "day_2", etc.
        else if (actualPlan[altKey]) {
            dayData = actualPlan[altKey];
        }
        
        if (dayData) {
            converted.push({
                day: dayName,
                meal: dayData.recipe || dayData.meal || 'Meal',
                reason: dayData.reason || ''
            });
        } else {
            // If we can't find the day, add a placeholder
            converted.push({
                day: dayName,
                meal: 'Meal TBD',
                reason: ''
            });
        }
    }
    
    return converted;
}

// Render meal plan as chat message with transitions
async function renderMealPlanAsMessage(mealPlanData) {
    const savedName = localStorage.getItem('loaf_userName') || 'User';
    
    // Convert meal plan to display format
    const mealPlan = convertMealPlanFormat(mealPlanData);
    
    // Create the meal plan message container
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message bot meal-plan';
    
    // Add greeting and heading first
    messageDiv.innerHTML = `
        <div class="meal-plan-greeting">
            <p>Hi <span>${savedName}</span>! I've created a personalized meal plan for you. Let me take care of everything else.</p>
        </div>
        <h2 class="meal-plan-heading">Your Personalized Meal Plan</h2>
        <div class="meal-plan-content"></div>
        <div class="processing-card-container" style="display: none;">
            <div class="processing-card">
                <h2 class="processing-title">Processing Your Request</h2>
                <div class="tasks-list"></div>
                <div class="completion-message" id="completion-message" style="display: none;">
                    <div class="task-icon">
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2"
                                stroke-linecap="round" stroke-linejoin="round" />
                        </svg>
                    </div>
                    <span class="task-text">All set! Your meal plan is ready, groceries are ordered, and calendar events are created.</span>
                </div>
            </div>
        </div>
    `;
    
    // Add message to chat
    chatMessages.appendChild(messageDiv);
    scrollChatToBottom();
    
    // Get the meal plan content container
    const mealPlanContent = messageDiv.querySelector('.meal-plan-content');
    
    // Add days one by one with delay
    for (let i = 0; i < mealPlan.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay between each day
        
        const dayMealItem = document.createElement('div');
        dayMealItem.className = 'day-meal-item day-meal-item-enter';
        dayMealItem.innerHTML = `
            <span class="day-name">${mealPlan[i].day}</span>
            <span class="meal-separator">:</span>
            <span class="meal-name">${mealPlan[i].meal}</span>
        `;
        mealPlanContent.appendChild(dayMealItem);
        scrollChatToBottom();
    }
    
    // Wait a bit, then show processing card
    await new Promise(resolve => setTimeout(resolve, 500));
    const processingContainer = messageDiv.querySelector('.processing-card-container');
    processingContainer.style.display = 'block';
    scrollChatToBottom();
    
    // Get the tasks list container
    const tasksList = messageDiv.querySelector('.tasks-list');
    
    // Define tasks
    const tasks = [
        { text: "Adding groceries to cart" },
        { text: "Processing payment via Stripe" },
        { text: "Creating Google Calendar events" }
    ];
    
    // Add tasks one by one with delay
    for (let i = 0; i < tasks.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 400)); // 400ms delay between each task
        
        const taskItem = document.createElement('div');
        taskItem.className = 'task-item task-item-enter';
        taskItem.innerHTML = `
            <div class="task-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2"
                        stroke-linecap="round" stroke-linejoin="round" />
                </svg>
            </div>
            <span class="task-text">${tasks[i].text}</span>
        `;
        tasksList.appendChild(taskItem);
        scrollChatToBottom();
    }
    
    // Wait a bit, then show completion message
    await new Promise(resolve => setTimeout(resolve, 500));
    const completionMessage = messageDiv.querySelector('.completion-message');
    completionMessage.style.display = 'flex';
    scrollChatToBottom();
}

// Handle send button click
async function handleSend() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }
    
    // Extract name if user says "I'm [name]" or similar
    const nameMatch = message.match(/(?:i'?m|my name is|call me)\s+([A-Za-z]+)/i);
    if (nameMatch) {
        const newName = nameMatch[1];
        userName.textContent = newName;
        localStorage.setItem('loaf_userName', newName);
    }
    
    // Hide welcome screen and show chat
    welcomeScreen.style.display = 'none';
    chatContainer.style.display = 'flex';
    
    // Add user message to chat
    addChatMessage(message, true);
    
    // Clear input
    userInput.value = '';
    userInput.disabled = true;
    sendButton.disabled = true;
    
    // Show loading message
    await new Promise(resolve => setTimeout(resolve, 500));
    const loadingMessage = addChatMessage("Thinking...", false);
    
    try {
        // Call the API to get the meal plan
        console.log('Calling API:', `${API_BASE_URL}/chat`);
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                run_workflow: false  // Set to true if you want to run the full workflow
            })
        });
        
        // Remove loading message
        if (loadingMessage && loadingMessage.parentNode) {
            loadingMessage.parentNode.removeChild(loadingMessage);
        }
        
        if (!response.ok) {
            let errorMessage = `API error: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If we can't parse the error, use the status text
            }
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data.success && data.meal_plan) {
            // Show the chatbot's message if available, otherwise use a default
            const botMessage = data.message || "I've created a personalized meal plan for you!";
            addChatMessage(botMessage);
            
            // If there's a raw_response with additional text, show it
            if (data.raw_response && data.raw_response.trim()) {
                // Try to extract any text before/after the JSON
                const jsonMatch = data.raw_response.match(/\{.*\}/s);
                if (jsonMatch) {
                    const beforeJson = data.raw_response.substring(0, jsonMatch.index).trim();
                    const afterJson = data.raw_response.substring(jsonMatch.index + jsonMatch[0].length).trim();
                    
                    if (beforeJson) {
                        addChatMessage(beforeJson);
                    }
                    if (afterJson) {
                        addChatMessage(afterJson);
                    }
                } else {
                    // If no JSON found, show the raw response
                    addChatMessage(data.raw_response);
                }
            }
            
            // Wait a bit, then show meal plan in chat (with delay)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // Show meal plan as a chat message with transitions
            await renderMealPlanAsMessage(data.meal_plan);
        } else {
            throw new Error(data.message || 'Failed to get meal plan from API');
        }
    } catch (error) {
        console.error('Error calling API:', error);
        // Remove loading message if it still exists
        if (loadingMessage && loadingMessage.parentNode) {
            loadingMessage.parentNode.removeChild(loadingMessage);
        }
        
        // Provide helpful error messages
        let errorMsg = error.message;
        if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMsg = 'Cannot connect to the API server. Please make sure the API server is running on port 8000. Run: ./run_server.sh';
        }
        
        addChatMessage(`Sorry, I encountered an error: ${errorMsg}`);
    } finally {
        // Re-enable input
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}


// Show help dialog
function showHelp() {
    alert('Welcome to Loaf!\n\nI can help you create personalized meal plans for the week. Just tell me what you\'d like to eat, and I\'ll take care of the rest!');
}


// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
