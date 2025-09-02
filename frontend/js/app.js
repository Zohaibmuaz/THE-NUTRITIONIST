// API Configuration
const API_BASE_URL = '/api';

// Global state
let currentUser = null;
let authToken = null;
let weeklyChart = null;
let macroChart = null;
let dailyCaloriesChart = null;
let goalProgressChart = null;
let selectedDate = new Date().toISOString().split('T')[0];
let chatHistory = [];

// DOM Elements
const authContainer = document.getElementById('auth-container');
const profileSetup = document.getElementById('profile-setup');
const dashboard = document.getElementById('dashboard');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const profileForm = document.getElementById('profile-form');
const mealForm = document.getElementById('meal-form');
const aiForm = document.getElementById('ai-form');
const logoutBtn = document.getElementById('logout-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const toastContainer = document.getElementById('toast-container');

// Navigation elements
const navButtons = {
    dashboard: document.getElementById('nav-dashboard'),
    meals: document.getElementById('nav-meals'),
    charts: document.getElementById('nav-charts'),
    nutritionist: document.getElementById('nav-nutritionist'),
    analysis: document.getElementById('nav-analysis')
};

const sections = {
    dashboard: document.getElementById('section-dashboard'),
    meals: document.getElementById('section-meals'),
    charts: document.getElementById('section-charts'),
    nutritionist: document.getElementById('section-nutritionist'),
    analysis: document.getElementById('section-analysis')
};

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    updateCurrentDate();
    initializeTheme();
    initializeMobileMenu();
});

function initializeApp() {
    // Check for stored auth token
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    const storedChatHistory = localStorage.getItem('chatHistory');
    
    if (storedToken && storedUser) {
        authToken = storedToken;
        currentUser = JSON.parse(storedUser);
        
        // Load chat history
        if (storedChatHistory) {
            chatHistory = JSON.parse(storedChatHistory);
            restoreChatHistory();
        }
        
        checkUserProfile();
    } else {
        showAuthContainer();
    }
}

function setupEventListeners() {
    // Auth tab switching
    document.getElementById('login-tab').addEventListener('click', () => switchAuthTab('login'));
    document.getElementById('register-tab').addEventListener('click', () => switchAuthTab('register'));
    
    // Form submissions
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    profileForm.addEventListener('submit', handleProfileSetup);
    mealForm.addEventListener('submit', handleMealLog);
    aiForm.addEventListener('submit', handleAIQuestion);
    
    // Logout
    logoutBtn.addEventListener('click', handleLogout);
    
    // Navigation buttons
    Object.keys(navButtons).forEach(section => {
        navButtons[section].addEventListener('click', () => switchSection(section));
    });
    
    // Analysis report button
    document.getElementById('generate-report-btn').addEventListener('click', generateAnalysisReport);
    
    // Download report button
    document.getElementById('download-report-btn').addEventListener('click', downloadComprehensiveReport);
    
    // Date picker
    const mealDateInput = document.getElementById('meal-date');
    if (mealDateInput) {
        mealDateInput.value = selectedDate;
        mealDateInput.addEventListener('change', handleDateChange);
    }
    
    // Chart controls
    const chartPeriodSelect = document.getElementById('chart-period');
    const refreshChartsBtn = document.getElementById('refresh-charts');
    if (chartPeriodSelect) {
        chartPeriodSelect.addEventListener('change', loadCharts);
    }
    if (refreshChartsBtn) {
        refreshChartsBtn.addEventListener('click', loadCharts);
    }
    
    // Clear chat button
    const clearChatBtn = document.getElementById('clear-chat-btn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChatHistory);
    }
}

function switchSection(sectionName) {
    // Remove active class from all buttons and sections
    Object.keys(navButtons).forEach(key => {
        navButtons[key].classList.remove('active');
        sections[key].classList.remove('active');
    });
    
    // Add active class to selected button and section
    navButtons[sectionName].classList.add('active');
    sections[sectionName].classList.add('active');
    
    // Load section-specific data
    if (sectionName === 'charts') {
        loadCharts();
    }
}

function switchAuthTab(tab) {
    const loginTab = document.getElementById('login-tab');
    const registerTab = document.getElementById('register-tab');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    
    if (tab === 'login') {
        loginTab.classList.add('text-blue-600', 'border-blue-600');
        loginTab.classList.remove('text-gray-500', 'border-transparent');
        registerTab.classList.add('text-gray-500', 'border-transparent');
        registerTab.classList.remove('text-blue-600', 'border-blue-600');
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        registerTab.classList.add('text-blue-600', 'border-blue-600');
        registerTab.classList.remove('text-gray-500', 'border-transparent');
        loginTab.classList.add('text-gray-500', 'border-transparent');
        loginTab.classList.remove('text-blue-600', 'border-blue-600');
        registerForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    showLoading();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = {
                id: data.id,
                email: data.email,
                full_name: data.full_name
            };
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showToast('Login successful!', 'success');
            checkUserProfile();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(e) {
    e.preventDefault();
    showLoading();
    
    const fullName = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                full_name: fullName,
                email, 
                password 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = {
                id: data.id,
                email: data.email,
                full_name: data.full_name
            };
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            showToast('Registration successful!', 'success');
            showProfileSetup();
        } else {
            showToast(data.detail || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleProfileSetup(e) {
    e.preventDefault();
    showLoading();
    
    const profileData = {
        age: parseInt(document.getElementById('profile-age').value),
        weight: parseFloat(document.getElementById('profile-weight').value),
        height: parseFloat(document.getElementById('profile-height').value),
        gender: document.getElementById('profile-gender').value,
        activity_level: document.getElementById('profile-activity').value,
        fitness_goal: document.getElementById('profile-goal').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(profileData)
        });
        
        if (response.ok) {
            showToast('Profile setup complete!', 'success');
            loadDashboard();
        } else {
            const data = await response.json();
            showToast(data.detail || 'Profile setup failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleMealLog(e) {
    e.preventDefault();
    showLoading();
    
    const description = document.getElementById('meal-description').value;
    const date = document.getElementById('meal-date').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/meals`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ description, date })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Meal logged successfully!', 'success');
            document.getElementById('meal-description').value = '';
            loadMealsForDate(date);
            loadDashboard();
        } else {
            showToast(data.detail || 'Failed to log meal', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleDateChange(e) {
    selectedDate = e.target.value;
    const dateDisplay = document.getElementById('selected-date-display');
    const selectedDateObj = new Date(selectedDate);
    const today = new Date();
    
    if (selectedDate === today.toISOString().split('T')[0]) {
        dateDisplay.textContent = 'Today';
    } else {
        dateDisplay.textContent = selectedDateObj.toLocaleDateString('en-US', { 
            weekday: 'long', 
            month: 'short', 
            day: 'numeric' 
        });
    }
    
    loadMealsForDate(selectedDate);
}

async function handleAIQuestion(e) {
    e.preventDefault();
    
    const question = document.getElementById('ai-question').value;
    
    // Add user message
    addAIMessage(question, 'user');
    document.getElementById('ai-question').value = '';
    
    // Save user message to history
    chatHistory.push({ sender: 'user', message: question, timestamp: new Date().toISOString() });
    saveChatHistory();
    
    // Show typing indicator
    const typingId = addAIMessage('Thinking...', 'ai', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/ask`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ question })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Remove typing indicator and add AI response
            removeAIMessage(typingId);
            addAIMessage(data.response, 'ai');
            
            // Save AI response to history
            chatHistory.push({ sender: 'ai', message: data.response, timestamp: new Date().toISOString() });
            saveChatHistory();
        } else {
            removeAIMessage(typingId);
            const errorMessage = 'Sorry, I encountered an error. Please try again.';
            addAIMessage(errorMessage, 'ai');
            
            // Save error message to history
            chatHistory.push({ sender: 'ai', message: errorMessage, timestamp: new Date().toISOString() });
            saveChatHistory();
        }
    } catch (error) {
        removeAIMessage(typingId);
        const errorMessage = 'Network error. Please try again.';
        addAIMessage(errorMessage, 'ai');
        
        // Save error message to history
        chatHistory.push({ sender: 'ai', message: errorMessage, timestamp: new Date().toISOString() });
        saveChatHistory();
    }
}

async function generateAnalysisReport() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/ai/analyze-meals`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Render markdown
            const htmlContent = marked.parse(data.response);
            document.getElementById('analysis-report').innerHTML = `
                <div class="glass-card rounded-2xl p-6">
                    <h4 class="text-2xl font-bold gradient-text mb-6">Your Personalized Nutrition Report</h4>
                    <div class="prose max-w-none text-gray-300 prose-headings:text-white prose-a:text-blue-400 prose-strong:text-white prose-code:text-green-400 prose-code:bg-gray-800 prose-code:px-2 prose-code:py-1 prose-code:rounded">${htmlContent}</div>
                </div>
            `;
            showToast('Analysis report generated successfully!', 'success');
        } else {
            showToast(data.detail || 'Failed to generate report', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function downloadComprehensiveReport() {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/reports/download`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const htmlContent = await response.text();
            
            // Create blob and download
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `nutrition-report-${new Date().toISOString().split('T')[0]}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showToast('Report downloaded successfully!', 'success');
        } else {
            const data = await response.json();
            showToast(data.detail || 'Failed to download report', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('chatHistory');
    authToken = null;
    currentUser = null;
    chatHistory = [];
    showAuthContainer();
    showToast('Logged out successfully', 'success');
}

function saveChatHistory() {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

function restoreChatHistory() {
    const aiChat = document.getElementById('ai-chat');
    if (!aiChat) return;
    
    // Clear existing messages
    aiChat.innerHTML = '';
    
    if (chatHistory.length === 0) {
        // Show welcome message if no history
        aiChat.innerHTML = `
            <div class="text-center text-gray-500">
                <i class="fas fa-comments text-2xl mb-2"></i>
                <p>Ask me anything about nutrition!</p>
            </div>
        `;
        return;
    }
    
    // Restore all messages
    chatHistory.forEach(chat => {
        addAIMessage(chat.message, chat.sender);
    });
}

function clearChatHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatHistory = [];
        saveChatHistory();
        restoreChatHistory();
        showToast('Chat history cleared', 'success');
    }
}

async function deleteMeal(mealId) {
    if (!confirm('Are you sure you want to delete this meal?')) {
        return;
    }
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logs/meals/${mealId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showToast('Meal deleted successfully!', 'success');
            loadDashboard();
        } else {
            const data = await response.json();
            showToast(data.detail || 'Failed to delete meal', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function checkUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/profile`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            loadDashboard();
        } else if (response.status === 404) {
            showProfileSetup();
        } else {
            showToast('Authentication error', 'error');
            handleLogout();
        }
    } catch (error) {
        showToast('Network error', 'error');
        handleLogout();
    }
}

async function loadDashboard() {
    showLoading();
    
    try {
        // Load dashboard data
        const dashboardResponse = await fetch(`${API_BASE_URL}/dashboard`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!dashboardResponse.ok) {
            throw new Error('Failed to load dashboard data');
        }
        
        const dashboardData = await dashboardResponse.json();
        
        // Load today's meals
        const today = new Date().toISOString().split('T')[0];
        const mealsResponse = await fetch(`${API_BASE_URL}/logs/${today}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!mealsResponse.ok) {
            throw new Error('Failed to load meals data');
        }
        
        const mealsData = await mealsResponse.json();
        
        // Update UI
        updateDashboard(dashboardData, mealsData);
        showDashboard();
        
    } catch (error) {
        showToast('Failed to load dashboard', 'error');
    } finally {
        hideLoading();
    }
}

function updateDashboard(dashboardData, mealsData) {
    // Update welcome message
    document.getElementById('welcome-message').textContent = 
        `Hello ${currentUser.full_name}! Track your meals and stay on top of your goals.`;
    
    // Update goals
    document.getElementById('calories-goal').textContent = Math.round(dashboardData.goals.calories);
    document.getElementById('protein-goal').textContent = Math.round(dashboardData.goals.protein) + 'g';
    document.getElementById('carbs-goal').textContent = Math.round(dashboardData.goals.carbs) + 'g';
    document.getElementById('fats-goal').textContent = Math.round(dashboardData.goals.fats) + 'g';
    
    // Update consumed amounts
    document.getElementById('calories-consumed').textContent = Math.round(dashboardData.today.total_calories);
    document.getElementById('protein-consumed').textContent = Math.round(dashboardData.today.total_protein) + 'g';
    document.getElementById('carbs-consumed').textContent = Math.round(dashboardData.today.total_carbohydrates) + 'g';
    document.getElementById('fats-consumed').textContent = Math.round(dashboardData.today.total_fats) + 'g';
    
    // Update progress bars
    updateProgressBar('calories-progress', dashboardData.today.total_calories, dashboardData.goals.calories);
    updateProgressBar('protein-progress', dashboardData.today.total_protein, dashboardData.goals.protein);
    updateProgressBar('carbs-progress', dashboardData.today.total_carbohydrates, dashboardData.goals.carbs);
    updateProgressBar('fats-progress', dashboardData.today.total_fats, dashboardData.goals.fats);
    
    // Update meals list
    updateMealsList(mealsData.meals);
    updateMealsSummary(mealsData.meals);
    
    // Update weekly chart
    updateWeeklyChart(dashboardData.weekly_trends);
}

function updateProgressBar(elementId, current, goal) {
    const progressBar = document.getElementById(elementId);
    const percentage = Math.min((current / goal) * 100, 100);
    progressBar.style.width = percentage + '%';
    
    // Change color based on progress
    if (percentage > 100) {
        progressBar.className = 'bg-gradient-to-r from-red-500 to-pink-500 h-3 rounded-full progress-bar';
    } else if (percentage > 80) {
        progressBar.className = 'bg-gradient-to-r from-yellow-500 to-orange-500 h-3 rounded-full progress-bar';
    } else {
        progressBar.className = 'bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full progress-bar';
    }
}

function updateMealsList(meals) {
    const mealsList = document.getElementById('meals-list');
    
    if (meals.length === 0) {
        mealsList.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-utensils text-3xl mb-2"></i>
                <p>No meals logged today</p>
                <p class="text-sm">Start by logging your first meal above!</p>
            </div>
        `;
        return;
    }
    
    mealsList.innerHTML = meals.map(meal => `
        <div class="glass-card rounded-xl p-4 border border-gray-600 hover:border-gray-500 transition-all duration-300">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h5 class="font-medium text-white text-lg">${meal.name}</h5>
                    <p class="text-sm text-gray-300 mt-2">
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-red-500 to-pink-500 text-white mr-2">
                            ${Math.round(meal.calories)} cal
                        </span>
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-blue-500 to-cyan-500 text-white mr-2">
                            ${Math.round(meal.protein)}g protein
                        </span>
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-green-500 to-emerald-500 text-white mr-2">
                            ${Math.round(meal.carbohydrates)}g carbs
                        </span>
                        <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-yellow-500 to-orange-500 text-white">
                            ${Math.round(meal.fats)}g fat
                        </span>
                    </p>
                </div>
                <div class="flex items-center space-x-3">
                    <div class="text-right text-sm text-gray-400">
                        ${new Date(meal.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </div>
                    <button onclick="deleteMeal(${meal.id})" 
                            class="text-red-400 hover:text-red-300 transition-colors p-2 rounded-lg hover:bg-red-500 hover:bg-opacity-20"
                            title="Delete meal">
                        <i class="fas fa-trash text-sm"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function updateMealsSummary(meals) {
    const mealsSummary = document.getElementById('meals-summary');
    
    if (meals.length === 0) {
        mealsSummary.innerHTML = `
            <div class="text-center text-gray-500 py-4">
                <i class="fas fa-utensils text-2xl mb-2"></i>
                <p>No meals logged today</p>
            </div>
        `;
        return;
    }
    
    mealsSummary.innerHTML = meals.map(meal => `
        <div class="flex justify-between items-center py-3 border-b border-gray-600 hover:border-gray-500 transition-colors">
            <div class="flex-1">
                <span class="font-medium text-white text-lg">${meal.name}</span>
                <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-red-500 to-pink-500 text-white ml-3">${Math.round(meal.calories)} cal</span>
            </div>
            <span class="text-sm text-gray-400">
                ${new Date(meal.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
            </span>
        </div>
    `).join('');
}

async function loadMealsForDate(date) {
    try {
        const response = await fetch(`${API_BASE_URL}/logs/${date}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateMealsList(data.meals);
        }
    } catch (error) {
        console.error('Error loading meals for date:', error);
    }
}

async function loadCharts() {
    const period = document.getElementById('chart-period').value;
    
    try {
        // Load historical data for charts
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(endDate.getDate() - parseInt(period));
        
        const response = await fetch(`${API_BASE_URL}/dashboard?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateAllCharts(data);
        }
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

function updateWeeklyChart(weeklyData) {
    const ctx = document.getElementById('weekly-chart').getContext('2d');
    
    if (weeklyChart) {
        weeklyChart.destroy();
    }
    
    const labels = weeklyData.map(day => {
        const date = new Date(day.date);
        return date.toLocaleDateString('en-US', { weekday: 'short' });
    });
    
    weeklyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Calories',
                data: weeklyData.map(day => day.calories),
                borderColor: '#00f5ff',
                backgroundColor: 'rgba(0, 245, 255, 0.1)',
                tension: 0.4,
                fill: true,
                borderWidth: 3,
                pointBackgroundColor: '#00f5ff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10
                }
            }
        }
    });
}

function updateAllCharts(data) {
    updateWeeklyChart(data.weekly_trends || []);
    updateDailyCaloriesChart(data.daily_data || []);
    updateMacroChart(data.macro_data || {});
    updateGoalProgressChart(data.goal_progress || {});
}

function updateDailyCaloriesChart(dailyData) {
    const ctx = document.getElementById('daily-calories-chart').getContext('2d');
    
    if (dailyCaloriesChart) {
        dailyCaloriesChart.destroy();
    }
    
    const labels = dailyData.map(day => {
        const date = new Date(day.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    dailyCaloriesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Calories',
                data: dailyData.map(day => day.calories),
                backgroundColor: 'rgba(0, 245, 255, 0.8)',
                borderColor: '#00f5ff',
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff'
                    }
                }
            }
        }
    });
}

function updateGoalProgressChart(goalData) {
    const ctx = document.getElementById('goal-progress-chart').getContext('2d');
    
    if (goalProgressChart) {
        goalProgressChart.destroy();
    }
    
    goalProgressChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Achieved', 'Remaining'],
            datasets: [{
                data: [goalData.achieved || 0, goalData.remaining || 100],
                backgroundColor: ['rgba(0, 245, 255, 0.8)', 'rgba(255, 255, 255, 0.1)'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 1,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            }
        }
    });
}

function addAIMessage(message, sender, isTyping = false) {
    const aiChat = document.getElementById('ai-chat');
    const messageId = 'msg-' + Date.now();
    
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `mb-4 ${sender === 'user' ? 'flex justify-end' : 'flex justify-start'}`;
    
    const bubbleClass = sender === 'user' 
        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-4 rounded-2xl max-w-4xl shadow-lg'
        : 'glass-card border border-gray-600 px-6 py-4 rounded-2xl max-w-4xl shadow-lg';
    
    const messageContent = isTyping ? '<i class="fas fa-circle animate-pulse text-cyan-400"></i>' : marked.parse(message);
    const contentClass = sender === 'user' ? 'text-base leading-relaxed text-white' : 'text-base leading-relaxed ai-chat-content';
    messageDiv.innerHTML = `
        <div class="${bubbleClass}">
            <div class="${contentClass}">
                ${messageContent}
            </div>
        </div>
    `;
    
    aiChat.appendChild(messageDiv);
    aiChat.scrollTop = aiChat.scrollHeight;
    
    return messageId;
}

function removeAIMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

function updateCurrentDate() {
    const today = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    document.getElementById('current-date').textContent = today.toLocaleDateString('en-US', options);
}

// UI State Management
function showAuthContainer() {
    authContainer.classList.remove('hidden');
    profileSetup.classList.add('hidden');
    dashboard.classList.add('hidden');
    logoutBtn.classList.add('hidden');
}

function showProfileSetup() {
    authContainer.classList.add('hidden');
    profileSetup.classList.remove('hidden');
    dashboard.classList.add('hidden');
    logoutBtn.classList.remove('hidden');
}

function showDashboard() {
    authContainer.classList.add('hidden');
    profileSetup.classList.add('hidden');
    dashboard.classList.remove('hidden');
    logoutBtn.classList.remove('hidden');
}

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const bgColor = type === 'success' ? 'bg-gradient-to-r from-green-500 to-teal-500' : 
                   type === 'error' ? 'bg-gradient-to-r from-red-500 to-pink-500' : 'bg-gradient-to-r from-blue-500 to-purple-500';
    
    toast.className = `${bgColor} text-white px-6 py-3 rounded-xl shadow-lg transform transition-all duration-300 translate-x-full glass`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 4000);
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
    
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle visual state
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        if (theme === 'dark') {
            themeToggle.classList.add('dark');
        } else {
            themeToggle.classList.remove('dark');
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
    
    // Add smooth transition effect
    document.body.style.transition = 'all 0.3s ease';
    setTimeout(() => {
        document.body.style.transition = '';
    }, 300);
}

// Mobile Menu Management
function initializeMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (mobileMenuBtn && sidebar && sidebarOverlay) {
        mobileMenuBtn.addEventListener('click', toggleMobileMenu);
        sidebarOverlay.addEventListener('click', closeMobileMenu);
        
        // Close menu when clicking on nav items
        const navItems = sidebar.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', closeMobileMenu);
        });
    }
}

function toggleMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && sidebarOverlay) {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('hidden');
    }
}

function closeMobileMenu() {
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    
    if (sidebar && sidebarOverlay) {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.add('hidden');
    }
}

// Enhanced UI Updates
function updateUserInfo() {
    const userName = document.getElementById('user-name');
    if (userName && currentUser) {
        userName.textContent = currentUser.full_name || 'Welcome';
    }
}

// Override existing functions to include new UI updates
const originalLoadDashboard = loadDashboard;
loadDashboard = function() {
    originalLoadDashboard();
    updateUserInfo();
};

const originalHandleLogin = handleLogin;
handleLogin = function(e) {
    originalHandleLogin(e);
    updateUserInfo();
};

const originalHandleRegister = handleRegister;
handleRegister = function(e) {
    originalHandleRegister(e);
    updateUserInfo();

};
