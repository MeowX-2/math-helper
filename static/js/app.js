/**
 * HintSpark — Frontend Application Logic
 * =====================================
 * Handles article fetching, Markdown parsing, KaTeX math rendering, topic filtering,
 * article creation, full reader modal, theme toggling, and real-time AI tutor interaction.
 */

// Application State Variables
let currentTopic = 'All'; // Active category filter
let heroArticle = null;   // Currently featured top article

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

    // 1. Extract and protect math expressions using unique placeholders (no markdown special characters)
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

    // 2. Parse Markdown to HTML via marked.js
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

    // 3. Restore protected math blocks back into HTML
    html = html.replace(/@@KATEXMATH(\d+)@@/g, (match, id) => {
        return mathBlocks[parseInt(id, 10)] || '';
    });

    // 4. Update container innerHTML
    container.innerHTML = html;

    // 5. Render KaTeX expressions inside container
    renderMath(container);
}

/**
 * Asynchronously fetch article records from backend REST API with optional
 * topic category filter and live keyword search.
 */
async function fetchArticles() {
    try {
        const searchInput = document.getElementById('search-input');
        const searchVal = searchInput ? searchInput.value.trim() : '';
        const url = `/api/blogs?category=${encodeURIComponent(currentTopic)}&search=${encodeURIComponent(searchVal)}`;
        
        const res = await fetch(url);
        const data = await res.json();

        if (data.status === 'success') {
            renderArticles(data.blogs);
        }
    } catch (err) {
        console.error('Error fetching articles:', err);
    }
}

/**
 * Populate DOM with articles data into the Featured Hero card and Articles Grid.
 * @param {Array} blogs - Array of blog post objects returned from the backend API.
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
                <p style="font-family: var(--font-title); font-size: 1.5rem; margin-bottom: 0.5rem;">No stories found.</p>
                <p style="font-size: 0.9rem;">Click "+ Publish Story" in the sidebar to contribute!</p>
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
    renderMath(heroSection);

    // Render Remaining Articles in Substack-Style Grid
    const gridBlogs = blogs.slice(1);
    gridBlogs.forEach(blog => {
        const card = document.createElement('article');
        card.className = 'article-card';
        card.onclick = () => openReader(blog);

        card.innerHTML = `
            <div>
                <div class="article-card-tag">${escapeHtml(blog.category || 'MATH')}</div>
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
 * @param {string} topic - Category name ('All', 'NumberTheory', 'Calculus', etc.)
 * @param {HTMLElement} element - Clicked DOM sidebar navigation link.
 */
function selectTopic(topic, element) {
    currentTopic = topic;
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
    selectTopic('All', document.querySelector('.nav-item'));
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

    const bodyElem = document.getElementById('reader-body');
    renderFormattedContent(bodyElem, article.content);

    document.getElementById('reader-overlay').classList.add('active');
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
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
    const content = document.getElementById('pub-content').value.trim();

    if (!title || !content) return;

    try {
        const res = await fetch('/api/blogs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, subtitle, author, category, content })
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

/** Toggle AI Math Tutor side drawer visibility. */
function toggleTutorDrawer() {
    document.getElementById('tutor-drawer').classList.toggle('active');
}

/**
 * Send user's math problem prompt to backend `/get_hint` endpoint
 * and render the tutor's Markdown + LaTeX-annotated response.
 */
async function sendTutorMessage() {
    const input = document.getElementById('tutor-input');
    const sendBtn = document.getElementById('tutor-send-btn');
    const prompt = input.value.trim();
    if (!prompt) return;

    const container = document.getElementById('tutor-messages');

    // 1. Append User Prompt Bubble
    const userMsg = document.createElement('div');
    userMsg.className = 'tutor-msg tutor-user-msg';
    userMsg.textContent = prompt;
    container.appendChild(userMsg);
    input.value = '';
    container.scrollTop = container.scrollHeight;

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
        const res = await fetch('/get_hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        const data = await res.json();

        // Remove loading state
        const activeLoading = document.getElementById('active-loading-msg');
        if (activeLoading) activeLoading.remove();

        // Append AI Response Bubble
        const aiMsg = document.createElement('div');
        aiMsg.className = 'tutor-msg tutor-ai-msg';
        container.appendChild(aiMsg);

        if (res.ok && data.status === 'success') {
            renderFormattedContent(aiMsg, data.response);
        } else {
            renderFormattedContent(aiMsg, `Error: ${data.message || 'Unable to generate hint.'}`);
        }
        
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Tutor error:', err);
        const activeLoading = document.getElementById('active-loading-msg');
        if (activeLoading) activeLoading.remove();

        const errMsg = document.createElement('div');
        errMsg.className = 'tutor-msg tutor-ai-msg';
        errMsg.textContent = 'Network error. Please try again.';
        container.appendChild(errMsg);
    } finally {
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
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
        const tutorDrawer = document.getElementById('tutor-drawer');
        if (tutorDrawer && tutorDrawer.classList.contains('active')) {
            toggleTutorDrawer();
        }
    }
});

// Initialize application on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    fetchArticles();
    
    // Register PWA Service Worker for App Mode Installation
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .catch(err => console.warn('PWA ServiceWorker note:', err));
    }
});
