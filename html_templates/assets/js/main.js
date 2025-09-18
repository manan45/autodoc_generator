// Main JavaScript for Auto-Generated Documentation
class DocumentationApp {
    constructor() {
        this.searchData = [];
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.setupTheme();
        this.setupNavigation();
        this.setupSearch();
        this.setupMobileMenu();
        this.setupScrollSpy();
        this.setupAnimations();
        this.loadSearchData();
    }

    // Theme Management
    setupTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const body = document.body;
        
        // Apply saved theme
        body.setAttribute('data-theme', this.currentTheme);
        this.updateThemeIcon();

        // Theme toggle handler
        themeToggle?.addEventListener('click', () => {
            this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
            body.setAttribute('data-theme', this.currentTheme);
            localStorage.setItem('theme', this.currentTheme);
            this.updateThemeIcon();
            
            // Animate theme change
            body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
            setTimeout(() => {
                body.style.transition = '';
            }, 300);
        });
    }

    updateThemeIcon() {
        const icon = document.querySelector('#theme-toggle i');
        if (icon) {
            icon.className = this.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }

    // Navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');
        const currentPage = window.location.pathname.split('/').pop() || 'index.html';

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === currentPage) {
                link.classList.add('active');
            }

            link.addEventListener('click', (e) => {
                // Add loading animation
                link.style.opacity = '0.7';
                setTimeout(() => {
                    link.style.opacity = '';
                }, 200);
            });
        });
    }

    // Mobile Navigation
    setupMobileMenu() {
        const mobileToggle = document.getElementById('mobile-nav-toggle');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');

        mobileToggle?.addEventListener('click', () => {
            sidebar?.classList.toggle('open');
            
            // Close menu when clicking outside
            if (sidebar?.classList.contains('open')) {
                const closeMenu = (e) => {
                    if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
                        sidebar.classList.remove('open');
                        document.removeEventListener('click', closeMenu);
                    }
                };
                
                setTimeout(() => {
                    document.addEventListener('click', closeMenu);
                }, 100);
            }
        });

        // Close mobile menu on window resize if desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth > 1024) {
                sidebar?.classList.remove('open');
            }
        });
    }

    // Search Functionality
    setupSearch() {
        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');
        let searchTimeout;

        searchInput?.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim().toLowerCase();

            searchTimeout = setTimeout(() => {
                if (query.length < 2) {
                    this.hideSearchResults();
                    return;
                }

                const results = this.performSearch(query);
                this.displaySearchResults(results);
            }, 300);
        });

        // Hide search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput?.contains(e.target) && !searchResults?.contains(e.target)) {
                this.hideSearchResults();
            }
        });

        // Handle search result clicks
        searchResults?.addEventListener('click', (e) => {
            const resultItem = e.target.closest('.search-result-item');
            if (resultItem) {
                const href = resultItem.dataset.href;
                if (href) {
                    window.location.href = href;
                }
            }
        });
    }

    performSearch(query) {
        if (!this.searchData.length) return [];

        return this.searchData.filter(item => {
            return item.title.toLowerCase().includes(query) ||
                   item.content.toLowerCase().includes(query) ||
                   item.tags?.some(tag => tag.toLowerCase().includes(query));
        }).slice(0, 10); // Limit to 10 results
    }

    displaySearchResults(results) {
        const searchResults = document.getElementById('search-results');
        if (!searchResults) return;

        if (results.length === 0) {
            searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
        } else {
            searchResults.innerHTML = results.map(result => `
                <div class="search-result-item" data-href="${result.href}">
                    <div class="search-result-title">${this.highlightQuery(result.title)}</div>
                    <div class="search-result-snippet">${this.highlightQuery(result.snippet)}</div>
                </div>
            `).join('');
        }

        searchResults.style.display = 'block';
        searchResults.classList.add('fade-in');
    }

    hideSearchResults() {
        const searchResults = document.getElementById('search-results');
        if (searchResults) {
            searchResults.style.display = 'none';
            searchResults.classList.remove('fade-in');
        }
    }

    highlightQuery(text) {
        const query = document.getElementById('search-input')?.value.trim();
        if (!query) return text;

        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    // Load search data (would be populated by the documentation generator)
    async loadSearchData() {
        try {
            // This would typically load from a search index file
            this.searchData = [
                {
                    title: 'Home',
                    href: 'index.html',
                    content: 'Overview and introduction to the system',
                    snippet: 'Main documentation page with system overview',
                    tags: ['home', 'overview', 'introduction']
                },
                {
                    title: 'Architecture',
                    href: 'architecture.html',
                    content: 'System architecture and component relationships',
                    snippet: 'Detailed architecture documentation and diagrams',
                    tags: ['architecture', 'system', 'components', 'design']
                },
                {
                    title: 'API Reference',
                    href: 'api.html',
                    content: 'API endpoints and usage documentation',
                    snippet: 'Complete API reference with examples',
                    tags: ['api', 'endpoints', 'reference', 'examples']
                },
                {
                    title: 'AI Models',
                    href: 'ai_models.html',
                    content: 'Machine learning models and AI components',
                    snippet: 'Documentation of AI models and ML pipelines',
                    tags: ['ai', 'models', 'machine learning', 'ml']
                },
                {
                    title: 'AI Pipelines',
                    href: 'ai_pipelines.html',
                    content: 'AI pipeline documentation and workflows',
                    snippet: 'AI processing pipelines and data flows',
                    tags: ['pipelines', 'ai', 'workflow', 'processing']
                },
                {
                    title: 'Onboarding',
                    href: 'onboarding.html',
                    content: 'Getting started guide and setup instructions',
                    snippet: 'Setup guide for new developers',
                    tags: ['onboarding', 'setup', 'getting started', 'guide']
                },
                {
                    title: 'Code Quality',
                    href: 'complexity.html',
                    content: 'Code quality metrics and complexity analysis',
                    snippet: 'Code quality report and metrics',
                    tags: ['quality', 'complexity', 'metrics', 'analysis']
                }
            ];
        } catch (error) {
            console.warn('Could not load search data:', error);
        }
    }

    // Scroll Spy for table of contents
    setupScrollSpy() {
        const headers = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const tocLinks = document.querySelectorAll('.toc a');
        
        if (!headers.length) return;

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    tocLinks.forEach(link => {
                        link.classList.remove('active');
                        if (link.getAttribute('href') === `#${id}`) {
                            link.classList.add('active');
                        }
                    });
                }
            });
        }, {
            rootMargin: '-50px 0px -50px 0px',
            threshold: 0.5
        });

        headers.forEach(header => {
            if (header.id) {
                observer.observe(header);
            }
        });
    }

    // Animation setup
    setupAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, observerOptions);

        // Observe elements that should animate in
        const animateElements = document.querySelectorAll('.card, h2, h3, table, pre');
        animateElements.forEach(el => {
            observer.observe(el);
        });
    }

    // Utility methods
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Generate table of contents
    generateTOC() {
        const headers = document.querySelectorAll('h2, h3, h4');
        const tocContainer = document.querySelector('.table-of-contents');
        
        if (!tocContainer || !headers.length) return;

        const tocHTML = Array.from(headers).map(header => {
            const id = header.id || this.generateId(header.textContent);
            header.id = id;
            
            const level = parseInt(header.tagName.charAt(1));
            const indent = '  '.repeat(level - 2);
            
            return `${indent}<li><a href="#${id}" class="toc-link">${header.textContent}</a></li>`;
        }).join('\n');

        tocContainer.innerHTML = `<ul class="toc-list">\n${tocHTML}\n</ul>`;
    }

    generateId(text) {
        return text.toLowerCase()
                  .replace(/[^\w\s-]/g, '')
                  .replace(/\s+/g, '-')
                  .trim();
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.docApp = new DocumentationApp();
    
    // Generate table of contents if container exists
    window.docApp.generateTOC();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('search-input');
        searchInput?.focus();
    }
    
    // Escape to close search
    if (e.key === 'Escape') {
        const searchResults = document.getElementById('search-results');
        if (searchResults?.style.display === 'block') {
            window.docApp.hideSearchResults();
            document.getElementById('search-input')?.blur();
        }
    }
});

// Copy code functionality
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('copy-code')) {
        const codeBlock = e.target.nextElementSibling?.querySelector('code');
        if (codeBlock) {
            navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                e.target.textContent = 'Copied!';
                setTimeout(() => {
                    e.target.textContent = 'Copy';
                }, 2000);
            });
        }
    }
});

// Print functionality
window.addEventListener('beforeprint', () => {
    document.body.classList.add('printing');
});

window.addEventListener('afterprint', () => {
    document.body.classList.remove('printing');
});

// Export for use in other scripts
window.DocumentationApp = DocumentationApp;
