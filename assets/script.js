/**
 * 韮崎工業高校 太鼓部 非公式ポータルサイト
 * 共通スクリプト
 * - アクセシブルなモバイルメニュー（Esc, 外側クリック, リサイズ, フォーカス管理）
 * - 遅延YouTube iframe生成（クリック時再生, キーボード操作対応, 外部通信ゼロ初期状態）
 */

document.addEventListener('DOMContentLoaded', () => {
  /* --------------------------------------------------------------------------
     1. モバイルナビゲーション
     -------------------------------------------------------------------------- */
  const menuToggle = document.querySelector('.menu-toggle');
  const mainNav = document.querySelector('#primary-nav');

  if (menuToggle && mainNav) {
    const setMenuOpen = (open) => {
      const isExpanded = open !== undefined ? open : menuToggle.getAttribute('aria-expanded') !== 'true';
      menuToggle.setAttribute('aria-expanded', String(isExpanded));
      menuToggle.setAttribute('aria-label', isExpanded ? 'メニューを閉じる' : 'メニューを開く');
      mainNav.classList.toggle('is-open', isExpanded);

      if (isExpanded) {
        document.body.style.overflow = 'hidden';
        // メニュー内の最初のフォーカス可能要素にフォーカス
        const firstFocusable = mainNav.querySelector('a, button');
        if (firstFocusable) {
          firstFocusable.focus();
        }
      } else {
        document.body.style.overflow = '';
      }
    };

    menuToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      setMenuOpen();
    });

    // リンククリック時に閉じる
    mainNav.querySelectorAll('.nav-link').forEach((link) => {
      link.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
          setMenuOpen(false);
        }
      });
    });

    // 外側クリックで閉じる
    document.addEventListener('click', (e) => {
      if (mainNav.classList.contains('is-open') && !mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
        setMenuOpen(false);
        menuToggle.focus();
      }
    });

    // Escキーで閉じてボタンへフォーカス復帰
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && mainNav.classList.contains('is-open')) {
        setMenuOpen(false);
        menuToggle.focus();
      }
    });

    // 画面幅が768pxを超えたら閉じる
    window.addEventListener('resize', () => {
      if (window.innerWidth > 768 && mainNav.classList.contains('is-open')) {
        setMenuOpen(false);
      }
    });
  }

  /* --------------------------------------------------------------------------
     2. YouTube遅延プレイヤー
     初期通信0、明示クリック/Enterキーでiframeを生成して再生
     -------------------------------------------------------------------------- */
  const lazyPlayers = document.querySelectorAll('.yt-lazy-player');

  lazyPlayers.forEach((player) => {
    const videoId = player.getAttribute('data-video-id');
    const videoTitle = player.getAttribute('data-video-title') || '和太鼓演奏動画';
    if (!videoId) return;

    const activatePlayer = () => {
      if (player.querySelector('iframe')) return; // 既に生成済みなら無視

      const iframe = document.createElement('iframe');
      iframe.setAttribute('src', `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`);
      iframe.setAttribute('title', videoTitle);
      iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share');
      iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
      iframe.setAttribute('allowfullscreen', 'true');
      
      // サムネイルとボタンを非表示・置換
      player.innerHTML = '';
      player.removeAttribute('role');
      player.removeAttribute('tabindex');
      player.removeAttribute('aria-label');
      player.appendChild(iframe);
      iframe.focus();
    };

    player.addEventListener('click', activatePlayer);
    
    // キーボード Enter / Space 対応
    player.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        activatePlayer();
      }
    });
  });

  /* --------------------------------------------------------------------------
     3. 外部リンクのセキュリティ担保
     -------------------------------------------------------------------------- */
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

  /* --------------------------------------------------------------------------
     4. ヒーロースライダー（写真自動切替・手動切替）
     -------------------------------------------------------------------------- */
  const heroSlider = document.getElementById('hero-slider');
  if (heroSlider) {
    const slides = heroSlider.querySelectorAll('.hero-slide');
    const dots = heroSlider.querySelectorAll('.hero-slider-dot');
    const slideCount = slides.length;
    let currentIndex = 0;
    let slideTimer = null;
    const intervalMs = 5000;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const goToSlide = (nextIndex) => {
      if (nextIndex < 0) {
        nextIndex = slideCount - 1;
      } else if (nextIndex >= slideCount) {
        nextIndex = 0;
      }

      slides.forEach((slide, i) => {
        const isActive = i === nextIndex;
        slide.classList.toggle('is-active', isActive);
        if (isActive) {
          slide.removeAttribute('aria-hidden');
        } else {
          slide.setAttribute('aria-hidden', 'true');
        }
      });

      dots.forEach((dot, i) => {
        const isActive = i === nextIndex;
        dot.classList.toggle('is-active', isActive);
        dot.setAttribute('aria-current', isActive ? 'true' : 'false');
      });

      currentIndex = nextIndex;
    };

    const startAutoPlay = () => {
      if (prefersReducedMotion || slideCount <= 1) return;
      stopAutoPlay();
      slideTimer = setInterval(() => {
        goToSlide(currentIndex + 1);
      }, intervalMs);
    };

    const stopAutoPlay = () => {
      if (slideTimer) {
        clearInterval(slideTimer);
        slideTimer = null;
      }
    };

    // 初期ARIA属性設定
    slides.forEach((slide, i) => {
      if (i !== 0) slide.setAttribute('aria-hidden', 'true');
    });
    dots.forEach((dot, i) => {
      dot.setAttribute('aria-current', i === 0 ? 'true' : 'false');
      dot.addEventListener('click', () => {
        goToSlide(i);
        startAutoPlay(); // クリック後にタイマーリセット
      });
    });

    // キーボード左右矢印でスライド切替（フォーカス時）
    heroSlider.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') {
        goToSlide(currentIndex + 1);
        startAutoPlay();
      } else if (e.key === 'ArrowLeft') {
        goToSlide(currentIndex - 1);
        startAutoPlay();
      }
    });

    // ホバーまたはフォーカス中は自動切替を一時停止
    heroSlider.addEventListener('mouseenter', stopAutoPlay);
    heroSlider.addEventListener('mouseleave', startAutoPlay);
    heroSlider.addEventListener('focusin', stopAutoPlay);
    heroSlider.addEventListener('focusout', startAutoPlay);

    // タブがバックグラウンドのときは一時停止
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        stopAutoPlay();
      } else {
        startAutoPlay();
      }
    });

    // 自動切替開始
    startAutoPlay();
  }
});
