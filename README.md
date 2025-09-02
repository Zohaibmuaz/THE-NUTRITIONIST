# THE Nutritionist™ 🍃

> **AI-Powered Nutrition Tracking & Health Management System**  
> *Developed by Zohaib Muaz*

![THE Nutritionist](https://img.shields.io/badge/THE%20Nutritionist-AI%20Powered-00f5ff?style=for-the-badge&logo=leaf)
![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

## 🌟 Overview

**THE Nutritionist™** is a cutting-edge, AI-powered nutrition tracking application that combines advanced artificial intelligence with a stunning futuristic user interface. This comprehensive health management system helps users track their meals, monitor nutrition goals, and receive personalized dietary recommendations through an intelligent AI nutritionist.

### ✨ Key Highlights
- 🤖 **AI-Powered Meal Analysis** - Instantly analyze nutrition from natural language meal descriptions
- 🎨 **Futuristic UI/UX** - Glassmorphism design with smooth animations and neon accents
- 🌙 **Dark/Light Theme** - Seamless theme switching with beautiful transitions
- 📊 **Advanced Analytics** - Comprehensive charts and progress tracking
- 💬 **AI Nutritionist Chat** - Interactive AI assistant for personalized nutrition advice
- 📱 **Fully Responsive** - Perfect experience across all devices
- 📈 **Comprehensive Reports** - Detailed nutrition analysis and recommendations

---

## 🚀 Features

### 🍽️ **Smart Meal Logging**
- Natural language meal input (e.g., "scrambled eggs with spinach")
- Automatic nutrition calculation using AI
- Real-time progress tracking with animated progress bars
- Historical meal logging with date selection

### 🤖 **AI Nutritionist Assistant**
- Interactive chat interface with markdown support
- Personalized nutrition advice and recommendations
- Expert guidance on diet planning and health goals
- Beautiful glass-style chat bubbles with smooth animations

### 📊 **Advanced Analytics**
- **Real-time Dashboard** - Live nutrition stats with gradient progress bars
- **Interactive Charts** - Neon-colored charts showing calorie trends, macro distribution
- **Weekly/Monthly Trends** - Comprehensive data visualization
- **Goal Progress Tracking** - Visual progress indicators

### 🎨 **Futuristic Design**
- **Glassmorphism Effects** - Modern glass-style cards and components
- **Neon Color Scheme** - Cyan, purple, and gradient accents throughout
- **Smooth Animations** - Hover effects, transitions, and micro-interactions
- **Animated Background** - Dynamic floating gradient orbs
- **Custom UI Elements** - Styled progress bars, buttons, and form inputs

### 📱 **User Experience**
- **Responsive Design** - Mobile-first approach with collapsible sidebar
- **Theme Toggle** - Smooth dark/light mode switching
- **Toast Notifications** - Beautiful gradient notifications with icons
- **Loading Animations** - Custom spinners and loading states
- **Profile Management** - Comprehensive user profile setup

---

## 🛠️ Technology Stack

### **Backend**
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.8+** - Core programming language
- **SQLAlchemy** - Database ORM for data management
- **SQLite** - Lightweight database for data storage
- **Pydantic** - Data validation and settings management
- **AI Integration** - Custom nutrition analysis algorithms

### **Frontend**
- **HTML5** - Modern semantic markup
- **CSS3** - Advanced styling with custom properties and animations
- **JavaScript (ES6+)** - Modern JavaScript with async/await
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Beautiful, responsive charts
- **Font Awesome** - Professional icon library
- **Google Fonts (Inter)** - Modern typography

### **Design & Animation**
- **Glassmorphism** - Modern glass-style design pattern
- **CSS Animations** - Smooth transitions and hover effects
- **Gradient Backgrounds** - Dynamic color schemes
- **Responsive Design** - Mobile-first approach
- **Custom Scrollbars** - Styled scroll elements

---

## 📋 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser

### **1. Clone the Repository**
```bash
git clone https://github.com/zohaibmuaz/the-nutritionist.git
cd the-nutritionist
```

### **2. Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Start the Backend Server**
```bash
# Run the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **4. Start the Frontend Server**
```bash
# Open new terminal and navigate to frontend
cd frontend

# Start HTTP server
python -m http.server 3000
```

### **5. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🎮 Usage Guide

### **Getting Started**
1. **Register Account** - Create your profile with personal information
2. **Complete Profile** - Set your age, weight, height, activity level, and fitness goals
3. **Start Logging Meals** - Simply describe what you ate in natural language
4. **Track Progress** - Monitor your nutrition goals with beautiful visual indicators
5. **Chat with AI** - Ask the AI nutritionist for personalized advice
6. **View Analytics** - Analyze your eating patterns with comprehensive charts

### **Demo Flow**
```
1. Register → 2. Profile Setup → 3. Log Meals → 4. View Dashboard → 5. AI Chat → 6. Analytics
```

---

## 📁 Project Structure

```
the-nutritionist/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── auth.py              # Authentication logic
│   ├── services.py          # Business logic services
│   ├── requirements.txt     # Python dependencies
│   └── calorie_tracker.db   # SQLite database
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── js/
│   │   └── app.js          # JavaScript application logic
│   └── css/                 # Additional styles (if needed)
├── README.md               # Project documentation
└── requirements.txt        # Global requirements
```

---

## 🎨 Design Philosophy

### **Glassmorphism & Futuristic Aesthetics**
- **Glass Effects**: Translucent cards with backdrop blur for modern appeal
- **Neon Accents**: Cyan and purple color scheme inspired by cyberpunk aesthetics
- **Smooth Animations**: 60fps animations with cubic-bezier timing functions
- **Gradient Elements**: Dynamic gradients throughout the interface

### **User Experience Principles**
- **Intuitive Navigation**: Clear sidebar navigation with visual feedback
- **Responsive Design**: Mobile-first approach ensuring great experience on all devices
- **Accessibility**: High contrast ratios and clear typography
- **Performance**: Optimized animations and efficient rendering

---

## 🔮 Future Enhancements

### **Planned Features**
- [ ] **Food Photo Recognition** - AI-powered image analysis for meal logging
- [ ] **Social Features** - Share progress and compete with friends
- [ ] **Wearable Integration** - Connect with fitness trackers and smartwatches
- [ ] **Meal Planning** - AI-generated meal plans based on goals and preferences
- [ ] **Barcode Scanner** - Quick food item entry via barcode scanning
- [ ] **Export Data** - PDF reports and data export functionality
- [ ] **Push Notifications** - Meal reminders and goal notifications
- [ ] **Multi-language Support** - Internationalization for global users

### **Technical Improvements**
- [ ] **Database Migration** - Move to PostgreSQL for production
- [ ] **Caching Layer** - Redis integration for improved performance
- [ ] **API Rate Limiting** - Enhanced security and performance
- [ ] **WebSocket Integration** - Real-time updates and notifications
- [ ] **Progressive Web App** - Offline functionality and app-like experience

---

## 🤝 Contributing

We welcome contributions to THE Nutritionist™! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### **Development Guidelines**
- Follow existing code style and patterns
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Zohaib Muaz**
- 🌐 Portfolio: [Your Portfolio URL]
- 💼 LinkedIn: [Your LinkedIn Profile]
- 📧 Email: [Your Email]
- 🐙 GitHub: [Your GitHub Profile]

---

## 🙏 Acknowledgments

- **FastAPI** - For the amazing web framework
- **Tailwind CSS** - For the utility-first CSS framework
- **Chart.js** - For beautiful chart visualizations
- **Font Awesome** - For the comprehensive icon library
- **AI Community** - For inspiration in nutrition analysis algorithms

---

## 📸 Screenshots

### Dashboard
![Dashboard](screenshots/dashboard.png)
*Beautiful glassmorphism dashboard with real-time nutrition tracking*

### AI Nutritionist
![AI Chat](screenshots/ai-chat.png)
*Interactive AI nutritionist with markdown support and glass-style chat bubbles*

### Analytics
![Analytics](screenshots/analytics.png)
*Comprehensive charts with neon colors and dark theme styling*

### Mobile Experience
![Mobile](screenshots/mobile.png)
*Fully responsive design with collapsible sidebar for mobile devices*

---

## 📊 Project Stats

![Lines of Code](https://img.shields.io/tokei/lines/github/zohaibmuaz/the-nutritionist?style=flat-square)
![Repo Size](https://img.shields.io/github/repo-size/zohaibmuaz/the-nutritionist?style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/zohaibmuaz/the-nutritionist?style=flat-square)

---

<div align="center">

**Made with ❤️ by Zohaib Muaz**

*THE Nutritionist™ - Transforming Health Through Technology*

</div>