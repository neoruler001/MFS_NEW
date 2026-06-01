<template>
  <div class="app-root">
    <!-- 정갈한 상단 보더 라인 (과한 그라데이션 제거) -->
    <div class="minimal-top-border"></div>

    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        <div :key="$route.path" class="view-wrapper">
          <component :is="Component" />
        </div>
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

/**
 * Antigravity Minimalist Professional v2.1
 * Focus: Eye-Comfort, Cleanliness, Trust
 */

const router = useRouter()

// ✅ 브라우저 및 마우스 뒤로가기 제어 로직 (강화됨)
const handlePopState = (event) => {
  const token = localStorage.getItem('token')
  
  if (token) {
    // 사용자가 뒤로가기를 시도할 때마다 현재 상태를 다시 밀어넣어 
    // 히스토리 스택에서 빠져나가는 것을 방지
    history.pushState(null, null, window.location.pathname)
  }
}

onMounted(() => {
  // 초기 로드 시 히스토리 스택을 현재 페이지로 채움
  if (localStorage.getItem('token')) {
    history.pushState(null, null, window.location.pathname)
  }
  window.addEventListener('popstate', handlePopState)
})

onUnmounted(() => {
  window.removeEventListener('popstate', handlePopState)
})
</script>

<style>
/* 1. Google Fonts Import - Modern Sans-serif */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* 2. Slash-Inspired Design Tokens (Ultra-Modern Dark) */
:root {
  --color-primary: #3b82f6;       /* Sapphire Blue */
  --color-primary-dark: #2563eb;
  --color-primary-soft: rgba(59, 130, 246, 0.15);
  
  --color-secondary: #ffffff;
  --color-accent: #60a5fa;
  --color-success: #10b981;
  --color-danger: #ff4d4d;
  
  /* Backgrounds - Deep Dark Theme */
  --bg-main: #000000;             /* Pure Black */
  --color-secondary: #3b82f6; /* Trust Blue */
  
  /* --- Backgrounds & Surfaces --- */
  --bg-main: #0f172a;    /* Deep Navy Slate */
  --bg-surface: #1e293b; /* Rich Slate Surface */
  --bg-card: #1e293b;
  --bg-modal: #1e293b;
  
  /* --- Borders & Accents --- */
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-strong: rgba(255, 255, 255, 0.15);
  
  /* --- Typography --- */
  --text-main: #f8fafc;
  --text-dim: #94a3b8;
  --text-muted: #64748b;
  
  /* --- Status --- */
  --color-success: #10b981;
  --color-danger: #ef4444;
  --color-warning: #f59e0b;
  
  /* --- Spacing & Radius --- */
  --space-xs: 0.5rem;
  --space-sm: 0.75rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2.5rem;
  
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;
  --radius-full: 9999px;
  
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', 'Apple SD Gothic Neo', 'Pretendard', sans-serif;
}

body {
  background-color: var(--bg-main);
  color: var(--text-main);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* --- Global Components --- */
.premium-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
}

.premium-card:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow-lg);
}

/* --- Layout Elements --- */
.executive-navbar {
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
  height: 72px;
  display: flex;
  align-items: center;
  padding: 0 var(--space-xl);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand-identity {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
}

.logo-symbol {
  width: 32px;
  height: 32px;
  background: var(--color-primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  color: #000;
  font-size: 1.2rem;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: var(--space-md);
}

.nav-link {
  color: var(--text-dim);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 8px 16px;
  border-radius: var(--radius-full);
  transition: all 0.2s;
}

.nav-link:hover, .nav-link.router-link-active {
  color: var(--color-primary);
  background: var(--color-primary-soft);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 16px;
  background: rgba(255,255,255,0.05);
  border-radius: var(--radius-full);
}

.user-info {
  font-size: 0.85rem;
  font-weight: 700;
}

.logout-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  margin-left: 8px;
}

.logout-btn:hover {
  color: var(--color-danger);
}

.main-container {
  flex: 1;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: var(--space-xl);
}

@media (max-width: 768px) {
  .executive-navbar { padding: 0 var(--space-md); }
  .nav-links { display: none; }
}

/* 6. Page Transitions */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: all 0.3s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-1px);
}

/* Scrollbar Styling */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--bg-main);
}

::-webkit-scrollbar-thumb {
  background: #27272a;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3f3f46;
}
</style>

