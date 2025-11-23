// DOM elements
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const welcomeScreen = document.getElementById('welcome-screen');
const chatContainer = document.getElementById('chat-container');
const chatMessages = document.getElementById('chat-messages');
const helpButton = document.getElementById('help-button');
const userName = document.getElementById('user-name');

// Hardcoded meal plan data (1 meal per day)
const hardcodedMealPlan = [
    {
        day: "Monday",
        meal: "Avocado Toast with Poached Eggs"
    },
    {
        day: "Tuesday",
        meal: "Greek Yogurt Parfait"
    },
    {
        day: "Wednesday",
        meal: "Overnight Oats"
    },
    {
        day: "Thursday",
        meal: "Scrambled Eggs with Spinach"
    },
    {
        day: "Friday",
        meal: "Smoothie Bowl"
    },
    {
        day: "Saturday",
        meal: "Pancakes with Maple Syrup"
    },
    {
        day: "Sunday",
        meal: "French Toast"
    }
];

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
}

// Scroll chat to bottom
function scrollChatToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render meal plan as chat message with transitions
async function renderMealPlanAsMessage() {
    const savedName = localStorage.getItem('loaf_userName') || 'User';
    
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
    for (let i = 0; i < hardcodedMealPlan.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 300)); // 300ms delay between each day
        
        const dayMealItem = document.createElement('div');
        dayMealItem.className = 'day-meal-item day-meal-item-enter';
        dayMealItem.innerHTML = `
            <span class="day-name">${hardcodedMealPlan[i].day}</span>
            <span class="meal-separator">:</span>
            <span class="meal-name">${hardcodedMealPlan[i].meal}</span>
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
    
    // Wait a moment, then show bot response
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Add bot response message
    addChatMessage("I'll create a personalized meal plan for you!");
    
    // Wait a bit more, then show meal plan in chat (with delay)
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Show meal plan as a chat message with transitions
    await renderMealPlanAsMessage();
    
    // Re-enable input
    userInput.disabled = false;
    sendButton.disabled = false;
    userInput.focus();
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
