// BGB RAG Chat - Vanilla JavaScript
(function() {
    'use strict';

    // DOM elements
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const sendButton = document.getElementById('send-button');
    const sendText = document.getElementById('send-text');
    const loadingText = document.getElementById('loading-text');
    const chatMessages = document.getElementById('chat-messages');

    // State
    let isLoading = false;

    // Convert BGB section number to gesetze-im-internet.de URL
    function sectionToUrl(section) {
        // Extract number from section string (§ 1922 → 1922)
        const match = section.match(/§\s*(\d+[a-z]?)/i);
        if (!match) return null;

        const sectionNum = match[1];
        // Format: https://www.gesetze-im-internet.de/bgb/__1922.html
        return `https://www.gesetze-im-internet.de/bgb/__${sectionNum}.html`;
    }

    // Add message to chat
    function addMessage(content, type = 'assistant', sources = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        // Add main content
        const textP = document.createElement('p');
        textP.textContent = content;
        contentDiv.appendChild(textP);

        // Add sources if provided
        if (sources && sources.length > 0) {
            const sourcesDiv = document.createElement('div');
            sourcesDiv.className = 'sources';

            const sourcesTitle = document.createElement('div');
            sourcesTitle.className = 'sources-title';
            sourcesTitle.textContent = 'Quellen:';
            sourcesDiv.appendChild(sourcesTitle);

            sources.forEach(source => {
                const sourceItem = document.createElement('div');
                sourceItem.className = 'source-item';

                const url = sectionToUrl(source.section);
                if (url) {
                    const link = document.createElement('a');
                    link.href = url;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.className = 'source-link';
                    link.textContent = source.section;

                    sourceItem.appendChild(link);

                    if (source.title) {
                        const title = document.createElement('span');
                        title.className = 'source-title';
                        title.textContent = ` - ${source.title}`;
                        sourceItem.appendChild(title);
                    }
                } else {
                    sourceItem.textContent = source.section;
                    if (source.title) {
                        sourceItem.textContent += ` - ${source.title}`;
                    }
                }

                sourcesDiv.appendChild(sourceItem);
            });

            contentDiv.appendChild(sourcesDiv);
        }

        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        scrollToBottom();

        return messageDiv;
    }

    // Add loading indicator
    function addLoadingIndicator() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message assistant';
        loadingDiv.id = 'loading-indicator';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const loadingDots = document.createElement('div');
        loadingDots.className = 'loading';
        loadingDots.innerHTML = '<div class="loading-dot"></div><div class="loading-dot"></div><div class="loading-dot"></div>';

        contentDiv.appendChild(loadingDots);
        loadingDiv.appendChild(contentDiv);
        chatMessages.appendChild(loadingDiv);

        scrollToBottom();
        return loadingDiv;
    }

    // Remove loading indicator
    function removeLoadingIndicator() {
        const loading = document.getElementById('loading-indicator');
        if (loading) {
            loading.remove();
        }
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Set loading state
    function setLoading(loading) {
        isLoading = loading;
        sendButton.disabled = loading;
        queryInput.disabled = loading;

        if (loading) {
            sendText.style.display = 'none';
            loadingText.style.display = 'inline';
        } else {
            sendText.style.display = 'inline';
            loadingText.style.display = 'none';
        }
    }

    // Send query to API
    async function sendQuery(query) {
        if (!query.trim()) return;

        // Add user message
        addMessage(query, 'user');

        // Clear input
        queryInput.value = '';

        // Set loading state
        setLoading(true);
        const loadingIndicator = addLoadingIndicator();

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    top_k: 6
                })
            });

            removeLoadingIndicator();

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Add assistant response
            addMessage(data.answer, 'assistant', data.sources);

        } catch (error) {
            removeLoadingIndicator();
            console.error('Error:', error);
            addMessage(
                `Fehler beim Verarbeiten Ihrer Anfrage: ${error.message}`,
                'assistant'
            );
        } finally {
            setLoading(false);
            queryInput.focus();
        }
    }

    // Handle form submission
    queryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (!isLoading) {
            const query = queryInput.value.trim();
            if (query) {
                sendQuery(query);
            }
        }
    });

    // Focus input on load
    queryInput.focus();

    // Load chat history from sessionStorage on page load
    function loadChatHistory() {
        const history = sessionStorage.getItem('chatHistory');
        if (history) {
            try {
                const messages = JSON.parse(history);
                messages.forEach(msg => {
                    if (msg.type === 'user') {
                        addMessage(msg.content, 'user');
                    } else {
                        addMessage(msg.content, 'assistant', msg.sources);
                    }
                });
            } catch (e) {
                console.error('Error loading chat history:', e);
            }
        }
    }

    // Save chat history to sessionStorage
    function saveChatHistory() {
        const messages = [];
        chatMessages.querySelectorAll('.message').forEach(msgDiv => {
            if (msgDiv.id === 'loading-indicator') return;

            const isUser = msgDiv.classList.contains('user');
            const content = msgDiv.querySelector('.message-content p').textContent;

            const messageData = {
                type: isUser ? 'user' : 'assistant',
                content: content
            };

            // Save sources if assistant message
            if (!isUser) {
                const sources = [];
                msgDiv.querySelectorAll('.source-item').forEach(sourceItem => {
                    const link = sourceItem.querySelector('.source-link');
                    const titleSpan = sourceItem.querySelector('.source-title');

                    if (link) {
                        sources.push({
                            section: link.textContent,
                            title: titleSpan ? titleSpan.textContent.replace(' - ', '') : ''
                        });
                    }
                });
                if (sources.length > 0) {
                    messageData.sources = sources;
                }
            }

            messages.push(messageData);
        });

        sessionStorage.setItem('chatHistory', JSON.stringify(messages));
    }

    // Save history before page unload
    window.addEventListener('beforeunload', saveChatHistory);

    // Load history on page load
    // Note: Disabled by default to start fresh each time
    // Uncomment the line below to enable persistent history
    // loadChatHistory();

    // Add clear history button (optional)
    window.clearChatHistory = function() {
        sessionStorage.removeItem('chatHistory');
        location.reload();
    };

})();
