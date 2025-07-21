# 🛒 Einstein AI Shopping Agent

A modern web application that provides an intelligent shopping assistant powered by Salesforce Einstein AI. This project demonstrates advanced API integration, real-time chat functionality, and cloud deployment capabilities.

## 🌐 Live Demo

**Try it now:** [https://einstein-shopping-agent-220897b2120c.herokuapp.com/](https://einstein-shopping-agent-220897b2120c.herokuapp.com/)

## ✨ Features

- **🤖 AI-Powered Chat**: Real-time conversations with Salesforce Einstein AI Agent
- **🛍️ Shopping Assistant**: Product recommendations, order status, and reorder assistance
- **📱 Responsive Design**: Beautiful, modern UI that works on desktop and mobile
- **⚡ Real-time Features**: Typing indicators, instant messaging, and status updates
- **🔒 Secure**: Environment-based configuration with OAuth 2.0 authentication
- **☁️ Cloud-Ready**: Deployed on Heroku with production-grade setup

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Salesforce    │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   Einstein AI   │
│                 │    │                 │    │   Agent         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Tech Stack

### Backend
- **Python 3.11.6** - Core language
- **Flask 3.0.0** - Web framework
- **Gunicorn** - WSGI HTTP Server
- **Requests** - HTTP library for API calls

### Frontend
- **HTML5** - Structure
- **CSS3** - Modern styling with gradients and animations
- **Vanilla JavaScript** - Real-time chat functionality
- **Font Awesome** - Icons
- **Google Fonts (Inter)** - Typography

### APIs & Services
- **Salesforce Einstein AI Agent API** - AI-powered conversations
- **OAuth 2.0** - Secure authentication
- **Heroku** - Cloud deployment platform

## 🛠️ Local Development Setup

### Prerequisites
- Python 3.11+
- Git
- Salesforce Connected App with Einstein AI Agent

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ssmaddux/AgentForce-shopping-agent.git
   cd AgentForce-shopping-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export SF_DOMAIN="https://your-domain.my.salesforce.com"
   export CLIENT_ID="3MVG9XXXXXXXXXXXXXXXXXXXXXXXXX"
   export CLIENT_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   export AGENT_ID="0XXXXXXXXXXXXXXX"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SF_DOMAIN` | Your Salesforce domain URL | `https://mycompany.my.salesforce.com` |
| `CLIENT_ID` | OAuth Consumer Key | `3MVG9XXXXXXXXXXXXXXXXXXXXXXXXX` |
| `CLIENT_SECRET` | OAuth Consumer Secret | `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX` |
| `AGENT_ID` | Einstein AI Agent ID | `0XXXXXXXXXXXXXXX` |

## 🚢 Deployment

### Heroku Deployment

This project is configured for easy Heroku deployment:

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set SF_DOMAIN="https://your-domain.my.salesforce.com"
   heroku config:set CLIENT_ID="3MVG9XXXXXXXXXXXXXXXXXXXXXXXXX"
   heroku config:set CLIENT_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   heroku config:set AGENT_ID="0XXXXXXXXXXXXXXX"
   ```

3. **Deploy**
   ```bash
   git push heroku master
   ```

### Key Files for Deployment
- `Procfile` - Heroku process configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification

## 📋 API Endpoints

### Frontend Routes
- `GET /` - Serves the chat interface

### Backend API
- `POST /api/start-chat` - Initialize new chat session
- `POST /api/send-message` - Send message to AI agent
- `POST /api/end-chat` - Terminate chat session

## 🎨 UI Features

- **Modern Design**: Clean, professional interface with gradient backgrounds
- **Real-time Chat**: Instant messaging with message timestamps
- **Typing Indicators**: Visual feedback when agent is processing
- **Status Indicators**: Connection status and system health
- **Mobile Responsive**: Optimized for all screen sizes
- **Accessibility**: Proper contrast ratios and keyboard navigation

## 🤖 Einstein AI Agent Capabilities

The integrated AI agent can assist with:
- **Product Recommendations** - Intelligent product suggestions
- **Order Status** - Real-time order tracking and updates
- **Reorder Assistance** - Quick reordering of previous purchases
- **Customer Support** - General customer service inquiries

## 📁 Project Structure

```
AgentForce-shopping-agent/
├── app.py                     # Main Flask application
├── main.py                    # Original standalone script
├── config.py                  # Configuration utilities
├── requirements.txt           # Python dependencies
├── Procfile                   # Heroku configuration
├── runtime.txt               # Python version
├── .gitignore                # Git ignore rules
├── templates/
│   └── chat.html             # Chat interface template
└── static/                   # Static assets (auto-created)
    ├── css/
    └── js/
```

## 🔒 Security Features

- **Environment Variables**: Sensitive data stored securely
- **OAuth 2.0**: Industry-standard authentication
- **CORS Protection**: Cross-origin request security
- **Input Sanitization**: XSS protection in chat interface
- **Session Management**: Secure session handling

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify environment variables are set correctly
   - Check Salesforce Connected App configuration
   - Ensure OAuth credentials are valid

2. **Agent Not Responding**
   - Verify `AGENT_ID` is correct
   - Check Salesforce org permissions
   - Review Heroku logs: `heroku logs --tail`

3. **Local Development Issues**
   - Ensure Python 3.11+ is installed
   - Check all dependencies are installed
   - Verify port 5000 is available

## 📊 Performance

- **Response Time**: ~2-3 seconds average for AI responses
- **Scalability**: Horizontal scaling ready with Heroku
- **Caching**: Token caching for improved performance
- **Error Handling**: Comprehensive error management and user feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Salesforce Einstein AI** - For the powerful AI agent capabilities
- **Heroku** - For seamless cloud deployment
- **Flask Community** - For the excellent web framework
- **Font Awesome & Google Fonts** - For beautiful design assets

## 📞 Contact

- **GitHub**: [@ssmaddux](https://github.com/ssmaddux)
- **Email**: madduxsage@gmail.com

---

⭐ **Star this repository if you found it helpful!** 