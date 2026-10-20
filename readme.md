Assistly — RAG-Powered Telegram AI Assistant
Assistly is an AI-powered Telegram chatbot built with Python, designed to answer user questions based on a predefined knowledge base, collect customer requests, and provide a web-based admin panel for managing the assistant.
Features
LLM Integration: Connects to language models through the OpenRouter API.
Retrieval-Augmented Generation (RAG): Retrieves relevant information from a custom knowledge base before generating answers.
Knowledge-Based Responses: Uses information stored in knowledge/train.txt to answer questions.
Reduced Hallucinations: If the required information is not available in the knowledge base, the assistant is instructed to indicate that sufficient information is unavailable instead of inventing an answer.
Semantic Search: Uses Sentence Transformers to generate text embeddings and ChromaDB for vector storage and retrieval.
Customer Request Collection: Collects customer names and Iranian mobile numbers through a Telegram conversation.
Admin Notifications: Sends submitted customer requests to the configured Telegram administrator.
Request Logging: Stores submitted requests in a local text file.
Configurable Language Model: Supports selecting the configured LLM through the project's model configuration.
Tech Stack
Python
python-telegram-bot
OpenAI Python SDK
OpenRouter API
Sentence Transformers
ChromaDB
RAG (Retrieval-Augmented Generation)
python-dotenv
How RAG Works
The knowledge base is stored in knowledge/train.txt.
The text is divided into chunks.
Sentence Transformers converts the chunks into vector embeddings.
ChromaDB stores the embeddings and associated text.
When a user asks a question, the system retrieves relevant information from the knowledge base.
The retrieved context is passed to the configured language model.
The assistant generates a response based on the available information.
The assistant is designed to avoid providing unsupported answers when the knowledge base does not contain the requested information.
Installation
1. Clone the repository
git clone <repository-url>
cd Assistly
2. Create a virtual environment
python -m venv venv
Activate it on Windows PowerShell:
.\venv\Scripts\Activate.ps1
3. Install dependencies
Install the packages required by the project:
pip install python-telegram-bot openai python-dotenv chromadb sentence-transformers
4. Configure environment variables
Create a .env file in the project root:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_api_key
Never commit your .env file or expose your API keys.
5. Prepare the knowledge base
Add your information to:
knowledge/train.txt
Separate individual knowledge entries with blank lines.
6. Build the knowledge database
python rag.py
7. Run the Telegram bot
python bot.py
Open your bot in Telegram and send /start.
Available Commands

Project Structure
Assistly/
├── bot.py
├── rag.py
├── config.py
├── knowledge/
│   └── train.txt
├── chroma_db/
├── admin/
├── requests.txt
├── .env
└── venv/
Note: The exact project structure may vary depending on the current implementation.
Example
User: What training courses do you offer?
Assistly: We offer Network+, Security+, and CEH courses.
User: What is the price of the Security+ course?
Assistly: Sufficient information about the course price is currently unavailable.
These examples demonstrate how the assistant uses the knowledge base to answer supported questions and declines to invent missing details.
Future Improvements
Web-based knowledge base management
Uploading and editing knowledge sources through the admin panel
Improved retrieval accuracy and relevance ranking
Support for additional messaging platforms
Enhanced request management and analytics
License
Specify a license before distributing this project publicly.