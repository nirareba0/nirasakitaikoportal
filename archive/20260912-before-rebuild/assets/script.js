/**
 * 韮崎工業高校 太鼓部 非公式ポータルサイト
 * 共通スクリプト
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. モバイルナビゲーション（ハンバーガーメニュー）
  const menuToggle = document.querySelector('.menu-toggle');
  const mainNavList = document.querySelector('.nav-list');

  if (menuToggle && mainNavList) {
    const toggleMenu = (open) => {
      const isExpanded = open !== undefined ? open : menuToggle.getAttribute('aria-expanded') !== 'true';
      menuToggle.setAttribute('aria-expanded', String(isExpanded));
      mainNavList.classList.toggle('is-open', isExpanded);
      if (isExpanded) {
        document.body.style.overflow = 'hidden'; // 背面スクロール抑止
      } else {
        document.body.style.overflow = '';
      }
    };

    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleMenu();
    });

    // メニュー内のリンクをクリックしたら閉じる
    mainNavList.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          toggleMenu(false);
        }
      });
    });

    // 外側クリックで閉じる
    document.addEventListener('click', (e) => {
      if (mainNavList.classList.contains('is-open') && !mainNavList.contains(e.target) && !menuToggle.contains(e.target)) {
        toggleMenu(false);
      }
    });

    // ESCキーで閉じる
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mainNavList.classList.contains('is-open')) {
        toggleMenu(false);
        menuToggle.focus();
      }
    });

    // リサイズ時にスマホ幅を超えたらリセット
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768 && mainNavList.classList.contains('is-open')) {
        toggleMenu(false);
      }
    });
  }

  // 2. 現在アクティブなページのナビゲーションリンクハイライト
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');
  
  navLinks.forEach((link) => {
    const href = link.getAttribute('href');
    if (!href) return;
    
    // index.html または ルート判定
    const isIndex = (href === 'index.html' || href === './') && 
                    (currentPath.endsWith('/') || currentPath.endsWith('/index.html') || currentPath === '');
    const isCurrent = currentPath.endsWith(href);

    if (isIndex || isCurrent) {
      link.classList.add('active');
      link.setAttribute('aria-current', 'page');
    }
  });

  // 3. 外部リンクのセキュリティ・利便性担保 (target="_blank", rel="noopener noreferrer")
  const externalLinks = document.querySelectorAll('a[href^="http"]');
  externalLinks.forEach((link) => {
    if (!link.hasAttribute('target')) {
      link.setAttribute('target', '_blank');
    }
    const rel = link.getAttribute('rel') || '';
    if (!rel.includes('noopener')) {
      link.setAttribute('rel', `${rel} noopener noreferrer`.trim());
    }
  });
});
