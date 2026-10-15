AOS.init({ duration: 900, once: true, offset: 70 });

// ── Navbar: add .scrolled class after 60px scroll ──
(function () {
  const nav = document.querySelector('.main-nav');
  if (!nav) return;
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 60);
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // ── Active nav link highlight ──
  const links = document.querySelectorAll('.main-nav .nav-link');
  const path = window.location.pathname;
  links.forEach(link => {
    if (link.getAttribute('href') === path) link.classList.add('active');
  });
})();




// ── Submenu hover with delay (prevents accidental close on mouse movement) ──
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.dropdown-submenu').forEach(function (item) {
    var submenu = item.querySelector('.submenu-dropdown');
    var timer;

    item.addEventListener('mouseenter', function () {
      clearTimeout(timer);
      if (submenu) submenu.style.display = 'block';
    });

    item.addEventListener('mouseleave', function () {
      timer = setTimeout(function () {
        if (submenu) submenu.style.display = '';
      }, 120);
    });

    if (submenu) {
      submenu.addEventListener('mouseenter', function () {
        clearTimeout(timer);
      });
      submenu.addEventListener('mouseleave', function () {
        timer = setTimeout(function () {
          submenu.style.display = '';
        }, 120);
      });
    }
  });
});



const swiperEl = document.querySelector('.testimonialSwiper');
if (swiperEl) {
  new Swiper('.testimonialSwiper', {
    loop: true,
    spaceBetween: 24,
    autoplay: { delay: 3500 },
    pagination: { el: '.swiper-pagination', clickable: true },
    breakpoints: {
      0: { slidesPerView: 1 },
      768: { slidesPerView: 2 },
      1200: { slidesPerView: 3 }
    }




  });


}
function toggleServiceOptions(id) {
    const allOptions = document.querySelectorAll('.service-suboptions');

    allOptions.forEach(option => {
        if (option.id !== id) {
            option.classList.remove('active');
        }
    });

    const selected = document.getElementById(id);
    selected.classList.toggle('active');
}