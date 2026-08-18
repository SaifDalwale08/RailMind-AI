/* RailMind AI — index page script */
        // Simple intersection observer for fade-in animations
        document.addEventListener("DOMContentLoaded", () => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.fade-in-up').forEach((el) => {
                observer.observe(el);
            });

            // Smooth scrolling and active state for navbar links
            const navLinks = document.querySelectorAll('.nav-link');
            const sections = document.querySelectorAll('section[id]');
            
            navLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    // Let native smooth scroll handle it due to scroll-behavior: smooth on html
                });
            });

            const navObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const id = entry.target.getAttribute('id');
                        navLinks.forEach(link => {
                            link.classList.remove('text-primary', 'font-semibold', 'border-primary');
                            link.classList.add('text-on-surface-variant', 'font-medium', 'border-transparent');
                            
                            if (link.getAttribute('href') === `#${id}`) {
                                link.classList.remove('text-on-surface-variant', 'font-medium', 'border-transparent');
                                link.classList.add('text-primary', 'font-semibold', 'border-primary');
                            }
                        });
                    }
                });
            }, { rootMargin: '-100px 0px -60% 0px' });

            sections.forEach(section => {
                navObserver.observe(section);
            });
        });
    
