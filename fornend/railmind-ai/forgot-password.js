/* RailMind AI — forgot-password page script */
        document.addEventListener('DOMContentLoaded', () => {
            const form = document.getElementById('reset-form');
            const formContainer = document.getElementById('form-container');
            const successState = document.getElementById('success-state');

            const errEl = document.getElementById('reset-error');
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                errEl.classList.add('hidden');
                const check = RailMindAuth.resetPassword(document.getElementById('email').value);
                if (!check.ok) { errEl.textContent = check.error; errEl.classList.remove('hidden'); return; }
                
                // Button loading simulation
                const btn = form.querySelector('button[type="submit"]');
                const originalText = btn.innerHTML;
                btn.innerHTML = `<span class="material-symbols-outlined animate-spin text-[20px]">sync</span><span>Processing...</span>`;
                btn.disabled = true;

                // Simulate network request
                setTimeout(() => {
                    formContainer.style.opacity = '0';
                    setTimeout(() => {
                        formContainer.classList.add('hidden');
                        successState.classList.remove('hidden');
                        successState.classList.add('flex');
                        
                        // Small delay to ensure display:flex is applied before fading in
                        setTimeout(() => {
                            successState.style.opacity = '1';
                        }, 50);
                    }, 300);
                }, 1200);
            });
        });
    
