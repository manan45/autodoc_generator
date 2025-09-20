/* data-integration.js - Repository data integration with vector embeddings */

/**
 * Repository Data Manager
 * Handles integration with repository code using vector embeddings
 */
const RepositoryDataManager = (() => {
    let repositoryData = {};
    let vectorIndex = null;
    let codeModules = [];
    
    const init = async () => {
        try {
            await loadRepositoryData();
            await buildVectorIndex();
            bindModuleInteractions();
            console.log('📊 Repository data integration initialized');
        } catch (error) {
            console.warn('Repository data integration failed:', error);
        }
    };
    
    const loadRepositoryData = async () => {
        try {
            // Try to load repository analysis data
            const response = await fetch('/api/repository-data');
            if (response.ok) {
                repositoryData = await response.json();
                console.log('📁 Repository data loaded:', repositoryData.modules.length, 'modules');
                console.log('📊 Stats:', {
                    files: repositoryData.totalFiles,
                    functions: repositoryData.totalFunctions,
                    classes: repositoryData.totalClasses
                });
                
                // Update UI stats
                updateRepositoryStats(repositoryData);
            } else {
                // Fallback to static data or generate from current page
                repositoryData = generateFallbackData();
                console.log('📁 Using fallback data:', repositoryData.modules.length, 'modules');
            }
        } catch (error) {
            console.warn('Failed to load repository data, using fallback:', error);
            repositoryData = generateFallbackData();
        }
    };
    
    const generateFallbackData = () => {
        // Extract data from current page elements
        const modules = [];
        const moduleCards = document.querySelectorAll('.module-card, .getting-started-card');
        
        moduleCards.forEach((card, index) => {
            const title = card.querySelector('h3, h4, .card__title')?.textContent?.trim();
            const description = card.querySelector('p, .card__description')?.textContent?.trim();
            const stats = extractStatsFromCard(card);
            
            if (title) {
                modules.push({
                    id: `module-${index}`,
                    name: title,
                    description: description || '',
                    path: generateModulePath(title),
                    stats: stats,
                    type: inferModuleType(title, description),
                    complexity: calculateComplexity(stats),
                    embedding: generateSimpleEmbedding(title + ' ' + description)
                });
            }
        });
        
        return {
            modules: modules,
            totalFiles: modules.length,
            totalFunctions: modules.reduce((sum, m) => sum + (m.stats.functions || 0), 0),
            totalClasses: modules.reduce((sum, m) => sum + (m.stats.classes || 0), 0),
            lastUpdated: new Date().toISOString()
        };
    };
    
    const extractStatsFromCard = (card) => {
        const stats = {};
        const statElements = card.querySelectorAll('.stat-value, .metric-value, .md-nav__stats-number');
        const statLabels = card.querySelectorAll('.stat-name, .metric-label, .md-nav__stats-label');
        
        statElements.forEach((element, index) => {
            const value = parseInt(element.textContent) || 0;
            const label = statLabels[index]?.textContent?.toLowerCase() || `metric${index}`;
            stats[label] = value;
        });
        
        return stats;
    };
    
    const generateModulePath = (title) => {
        return title.toLowerCase()
            .replace(/[^a-z0-9\s]/g, '')
            .replace(/\s+/g, '_')
            .replace(/^_+|_+$/g, '');
    };
    
    const inferModuleType = (title, description) => {
        const text = (title + ' ' + description).toLowerCase();
        // AI oriented labels
        if (/(embedding|vector store|faiss|milvus|ann index)/.test(text)) return 'embedding';
        if (/(model|llm|classifier|regression|transformer|bert|gpt|xgboost|sklearn)/.test(text)) return 'model';
        if (/(interface|protocol|adapter|port|contract)/.test(text)) return 'interface';
        if (/(schema|entity|dataclass|pydantic|orm|dto)/.test(text)) return 'class';
        // App domains
        if (text.includes('api') || text.includes('endpoint')) return 'api';
        if (text.includes('pipeline') || text.includes('workflow')) return 'pipeline';
        if (text.includes('component') || text.includes('ui')) return 'component';
        if (text.includes('util') || text.includes('helper')) return 'utility';
        if (text.includes('service') || text.includes('manager')) return 'service';
        if (text.includes('test') || text.includes('spec')) return 'test';
        return 'module';
    };
    
    const calculateComplexity = (stats) => {
        const totalItems = (stats.functions || 0) + (stats.classes || 0) + (stats.lines || 0) / 100;
        
        if (totalItems > 50) return 'high';
        if (totalItems > 20) return 'medium';
        return 'low';
    };
    
    const generateSimpleEmbedding = (text) => {
        // Simple text-to-vector embedding (in production, use proper embeddings)
        const words = text.toLowerCase().split(/\W+/).filter(w => w.length > 2);
        const embedding = new Array(50).fill(0);
        
        words.forEach((word, index) => {
            const hash = simpleHash(word);
            embedding[hash % 50] += 1 / (index + 1);
        });
        
        // Normalize
        const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
        return embedding.map(val => magnitude > 0 ? val / magnitude : 0);
    };
    
    const simpleHash = (str) => {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    };
    
    const buildVectorIndex = async () => {
        if (!repositoryData.modules) return;
        
        // Create a simple vector index for similarity search
        vectorIndex = {
            modules: repositoryData.modules,
            search: (query, limit = 5) => {
                const queryEmbedding = generateSimpleEmbedding(query);
                const similarities = repositoryData.modules.map(module => ({
                    module,
                    similarity: cosineSimilarity(queryEmbedding, module.embedding)
                }));
                
                return similarities
                    .sort((a, b) => b.similarity - a.similarity)
                    .slice(0, limit)
                    .map(item => item.module);
            }
        };
        
        console.log('🔍 Vector index built with', repositoryData.modules.length, 'modules');
    };
    
    const cosineSimilarity = (vecA, vecB) => {
        if (vecA.length !== vecB.length) return 0;
        
        let dotProduct = 0;
        let normA = 0;
        let normB = 0;
        
        for (let i = 0; i < vecA.length; i++) {
            dotProduct += vecA[i] * vecB[i];
            normA += vecA[i] * vecA[i];
            normB += vecB[i] * vecB[i];
        }
        
        const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
        return magnitude > 0 ? dotProduct / magnitude : 0;
    };
    
    const bindModuleInteractions = () => {
        // Enhance module cards with repository data
        const moduleCards = document.querySelectorAll('.module-card, .getting-started-card');
        
        // If we have real repository data, replace the cards with actual modules
        if (repositoryData.modules && repositoryData.modules.length > 0) {
            replaceModuleCards(repositoryData.modules);
        } else {
            // Enhance existing cards with available data
            moduleCards.forEach((card, index) => {
                const module = repositoryData.modules?.[index];
                if (module) {
                    enhanceModuleCard(card, module);
                }
            });
        }
        
        // Add click handlers for navigation to code
        document.addEventListener('click', (e) => {
            const moduleLink = e.target.closest('[data-module-path]');
            if (moduleLink) {
                e.preventDefault();
                navigateToModule(moduleLink.dataset.modulePath);
            }
        });
    };
    
    const replaceModuleCards = (modules) => {
        const modulesContainer = document.querySelector('.stats-grid, .module-grid, .getting-started-grid');
        if (!modulesContainer) return;
        
        // Clear existing cards
        modulesContainer.innerHTML = '';
        
        // Create new cards from repository data
        modules
            .filter(m => (m.description || '').trim().length > 0)
            .slice(0, 12)
            .forEach(module => {
                const card = createModuleCard(module);
                modulesContainer.appendChild(card);
            });
        
        console.log(`🔄 Replaced module cards with ${modules.length} real modules`);
    };
    
    const createModuleCard = (module) => {
        if (!module || !(module.description || '').trim()) return document.createDocumentFragment();
        const card = document.createElement('div');
        card.className = 'module-card';
        card.setAttribute('data-module-path', module.path);
        card.setAttribute('data-module-type', module.type);
        card.setAttribute('data-complexity', module.complexity);
        
        card.innerHTML = `
            <div class="card-header">
                <h3>${module.name}</h3>
                <div class="complexity-indicator complexity-${module.complexity}">
                    ${module.complexity.toUpperCase()}
                </div>
            </div>
            <div class="card-content">
                <p class="module-description">${module.description}</p>
                <div class="module-path">
                    <code>${module.path}</code>
                </div>
                <div class="module-stats">
                    <div class="stat-item">
                        <span class="stat-value">${module.stats.functions || 0}</span>
                        <span class="stat-label">Functions</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${module.stats.classes || 0}</span>
                        <span class="stat-label">Classes</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-value">${module.stats.lines || 0}</span>
                        <span class="stat-label">Lines</span>
                    </div>
                </div>
            </div>
        `;
        
        // Hover tooltip disabled
        
        return card;
    };
    
    const enhanceModuleCard = (card, module) => {
        // Add module path data attribute
        card.setAttribute('data-module-path', module.path);
        card.setAttribute('data-module-type', module.type);
        card.setAttribute('data-complexity', module.complexity);
        
        // Add complexity indicator
        if (!card.querySelector('.complexity-indicator')) {
            const complexityBadge = document.createElement('div');
            complexityBadge.className = `complexity-indicator complexity-${module.complexity}`;
            complexityBadge.textContent = module.complexity.toUpperCase();
            complexityBadge.title = `Code complexity: ${module.complexity}`;
            
            const header = card.querySelector('h3, h4, .card__title');
            if (header) {
                header.appendChild(complexityBadge);
            }
        }

        // Add module type badge (CLASS/INTERFACE/MODEL/EMBEDDING/etc.)
        if (!card.querySelector('.module-type-badge')) {
            const typeBadge = document.createElement('span');
            typeBadge.className = 'module-type-badge';
            typeBadge.textContent = (module.type || 'module').toUpperCase();
            const header = card.querySelector('h3, h4, .card__title');
            if (header) header.appendChild(typeBadge);
        }
        
        // Add click-to-code functionality
        if (!card.querySelector('.code-link')) {
            const codeLink = document.createElement('a');
            codeLink.className = 'code-link';
            codeLink.href = '#';
            codeLink.setAttribute('data-module-path', module.path);
            // codeLink.innerHTML = '📁 View Code';
            // codeLink.title = `Navigate to ${module.name} source code`;
            
            card.appendChild(codeLink);
        }
        
        // Hover tooltip disabled
    };
    
    const showModuleTooltip = () => {};
    const hideModuleTooltip = () => {};
    
    const navigateToModule = (modulePath) => {
        // In a real implementation, this would open the code in an IDE or code viewer
        console.log('🔍 Navigating to module:', modulePath);
        
        // For now, show a modal with module information
        showModuleModal(modulePath);
    };
    
    const showModuleModal = (modulePath) => {
        const module = repositoryData.modules?.find(m => m.path === modulePath);
        if (!module) return;
        
        const modal = document.createElement('div');
        modal.className = 'module-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${module.name}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="module-info">
                        <p><strong>Type:</strong> ${module.type}</p>
                        <p><strong>Path:</strong> ${module.path}</p>
                        <p><strong>Complexity:</strong> ${module.complexity}</p>
                        <p><strong>Description:</strong> ${module.description}</p>
                    </div>
                    <div class="module-stats">
                        <h4>Statistics</h4>
                        ${Object.entries(module.stats).map(([key, value]) => 
                            `<div class="stat-row">
                                <span class="stat-label">${key}:</span>
                                <span class="stat-value">${value}</span>
                            </div>`
                        ).join('')}
                    </div>
                    <div class="module-actions">
                        <button class="btn btn--primary" onclick="RepositoryDataManager.openInEditor('${module.path}')">
                            Open in Editor
                        </button>
                        <button class="btn btn--secondary" onclick="RepositoryDataManager.findSimilar('${module.name}')">
                            Find Similar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Bind close handlers
        modal.querySelector('.modal-close').addEventListener('click', () => modal.remove());
        modal.querySelector('.modal-backdrop').addEventListener('click', () => modal.remove());
        
        // ESC key to close
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    };
    
    const openInEditor = (modulePath) => {
        // Integration with Cursor/VS Code
        if (window.vscode) {
            // VS Code extension API
            window.vscode.postMessage({
                command: 'openFile',
                path: modulePath
            });
        } else {
            // Fallback: open in new tab or show file content
            window.open(`/code/${modulePath}`, '_blank');
        }
    };
    
    const findSimilar = (moduleName) => {
        if (!vectorIndex) return;
        
        const similar = vectorIndex.search(moduleName, 5);
        console.log('🔍 Similar modules to', moduleName, ':', similar.map(m => m.name));
        
        // Show similar modules in UI
        showSimilarModules(similar);
    };
    
    const showSimilarModules = (modules) => {
        // Implementation to show similar modules in a sidebar or modal
        console.log('Similar modules:', modules);
    };
    
    const searchModules = (query) => {
        if (!vectorIndex) return [];
        return vectorIndex.search(query);
    };
    
    const getModuleByPath = (path) => {
        return repositoryData.modules?.find(m => m.path === path);
    };
    
    const updateRepositoryStats = (data) => {
        // Update sidebar stats
        const statsElements = document.querySelectorAll('.md-nav__stats-number');
        const statsLabels = document.querySelectorAll('.md-nav__stats-label');
        
        if (statsElements.length >= 3) {
            statsElements[0].textContent = data.totalFiles || 0;
            statsElements[1].textContent = data.totalFunctions || 0;
            statsElements[2].textContent = data.totalClasses || 0;
        }
        
        // Update any stats cards on the page
        const statCards = document.querySelectorAll('.metric-card, .stats-widget .stat-value');
        statCards.forEach(card => {
            const label = card.closest('.metric-card')?.querySelector('.metric-label')?.textContent?.toLowerCase();
            if (label) {
                if (label.includes('file')) card.textContent = data.totalFiles || 0;
                if (label.includes('function')) card.textContent = data.totalFunctions || 0;
                if (label.includes('class')) card.textContent = data.totalClasses || 0;
                if (label.includes('module')) card.textContent = data.modules?.length || 0;
            }
        });
        
        // Remove repository info banner if present (disabled)
        const existingBanner = document.querySelector('.repo-info-banner');
        if (existingBanner) existingBanner.remove();

        // Update page-level stats if present
        const overviewStats = document.querySelector('#overview-stats');
        if (overviewStats) {
            const set = (key, val) => {
                const el = overviewStats.querySelector(`[data-stat="${key}"] .stat-number`);
                if (el) el.textContent = val;
            };
            set('modules', data.modules?.length || 0);
            set('files', data.totalFiles || 0);
            set('functions', data.totalFunctions || 0);
            set('classes', data.totalClasses || 0);
        }

        const modulesStats = document.querySelector('#modules-stats');
        if (modulesStats) {
            const set = (key, val) => {
                const el = modulesStats.querySelector(`[data-stat="${key}"] .stat-number`);
                if (el) el.textContent = val;
            };
            set('modules', data.modules?.length || 0);
            set('functions', data.totalFunctions || 0);
            set('classes', data.totalClasses || 0);
            set('lines', data.totalLines || data.total_lines || 0);
        }

        // Render unique top modules on Overview
        renderOverviewTopModules(data.modules || []);
        // Render components and modules sections on Modules page
        renderComponentsGrid(data.modules || []);
        renderModulesStructure(data.modules || []);

        // API page integration if present
        renderApiPage(data);

        // Update sidebar counts for Modules and Components
        const modulesCountEl = document.getElementById('sidebar-modules-count');
        const componentsCountEl = document.getElementById('sidebar-components-count');
        if (modulesCountEl || componentsCountEl) {
            const modulesList = dedupeModules(data.modules || []).filter(m => !m.path || m.path.split('/').length <= 2);
            const componentsList = dedupeModules(data.modules || []).filter(m => (m.description || '').trim().length > 0);
            if (modulesCountEl) modulesCountEl.textContent = `(${modulesList.length})`;
            if (componentsCountEl) componentsCountEl.textContent = `(${componentsList.length})`;
        }
        // All Modules page
        renderAllModulesPage(data);
    };
    


    const dedupeModules = (modules) => {
        const seen = new Set();
        return modules.filter(m => {
            const key = (m.path || m.name || '').toLowerCase();
            if (!key || seen.has(key)) return false;
            seen.add(key);
            return true;
        });
    };

    const renderOverviewTopModules = (modules) => {
        const container = document.getElementById('overview-modules');
        if (!container) return;
        container.innerHTML = '';
        const unique = dedupeModules(modules)
            .filter(m => (m.description || '').trim().length > 0)
            .slice(0, 6);
        unique.forEach(m => container.appendChild(createModuleCard({
            ...m,
            stats: m.stats || {},
            description: m.description || '',
            complexity: m.complexity || 'low'
        })));
    };

    const renderComponentsGrid = (modules) => {
        const container = document.getElementById('components-grid');
        if (!container) return;
        container.innerHTML = '';
        const items = dedupeModules(modules)
            .filter(m => (m.description || '').trim().length > 0);
        items.forEach(m => container.appendChild(createModuleCard({
            ...m,
            stats: m.stats || {},
            description: m.description || '',
            complexity: m.complexity || 'low'
        })));
    };

    const renderModulesStructure = (modules) => {
        const container = document.getElementById('modules-structure');
        if (!container) return;
        container.innerHTML = '';

        const topLevel = dedupeModules(modules).filter(m => !m.path || m.path.split('/').length <= 2);
        topLevel.slice(0, 20).forEach(m => {
            const card = document.createElement('div');
            card.className = 'getting-started-card';
            card.innerHTML = `
                <div class="card-icon">📁</div>
                <h3>${m.name || 'module'}</h3>
                <div class="code-block"><code>${m.path || ''}</code></div>
                <div class="diagram-section">
                    <div class="mermaid">classDiagram
                    class ${cssSafe(m.name || 'Module')} {
                        ${Array.from(new Set([...(m.classes||[]), ...(m.functions||[])]))
                            .slice(0,8)
                            .map(x => x.toString().split('(')[0])
                            .map(n => `+ ${n}()`)
                            .join('\n                        ')}
                    }
                    </div>
                </div>
                <div class="module-stats">
                    <div class="stat-item"><span class="stat-value">${(m.stats && m.stats.functions) || (m.functions?.length || 0)}</span><span class="stat-label">Functions</span></div>
                    <div class="stat-item"><span class="stat-value">${(m.stats && m.stats.classes) || (m.classes?.length || 0)}</span><span class="stat-label">Classes</span></div>
                    <div class="stat-item"><span class="stat-value">${(m.stats && m.stats.lines) || (m.lines_of_code || 0)}</span><span class="stat-label">Lines</span></div>
                </div>
            `;
            container.appendChild(card);
        });

        // Initialize Mermaid if present
        if (window.mermaid) {
            try { window.mermaid.init(undefined, container.querySelectorAll('.mermaid')); } catch(e) {}
        }
    };

    const cssSafe = (name) => name.replace(/[^a-zA-Z0-9_]/g, '_');

    const renderApiPage = (data) => {
        const apiStats = document.getElementById('api-stats');
        if (apiStats) {
            const endpoints = (data.api && data.api.endpoints) || [];
            const interfaces = (data.api && data.api.interfaces) || [];
            const patterns = (data.api && data.api.patterns) || [];
            const apiModules = (data.modules || []).filter(m => /api|endpoint|router/i.test(m.name || m.path || ''));
            const set = (key, val) => {
                const el = apiStats.querySelector(`[data-stat="${key}"] .stat-number`);
                if (el) el.textContent = val;
            };
            set('endpoints', endpoints.length);
            set('interfaces', interfaces.length);
            set('patterns', patterns.length);
            set('modules', apiModules.length);

            // Endpoints root rendering (override static if exists)
            const epRoot = document.getElementById('api-endpoints-root');
            if (epRoot && endpoints.length) {
                epRoot.innerHTML = '';
                const section = document.createElement('section');
                section.className = 'endpoints-section';
                section.id = 'endpoints';
                section.innerHTML = `<h2>🔌 API Endpoints</h2><p>Comprehensive list of available API endpoints and their specifications.</p>`;
                const grid = document.createElement('div');
                grid.className = 'getting-started-grid';
                dedupeModules(endpoints.map(e => ({ path: e.path, name: e.path + (e.method||'GET')})));
                endpoints.slice(0, 12).forEach(e => {
                    const card = document.createElement('div');
                    card.className = 'getting-started-card';
                    const method = (e.method || 'GET').toUpperCase();
                    const icon = method === 'GET' ? '📥' : method === 'POST' ? '📤' : method === 'PUT' ? '✏️' : method === 'DELETE' ? '🗑️' : '🔄';
                    card.innerHTML = `
                        <div class="card-icon">${icon}</div>
                        <h3><span class="http-method http-method--${method.toLowerCase()}">${method}</span></h3>
                        <div class="endpoint-details">
                            <strong>Path:</strong>
                            <div class="code-block"><code>${e.path}</code></div>
                            <p>${e.description || ''}</p>
                            ${e.module ? `<strong>Module:</strong><div class="code-block"><code>${e.module}</code></div>` : ''}
                        </div>`;
                    grid.appendChild(card);
                });
                section.appendChild(grid);
                epRoot.appendChild(section);
            }
        }
    };

    const renderAllModulesPage = (data) => {
        const statsEl = document.getElementById('all-modules-stats');
        const gridEl = document.getElementById('all-modules-grid');
        const searchEl = document.getElementById('all-modules-search');
        const countEl = document.getElementById('all-modules-count');
        if (!statsEl && !gridEl) return;

        const modules = dedupeModules(data.modules || []);
        const totalFunctions = modules.reduce((s, m) => s + (m.stats?.functions || m.functions?.length || 0), 0);
        const totalClasses = modules.reduce((s, m) => s + (m.stats?.classes || m.classes?.length || 0), 0);
        const totalLines = modules.reduce((s, m) => s + (m.stats?.lines || m.lines_of_code || 0), 0);
        const documentedCount = modules.filter(m => (m.description || '').trim().length > 0).length;
        // naive complexity estimate from available stats
        const complexities = modules.map(m => {
            const f = m.stats?.functions || m.functions?.length || 0;
            const c = m.stats?.classes || m.classes?.length || 0;
            const l = m.stats?.lines || m.lines_of_code || 0;
            return f + c * 2 + l / 300;
        });
        const avgComplexity = complexities.length ? (complexities.reduce((a,b)=>a+b,0) / complexities.length) : 0;
        const highComplexity = complexities.filter(x => x > 15).length;

        const set = (key, val) => {
            const el = statsEl?.querySelector(`[data-stat="${key}"] .stat-number`);
            if (el) el.textContent = val;
        };
        set('avgComplexity', avgComplexity.toFixed(1));
        set('highComplexity', highComplexity);
        set('documented', documentedCount);
        set('lines', totalLines);

        const createModuleDetailCard = (m) => {
            const card = document.createElement('div');
            card.className = 'getting-started-card';
            card.setAttribute('data-module-path', m.path || '');
            const classDiagram = createClassDiagram(m);
            const functionsList = (m.functions || []).map(fn => formatFunctionSignature(fn)).slice(0,8).join('<br/>');
            const isArchitecture = (window.location.pathname || '').includes('architecture.html');
            const actionsHtml = isArchitecture ? '' : `
                <div class="card-actions">
                    <a href="#" class="code-link" data-module-path="${m.path || ''}">📁 View Code</a>
                    <button class="btn btn--secondary btn--sm" onclick="RepositoryDataManager.findSimilar('${(m.name||'').replace(/'/g, "\'")}')">🔍 Similar</button>
                </div>`;
            card.innerHTML = `
                <div class="card-icon">📦</div>
                <h3>${m.name || 'module'}</h3>
                <p class="module-description">${(m.description || '').slice(0,200)}</p>
                <div class="code-block"><code>${m.path || ''}</code></div>
                ${classDiagram}
                <div class="module-stats">
                    <div class="stat-item"><span class="stat-value">${m.stats?.functions || m.functions?.length || 0}</span><span class="stat-label">Functions</span></div>
                    <div class="stat-item"><span class="stat-value">${m.stats?.classes || m.classes?.length || 0}</span><span class="stat-label">Classes</span></div>
                    <div class="stat-item"><span class="stat-value">${m.stats?.lines || m.lines_of_code || 0}</span><span class="stat-label">Lines</span></div>
                </div>
                ${functionsList ? `<div class="code-block" style="margin-top:.5rem">${functionsList}</div>` : ''}
                ${actionsHtml}
            `;
            return card;
        };

        const createClassDiagram = (m) => {
            const classNames = (m.classes || []).map(c => typeof c === 'string' ? c : c.name).slice(0,6);
            const methodNames = (m.functions || []).map(f => typeof f === 'string' ? f : f.name).slice(0,6);
            if (!classNames.length && !methodNames.length) return '';
            const mermaid = `classDiagram\n${classNames.map(n => `class ${cssSafe(n)} {}`).join("\n")}\n${methodNames.map(n => `${cssSafe(m.name||'Module')} : + ${n}()`).join("\n")}`;
            return `<div class="diagram-section"><div class="mermaid">${mermaid}</div></div>`;
        };

        const formatFunctionSignature = (fn) => {
            if (!fn) return '';
            if (typeof fn === 'string') return `<code>${fn}()</code>`;
            const name = fn.name || 'func';
            const args = Array.isArray(fn.args) ? fn.args.map(a => a.name || a).join(', ') : (fn.args || 0);
            return `<code>${name}(${args})</code>`;
        };

        const renderGrid = (list) => {
            if (!gridEl) return;
            gridEl.innerHTML = '';
            const density = (document.getElementById('density-select')?.value) || 'normal';
            list.forEach(m => {
                const card = createModuleDetailCard(m);
                card.classList.add(density);
                gridEl.appendChild(card);
            });
            if (countEl) countEl.textContent = `(${list.length})`;
            if (window.mermaid) { try { window.mermaid.init(undefined, gridEl.querySelectorAll('.mermaid')); } catch(e) {} }
        };

        let pageSize = 30;
        let visible = modules.slice(0, pageSize);
        renderGrid(visible);
        const loadMoreBtn = document.getElementById('load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.onclick = () => {
                pageSize += 30;
                visible = modules.slice(0, pageSize);
                renderGrid(visible);
                if (visible.length >= modules.length) loadMoreBtn.style.display = 'none';
            };
            if (visible.length >= modules.length) loadMoreBtn.style.display = 'none';
        }

        if (searchEl) {
            searchEl.addEventListener('input', () => {
                const q = searchEl.value.toLowerCase();
                const filtered = modules.filter(m =>
                    (m.name || '').toLowerCase().includes(q) ||
                    (m.path || '').toLowerCase().includes(q) ||
                    (m.description || '').toLowerCase().includes(q)
                );
                pageSize = 30;
                visible = filtered.slice(0, pageSize);
                renderGrid(visible);
                if (loadMoreBtn) loadMoreBtn.style.display = (visible.length >= filtered.length) ? 'none' : '';
            });
        }

        const densitySelect = document.getElementById('density-select');
        if (densitySelect) {
            densitySelect.addEventListener('change', () => renderGrid(visible));
        }
    };
    
    const getRepositoryStats = () => {
        return {
            totalModules: repositoryData.modules?.length || 0,
            totalFiles: repositoryData.totalFiles || 0,
            totalFunctions: repositoryData.totalFunctions || 0,
            totalClasses: repositoryData.totalClasses || 0,
            lastUpdated: repositoryData.lastUpdated
        };
    };
    
    // Public API
    return {
        init,
        searchModules,
        getModuleByPath,
        getRepositoryStats,
        openInEditor,
        findSimilar,
        navigateToModule
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    RepositoryDataManager.init();
});

// Export for global access
window.RepositoryDataManager = RepositoryDataManager;
