/* RailMind AI — create-account page script */
(function(){
  var form=document.getElementById('signup-form');
  var err=document.getElementById('signup-error');
  var ok=document.getElementById('signup-success');
  form.addEventListener('submit',function(e){
    e.preventDefault();
    err.classList.add('hidden');
    var res=RailMindAuth.register({
      fullName:document.getElementById('fullName').value.trim(),
      email:document.getElementById('email').value.trim(),
      organization:document.getElementById('organization').value.trim(),
      role:document.getElementById('role').value,
      password:document.getElementById('password').value,
      confirmPassword:document.getElementById('confirmPassword').value
    });
    if(!res.ok){err.textContent=res.error;err.classList.remove('hidden');return;}
    ok.classList.remove('hidden');ok.classList.add('flex');
  });
  form.querySelector('button[type="button"]').addEventListener('click',function(){
    err.textContent='Google sign-up is not available yet. Please use the form above.';
    err.classList.remove('hidden');
  });
})();
