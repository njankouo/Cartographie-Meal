 const btnOpen = document.getElementById('mobile-menu-btn');
    const btnClose = document.getElementById('close-menu');
    const drawer = document.getElementById('mobile-drawer');
    const overlay = document.getElementById('drawer-overlay');

    function openMenu() {
        drawer.classList.add('active');
        document.body.style.overflow = 'hidden'; // Bloque le scroll arrière
    }

    function closeMenu() {
        drawer.classList.remove('active');
        document.body.style.overflow = ''; // Réactive le scroll
    }

    btnOpen.addEventListener('click', openMenu);
    btnClose.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);


document.addEventListener('DOMContentLoaded', () => {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const toggle = item.querySelector('.faq-toggle');
        const content = item.querySelector('.faq-content');
        const chevron = item.querySelector('.chevron');

        toggle.addEventListener('click', () => {
            const isOpen = item.getAttribute('data-state') === 'open';

            // Fermer tous les autres items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.setAttribute('data-state', 'closed');
                    otherItem.querySelector('.faq-content').style.maxHeight = '0';
                    otherItem.querySelector('.chevron').style.transform = 'rotate(0deg)';
                }
            });

            // Basculer l'item actuel
            if (isOpen) {
                item.setAttribute('data-state', 'closed');
                content.style.maxHeight = '0';
                chevron.style.transform = 'rotate(0deg)';
            } else {
                item.setAttribute('data-state', 'open');
                content.style.maxHeight = content.scrollHeight + 'px';
                chevron.style.transform = 'rotate(180deg)';
            }
        });
    });
});



function mealCarousel(slidesCount) {

return {

current: 0,

slidesCount: Math.max(1, slidesCount || 1),

interval: null,

progress: 0,

progressInterval: null,

init() {

this.$nextTick(() => {

if (this.slidesCount > 1) {

this.startAutoplay();

}

});

},

next() {

this.current = (this.current + 1) % this.slidesCount;

this.resetAutoplay();

},

prev() {

this.current = this.current === 0 ? this.slidesCount - 1 : this.current - 1;

this.resetAutoplay();

},

goTo(index) {

this.current = index;

this.resetAutoplay();

},

startAutoplay() {

this.interval = setInterval(() => {

this.next();

}, 8000);

// Progress bar

this.progressInterval = setInterval(() => {

this.progress += 1;

if (this.progress >= 100) {

this.progress = 0;

}

}, 80);

},

pause() {

clearInterval(this.interval);

clearInterval(this.progressInterval);

},

resume() {

this.resetAutoplay();

},

resetAutoplay() {

this.pause();

this.progress = 0;

setTimeout(() => {

if (this.slidesCount > 1) {

this.startAutoplay();

}

}, 3000);

}

}

}


const cursor = document.querySelector('#custom-cursor');
const cursorOutline = document.querySelector('#custom-cursor-outline');

window.addEventListener('mousemove', (e) => {
    const posX = e.clientX;
    const posY = e.clientY;

    // Le point central suit exactement la souris
    cursor.style.transform = `translate(${posX - 4}px, ${posY - 4}px)`;
    
    // L'anneau suit avec un léger décalage (grâce à la transition CSS)
    cursorOutline.style.transform = `translate(${posX - 20}px, ${posY - 20}px)`;
});

// Effet au survol des liens et boutons
document.querySelectorAll('a, button').forEach(link => {
    link.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-hover');
        cursorOutline.classList.add('cursor-hover');
    });
    link.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-hover');
        cursorOutline.classList.remove('cursor-hover');
    });
});


// 1. Gestion du Menu Mobile
        document.addEventListener('DOMContentLoaded', () => {
            const btn = document.getElementById('mobile-menu-btn');
            const menu = document.getElementById('mobile-menu');
            const icon = btn.querySelector('i');

            btn.addEventListener('click', () => {
                menu.classList.toggle('active');
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            });
            
            // Fermer si clic sur un lien
            menu.querySelectorAll('a').forEach(l => l.addEventListener('click', () => {
                menu.classList.remove('active');
                icon.className = 'fas fa-bars text-2xl text-gray-700';
            }));
        });

        // 2. Logique du Carrousel (Alpine.js helper)
        function mealCarousel(slidesCount) {
            return {
                current: 0,
                slidesCount: slidesCount,
                interval: null,
                init() {
                    if (this.slidesCount > 1) this.startAutoplay();
                },
                next() {
                    this.current = (this.current + 1) % this.slidesCount;
                },
                prev() {
                    this.current = this.current === 0 ? this.slidesCount - 1 : this.current - 1;
                },
                startAutoplay() {
                    this.interval = setInterval(() => this.next(), 6000);
                },
                pause() { clearInterval(this.interval); },
                resume() { this.startAutoplay(); }
            }
        }

document.getElementById('mobile-menu-btn').addEventListener('click', () => {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('-translate-y-full');
    menu.classList.toggle('opacity-100');
    menu.classList.toggle('visible');
});

// Effet scroll navbar
window.addEventListener('scroll', () => {
    const nav = document.querySelector('nav');
    if (window.scrollY > 100) {
        nav.classList.add('shadow-2xl', 'py-3');
    } else {
        nav.classList.remove('shadow-2xl', 'py-3');
    }
});


 window.onscroll = function() {
        let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        let scrolled = (winScroll / height) * 100;
        document.getElementById("progress-bar").style.width = scrolled + "%";
    };