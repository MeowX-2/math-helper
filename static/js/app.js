/**
 * HintSpark — Frontend Application Logic
 * =====================================
 * Handles article fetching, Markdown parsing, KaTeX math rendering, topic filtering,
 * article creation, full reader modal, theme toggling, and real-time AI tutor interaction.
 */

// Application State Variables
let currentTopic = 'All'; // Active category filter
let currentTag = 'All';   // Active tag filter
let heroArticle = null;   // Currently featured top article
let allArticlesList = []; // Cached all articles list

/**
 * Render mathematical expressions inside a DOM element using KaTeX.
 * Parses both inline ($...$) and block ($$...$$) LaTeX expressions.
 * @param {HTMLElement} element - Target container element to search for LaTeX tokens.
 */
function renderMath(element) {
    if (typeof renderMathInElement === 'function') {
        try {
            renderMathInElement(element, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false }
                ],
                throwOnError: false
            });
        } catch (e) {
            console.warn('KaTeX render warning:', e);
        }
    }
}

/**
 * Render Markdown content and KaTeX mathematical notation into a target DOM container.
 * Safely protects math expressions ($...$ and $$...$$) from being corrupted by Markdown parsers.
 * @param {HTMLElement} container - Target DOM element.
 * @param {string} content - Raw text containing Markdown formatting and embedded LaTeX.
 */
function renderFormattedContent(container, content) {
    if (!container) return;
    if (!content) {
        container.innerHTML = '';
        return;
    }

    const mathBlocks = [];
    
    // Protect display math $$...$$
    let protectedText = content.replace(/\$\$([\s\S]+?)\$\$/g, (match) => {
        mathBlocks.push(match);
        return `@@KATEXMATH${mathBlocks.length - 1}@@`;
    });

    // Protect inline math $...$
    protectedText = protectedText.replace(/\$([^\$\n\r]+?)\$/g, (match) => {
        mathBlocks.push(match);
        return `@@KATEXMATH${mathBlocks.length - 1}@@`;
    });

    // Parse Markdown to HTML via marked.js
    let html = '';
    if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
        try {
            html = marked.parse(protectedText, { breaks: true, gfm: true });
        } catch (e) {
            console.warn('Marked parsing error fallback:', e);
            html = escapeHtml(protectedText).replace(/\n/g, '<br>');
        }
    } else {
        html = escapeHtml(protectedText).replace(/\n/g, '<br>');
    }

    // Restore protected math blocks
    html = html.replace(/@@KATEXMATH(\d+)@@/g, (match, id) => {
        return mathBlocks[parseInt(id, 10)] || '';
    });

    container.innerHTML = html;
    renderMath(container);
}

/**
 * Asynchronously fetch article records from backend REST API with optional
 * category, tag filter, and live keyword search.
 */
async function fetchArticles() {
    try {
        const searchInput = document.getElementById('search-input');
        const searchVal = searchInput ? searchInput.value.trim() : '';
        const url = `/api/blogs?category=${encodeURIComponent(currentTopic)}&tag=${encodeURIComponent(currentTag)}&search=${encodeURIComponent(searchVal)}`;
        
        const res = await fetch(url);
        const data = await res.json();

        if (data.status === 'success') {
            if (currentTopic === 'All' && currentTag === 'All' && !searchVal) {
                allArticlesList = data.blogs;
            }
            renderArticles(data.blogs);
            renderTagFilterBars(allArticlesList.length > 0 ? allArticlesList : data.blogs);
        }
    } catch (err) {
        console.error('Error fetching articles:', err);
    }
}

/**
 * Render dynamic Tag Cloud in sidebar and Tag Bar above article grid.
 * @param {Array} blogs - Full array of blog post objects.
 */
function renderTagFilterBars(blogs) {
    const mainTagBar = document.getElementById('main-tag-filter-bar');
    const sidebarTagCloud = document.getElementById('sidebar-tag-cloud');
    if (!blogs) return;

    // Collect unique tags
    const tagMap = new Map();
    blogs.forEach(b => {
        const tags = b.tags && Array.isArray(b.tags) ? b.tags : [b.category || 'Math'];
        tags.forEach(t => {
            const clean = t.trim();
            if (clean) tagMap.set(clean, (tagMap.get(clean) || 0) + 1);
        });
    });

    const uniqueTags = Array.from(tagMap.keys());

    // Render Main Tag Filter Bar above grid
    if (mainTagBar) {
        mainTagBar.innerHTML = '';
        
        const allBtn = document.createElement('button');
        allBtn.className = `tag-chip-btn ${currentTag === 'All' ? 'active' : ''}`;
        allBtn.textContent = '🏷️ All Tags';
        allBtn.onclick = () => filterByTag('All');
        mainTagBar.appendChild(allBtn);

        uniqueTags.forEach(tag => {
            const btn = document.createElement('button');
            btn.className = `tag-chip-btn ${currentTag.toLowerCase() === tag.toLowerCase() ? 'active' : ''}`;
            btn.textContent = `#${tag}`;
            btn.onclick = () => filterByTag(tag);
            mainTagBar.appendChild(btn);
        });
    }

    // Render Sidebar Tag Cloud
    if (sidebarTagCloud) {
        sidebarTagCloud.innerHTML = '';

        uniqueTags.forEach(tag => {
            const tagBadge = document.createElement('span');
            tagBadge.className = `sidebar-tag-badge ${currentTag.toLowerCase() === tag.toLowerCase() ? 'active' : ''}`;
            tagBadge.textContent = `#${tag}`;
            tagBadge.onclick = () => filterByTag(tag);
            sidebarTagCloud.appendChild(tagBadge);
        });
    }
}

/**
 * Filter feed stories by selecting a specific tag.
 * @param {string} tag - Selected tag name ('All', 'UserGuide', 'Calculus', etc.)
 */
function filterByTag(tag) {
    currentTag = tag;
    currentTopic = 'All';

    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const allNavItem = document.getElementById('nav-item-all');
    if (allNavItem && tag === 'All') allNavItem.classList.add('active');

    document.getElementById('page-heading').textContent = tag === 'All' ? 'Mathematical Insights & Essays' : `#${tag} Archive`;
    document.getElementById('grid-label').textContent = tag === 'All' ? 'Recent Math Articles' : `Articles tagged with #${tag}`;
    fetchArticles();
}

/**
 * Open the HintSpark User Guide & Showcase article directly.
 * @param {HTMLElement} navElement - Navigation DOM element clicked.
 */
function openUserGuide(navElement) {
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if (navElement) navElement.classList.add('active');

    filterByTag('UserGuide');
    
    // Find UserGuide article if loaded
    const guideArticle = allArticlesList.find(b => b.category === 'UserGuide' || b.id === '100' || (b.tags && b.tags.includes('UserGuide')));
    if (guideArticle) {
        openReader(guideArticle);
    }
}

/**
 * Populate DOM with articles data into the Featured Hero card and Articles Grid.
 * @param {Array} blogs - Array of blog post objects returned from backend.
 */
function renderArticles(blogs) {
    const heroSection = document.getElementById('hero-card');
    const gridSection = document.getElementById('articles-grid');
    gridSection.innerHTML = '';

    // Empty State Handler
    if (!blogs || blogs.length === 0) {
        heroSection.style.display = 'none';
        gridSection.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: var(--text-muted); padding: 4rem 1rem;">
                <p style="font-family: var(--font-display); font-size: 1.5rem; margin-bottom: 0.5rem;">No articles found.</p>
                <p style="font-size: 0.9rem;">Click "+ New Article" in the sidebar to contribute!</p>
            </div>
        `;
        return;
    }

    // Render Featured Hero Article (First article in list)
    heroSection.style.display = 'block';
    heroArticle = blogs[0];

    document.getElementById('hero-tag').textContent = heroArticle.category || 'MATHEMATICS';
    document.getElementById('hero-title').textContent = heroArticle.title;
    document.getElementById('hero-excerpt').textContent = heroArticle.subtitle || (heroArticle.content.substring(0, 150) + '...');
    document.getElementById('hero-author').textContent = heroArticle.author;
    document.getElementById('hero-date').textContent = heroArticle.date;
    document.getElementById('hero-readtime').textContent = `📖 ${heroArticle.read_time || '2 min read'}`;

    // Render Hero Tag Chips
    const heroTagsElem = document.getElementById('hero-tags');
    if (heroTagsElem) {
        heroTagsElem.innerHTML = '';
        const tags = heroArticle.tags && heroArticle.tags.length > 0 ? heroArticle.tags : [heroArticle.category || 'Math'];
        tags.forEach(t => {
            const tagSpan = document.createElement('span');
            tagSpan.className = 'hero-tag-pill';
            tagSpan.textContent = `#${t}`;
            tagSpan.onclick = (e) => {
                e.stopPropagation();
                filterByTag(t);
            };
            heroTagsElem.appendChild(tagSpan);
        });
    }

    renderMath(heroSection);

    // Render Remaining Articles in Substack-Style Grid
    const gridBlogs = blogs.slice(1);
    gridBlogs.forEach(blog => {
        const card = document.createElement('article');
        card.className = 'article-card';
        card.onclick = () => openReader(blog);

        const blogTags = blog.tags && blog.tags.length > 0 ? blog.tags : [blog.category || 'MATH'];
        const tagsHtml = blogTags.map(t => `<span class="card-tag-pill" onclick="event.stopPropagation(); filterByTag('${escapeHtml(t)}')">#${escapeHtml(t)}</span>`).join(' ');

        card.innerHTML = `
            <div>
                <div class="card-tags-bar">${tagsHtml}</div>
                <h3 class="article-card-title">${escapeHtml(blog.title)}</h3>
                <p class="article-card-subtitle">${escapeHtml(blog.subtitle || (blog.content.substring(0, 110) + '...'))}</p>
            </div>
            <div class="meta-strip">
                <span class="meta-author">${escapeHtml(blog.author)}</span>
                <span class="dot">•</span>
                <span>📖 ${escapeHtml(blog.read_time || '2 min read')}</span>
            </div>
        `;
        gridSection.appendChild(card);
        renderMath(card);
    });
}

/**
 * Filter feed articles by selecting a specific topic category.
 * @param {string} topic - Category name ('All', 'Calculus', etc.)
 * @param {HTMLElement} element - Clicked DOM sidebar navigation link.
 */
function selectTopic(topic, element) {
    currentTopic = topic;
    currentTag = 'All';
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    if (element) element.classList.add('active');

    document.getElementById('page-heading').textContent = topic === 'All' ? 'Mathematical Insights & Essays' : `${topic} Archive`;
    document.getElementById('grid-label').textContent = topic === 'All' ? 'Recent Math Articles' : `Articles in ${topic}`;
    fetchArticles();
}

/**
 * Reset active category topic filter and clear search query input.
 */
function resetTopic() {
    document.getElementById('search-input').value = '';
    currentTag = 'All';
    selectTopic('All', document.getElementById('nav-item-all'));
}

/**
 * Event handler triggered on user input in search bar.
 */
function onSearchInput() {
    fetchArticles();
}

// ==============================================================================
// Article Reader Overlay Logic
// ==============================================================================

/**
 * Open full-screen reader modal overlay for a selected article object.
 * @param {Object} article - Blog post item containing title, content, author, etc.
 */
function openReader(article) {
    document.getElementById('reader-tag').textContent = article.category || 'MATHEMATICS';
    document.getElementById('reader-title').textContent = article.title;
    document.getElementById('reader-subtitle').textContent = article.subtitle || '';
    document.getElementById('reader-author').textContent = article.author;
    document.getElementById('reader-date').textContent = article.date;
    document.getElementById('reader-readtime').textContent = `📖 ${article.read_time || '3 min read'}`;

    // Render tags in reader modal
    const readerTagsElem = document.getElementById('reader-tags');
    if (readerTagsElem) {
        readerTagsElem.innerHTML = '';
        const tags = article.tags && article.tags.length > 0 ? article.tags : [article.category || 'Math'];
        tags.forEach(t => {
            const span = document.createElement('span');
            span.className = 'reader-tag-pill';
            span.textContent = `#${t}`;
            span.onclick = () => {
                closeReader();
                filterByTag(t);
            };
            readerTagsElem.appendChild(span);
        });
    }

    // Wire Delete Article button
    const deleteBtn = document.getElementById('reader-delete-btn');
    if (deleteBtn) {
        deleteBtn.onclick = () => deleteArticle(article.id);
    }

    const bodyElem = document.getElementById('reader-body');
    renderFormattedContent(bodyElem, article.content);

    document.getElementById('reader-overlay').classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
}

/**
 * Delete an article by ID with user confirmation toast.
 * @param {string} articleId - Target article ID.
 */
async function deleteArticle(articleId) {
    if (!confirm('Are you sure you want to delete this article? This action cannot be undone.')) {
        return;
    }

    try {
        const res = await fetch(`/api/blogs/${encodeURIComponent(articleId)}`, { method: 'DELETE' });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
            closeReader();
            showToast('Article deleted successfully!', 'info');
            fetchArticles();
        } else {
            showToast(`Delete failed: ${data.message || 'Unknown error'}`, 'error');
        }
    } catch (err) {
        console.error('Delete error:', err);
        showToast('Network error while deleting article', 'error');
    }
}

/**
 * Helper to open the reader overlay for the currently featured Hero Article.
 */
function openHeroReader() {
    if (heroArticle) openReader(heroArticle);
}

/**
 * Close article reader overlay modal.
 */
function closeReader() {
    document.getElementById('reader-overlay').classList.remove('active');
    document.body.style.overflow = 'auto'; // Restore scrolling
}

// ==============================================================================
// Publish Article Modal Logic
// ==============================================================================

/** Open publish article form modal. */
function openPublishModal() {
    document.getElementById('publish-modal').classList.add('active');
}

/** Close publish article form modal. */
function closePublishModal() {
    document.getElementById('publish-modal').classList.remove('active');
}

/**
 * Handle form submission for creating a new math article.
 * @param {Event} e - Form submit event.
 */
async function handlePublishSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('pub-title').value.trim();
    const subtitle = document.getElementById('pub-subtitle').value.trim();
    const author = document.getElementById('pub-author').value.trim();
    const category = document.getElementById('pub-category').value;
    const tagsInput = document.getElementById('pub-tags') ? document.getElementById('pub-tags').value.trim() : '';
    const content = document.getElementById('pub-content').value.trim();

    if (!title || !content) return;

    try {
        const res = await fetch('/api/blogs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, subtitle, author, category, tags: tagsInput, content })
        });
        const data = await res.json();
        
        if (res.ok && data.status === 'success') {
            closePublishModal();
            document.querySelector('#publish-modal form').reset();
            fetchArticles(); // Refresh article grid
            showToast('Article published successfully!', 'success');
        } else {
            showToast(`Publish failed: ${data.message}`, 'error');
        }
    } catch (err) {
        console.error('Error publishing:', err);
        showToast('Network error during publication', 'error');
    }
}

// ==============================================================================
// AI Tutor Assistant Logic (Side Drawer Chat)
// ==============================================================================

// Chat memory state for multi-turn conversation
let chatHistory = [];

/** Load saved conversation history from sessionStorage on page load. */
function restoreChatHistory() {
    try {
        const saved = sessionStorage.getItem('hintspark_chat_history');
        if (saved) {
            chatHistory = JSON.parse(saved);
            renderChatHistoryUI();
        }
    } catch (e) {
        console.warn('Error restoring chat history:', e);
        chatHistory = [];
    }
}

/** Save active conversation history to sessionStorage. */
function saveChatHistory() {
    try {
        sessionStorage.setItem('hintspark_chat_history', JSON.stringify(chatHistory));
    } catch (e) {
        console.warn('Error saving chat history:', e);
    }
}

/**
 * Handle keydown events on tutor input textarea (Enter to send, Shift+Enter for newline).
 * @param {KeyboardEvent} e - Keyboard event.
 */
function handleTutorInputKeyDown(e) {
    const input = e.target;
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendTutorMessage();
    } else {
        setTimeout(() => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 120) + 'px';
        }, 0);
    }
}

/**
 * Attach a sleek copy-to-clipboard button on an AI message bubble.
 * @param {HTMLElement} msgDiv - Target DOM message element.
 * @param {string} textContent - Raw text to copy.
 */
function attachCopyButton(msgDiv, textContent) {
    if (!msgDiv || !textContent) return;
    const copyBtn = document.createElement('button');
    copyBtn.className = 'tutor-copy-btn';
    copyBtn.title = 'Copy response text';
    copyBtn.innerHTML = '📋 Copy';
    copyBtn.onclick = (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(textContent).then(() => {
            copyBtn.innerHTML = '✅ Copied!';
            setTimeout(() => { copyBtn.innerHTML = '📋 Copy'; }, 2000);
        }).catch(err => {
            console.warn('Clipboard copy warning:', err);
        });
    };
    msgDiv.appendChild(copyBtn);
}

/** Render stored chat history bubbles into the drawer container. */
function renderChatHistoryUI() {
    const container = document.getElementById('tutor-messages');
    if (!container) return;

    container.innerHTML = `
        <div class="tutor-msg tutor-ai-msg">
            Hello! I am your Socratic AI math tutor. Ask me any equation or problem concept — I will guide you with targeted questions and hints without giving away the final solution!
        </div>
    `;

    chatHistory.forEach(msg => {
        const msgDiv = document.createElement('div');
        if (msg.role === 'user') {
            msgDiv.className = 'tutor-msg tutor-user-msg';
            msgDiv.textContent = msg.content;
        } else {
            msgDiv.className = 'tutor-msg tutor-ai-msg';
            renderFormattedContent(msgDiv, msg.content);
            attachCopyButton(msgDiv, msg.content);
        }
        container.appendChild(msgDiv);
    });

    container.scrollTop = container.scrollHeight;
}

/** Reset active conversation session and clear chat memory history. */
function resetTutorChat() {
    chatHistory = [];
    sessionStorage.removeItem('hintspark_chat_history');
    renderChatHistoryUI();
    showToast('Started a new conversation session', 'info');
}

/** Toggle AI Math Tutor side drawer visibility. Prompt for API key if missing. */
async function toggleTutorDrawer() {
    const drawer = document.getElementById('tutor-drawer');
    const isOpening = !drawer.classList.contains('active');
    drawer.classList.toggle('active');

    if (isOpening) {
        const userApiKey = localStorage.getItem('user_gemini_api_key');
        if (!userApiKey) {
            try {
                const res = await fetch('/api/check_key');
                const data = await res.json();
                if (!data.has_key) {
                    showToast('Gemini API Key required to activate AI Tutor.', 'info');
                    openSettingsModal();
                }
            } catch (err) {
                console.warn('API key check fallback:', err);
            }
        }
    }
}

/**
 * Handle Enter keypress in tutor input textarea (Enter to send, Shift+Enter for new line).
 * @param {KeyboardEvent} e - Event object.
 */
function handleTutorInputKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendTutorMessage();
    }
}

/**
 * Send user's math problem prompt to backend `/get_hint` endpoint with conversation history
 * and render the tutor's Markdown + LaTeX-annotated response.
 */
async function sendTutorMessage() {
    const input = document.getElementById('tutor-input');
    const sendBtn = document.getElementById('tutor-send-btn');
    const prompt = input.value.trim();
    if (!prompt) return;

    const container = document.getElementById('tutor-messages');

    // 1. Append User Prompt Bubble & record in memory state
    const userMsg = document.createElement('div');
    userMsg.className = 'tutor-msg tutor-user-msg';
    userMsg.textContent = prompt;
    container.appendChild(userMsg);
    input.value = '';
    input.style.height = '';
    container.scrollTop = container.scrollHeight;

    // Snapshot current prior history to send to backend
    const priorHistory = [...chatHistory];

    // Add user turn to local history array
    chatHistory.push({ role: 'user', content: prompt });

    // 2. Append Loading Indicator
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'tutor-msg tutor-ai-msg';
    loadingMsg.id = 'active-loading-msg';
    loadingMsg.innerHTML = `
        <div class="loading-indicator">
            <div class="spinner-dots">
                <div></div><div></div><div></div>
            </div>
            <span>Please wait... HintSpark is thinking</span>
        </div>
    `;
    container.appendChild(loadingMsg);
    container.scrollTop = container.scrollHeight;

    // Disable input controls while waiting
    input.disabled = true;
    sendBtn.disabled = true;

    try {
        const userApiKey = localStorage.getItem('user_gemini_api_key') || '';
        const headers = { 'Content-Type': 'application/json' };
        if (userApiKey) {
            headers['X-Gemini-API-Key'] = userApiKey;
        }

        const res = await fetch('/get_hint', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ prompt, history: priorHistory })
        });
        
        let data = {};
        const contentType = res.headers.get('content-type') || '';
        if (contentType.includes('application/json')) {
            data = await res.json();
        } else {
            const rawText = await res.text();
            data = { status: 'error', message: `Server Error (${res.status}): Please verify backend server logs.` };
        }

        // Remove loading state
        const activeLoading = document.getElementById('active-loading-msg');
        if (activeLoading) activeLoading.remove();

        // Append AI Response Bubble
        const aiMsg = document.createElement('div');
        aiMsg.className = 'tutor-msg tutor-ai-msg';
        container.appendChild(aiMsg);

        if (data.status === 'success' && data.response) {
            renderFormattedContent(aiMsg, data.response);
            attachCopyButton(aiMsg, data.response);
            chatHistory.push({ role: 'assistant', content: data.response });
            saveChatHistory();
        } else {
            // Revert last user prompt from history if call failed
            chatHistory.pop();
            const errText = data.message || 'Unable to generate hint. Please check your API key.';
            renderFormattedContent(aiMsg, `Error: ${errText}`);
            if (errText.includes('API key') || errText.includes('API Key') || errText.includes('401') || errText.includes('INVALID')) {
                localStorage.removeItem('user_gemini_api_key');
                openSettingsModal();
            }
        }
        
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Tutor error:', err);
        chatHistory.pop(); // Revert failed turn
        const activeLoading = document.getElementById('active-loading-msg');
        if (activeLoading) activeLoading.remove();

        const errMsg = document.createElement('div');
        errMsg.className = 'tutor-msg tutor-ai-msg';
        
        if (err.name === 'TypeError' && err.message.includes('fetch')) {
            errMsg.textContent = 'Connection Error: Make sure python app.py is running and your internet connection is active.';
        } else {
            errMsg.textContent = `Error: ${err.message || 'Network request failed. Please try again.'}`;
        }
        
        container.appendChild(errMsg);
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

// ==============================================================================
// Settings API Key & .env Setup Modal Logic
// ==============================================================================

/** Open custom API Key settings modal dialog. */
function openSettingsModal() {
    const customInput = document.getElementById('custom-api-key');
    if (customInput) {
        customInput.value = localStorage.getItem('user_gemini_api_key') || '';
    }
    document.getElementById('settings-modal').classList.add('active');
}

/** Close custom API Key settings modal dialog. */
function closeSettingsModal() {
    document.getElementById('settings-modal').classList.remove('active');
}

/**
 * Handle form submission for saving custom client API Key into localStorage and writing .env on disk.
 * @param {Event} e - Form submit event.
 */
async function handleSaveApiKey(e) {
    e.preventDefault();
    const rawKey = document.getElementById('custom-api-key').value.trim();
    const cleanKey = rawKey.replace(/^["']|["']$/g, '').trim();
    if (!cleanKey) return;

    try {
        // Save clean key in localStorage for browser state
        localStorage.setItem('user_gemini_api_key', cleanKey);

        // Call backend API to write .env file to project root on disk
        const res = await fetch('/api/save_env', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: cleanKey })
        });
        const data = await res.json();

        if (res.ok && data.status === 'success') {
            showToast('.env file created & API key configured!', 'success');
            closeSettingsModal();
        } else {
            showToast(`API Key saved in browser (server note: ${data.message})`, 'info');
            closeSettingsModal();
        }
    } catch (err) {
        console.error('Error saving .env file:', err);
        showToast('API Key saved in browser localStorage', 'success');
        closeSettingsModal();
    }
}

/** Clear custom API Key from localStorage and server .env file on disk. */
async function clearApiKey() {
    // 1. Clear browser state
    localStorage.removeItem('user_gemini_api_key');
    const customInput = document.getElementById('custom-api-key');
    if (customInput) customInput.value = '';

    // 2. Call backend to wipe .env file on disk and in-memory os.environ
    try {
        const res = await fetch('/api/clear_key', { method: 'POST' });
        const data = await res.json();
        if (res.ok && data.status === 'success') {
            showToast('.env file & browser API keys cleared!', 'info');
        } else {
            showToast('Browser API key cleared', 'info');
        }
    } catch (err) {
        console.error('Error clearing .env file:', err);
        showToast('Browser API key cleared', 'info');
    }

    closeSettingsModal();
}

// ==============================================================================
// Theme Toggle & Utility Functions
// ==============================================================================

/** Toggle between Light Mode and Dark Mode themes. */
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);

    document.getElementById('theme-text').textContent = newTheme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
    showToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
}

/**
 * Utility function to sanitize raw strings for HTML rendering.
 * @param {string} str - Raw text string.
 * @returns {string} Escaped HTML string.
 */
function escapeHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * Populate tutor input box with a quick suggestion prompt and send automatically.
 * @param {string} promptText - Selected prompt text.
 */
function setTutorPrompt(promptText) {
    const input = document.getElementById('tutor-input');
    if (input) {
        input.value = promptText;
        sendTutorMessage();
    }
}

/**
 * Show a sleek floating toast notification.
 * @param {string} message - Notification text.
 * @param {string} type - Toast type ('success' or 'info' or 'error').
 */
function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `toast-item toast-${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Global Keyboard Shortcuts Listener
document.addEventListener('keydown', (e) => {
    // Ctrl+K or Cmd+K: Focus Search Bar
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        if (searchInput) searchInput.focus();
    }
    // Escape: Close active overlays
    if (e.key === 'Escape') {
        closeReader();
        closePublishModal();
        closeSettingsModal();
        const tutorDrawer = document.getElementById('tutor-drawer');
        if (tutorDrawer && tutorDrawer.classList.contains('active')) {
            toggleTutorDrawer();
        }
    }
});

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    fetchArticles();
    restoreChatHistory();
    
    // Register PWA Service Worker for App Mode Installation
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .catch(err => console.warn('PWA ServiceWorker note:', err));
    }
});
