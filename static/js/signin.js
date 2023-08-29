// Validación de formulario de SignIn
(() => {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    const forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
  
        form.classList.add('was-validated')
      }, false)
    })
})()

const sign_in = (csrf_token) => {
  let username = document.getElementById('floatingUsername').value;
  let password = document.getElementById('floatingPassword').value;

  axios.post('/login/',
    {'username': username, 'password': password},
    {headers: {'X-CSRFToken': csrf_token}}
  ).then(resultado => {
    document.location.href = '/';
  }).catch(error => {
    let feedbackOtrasValidaciones = document.getElementById('feedbackOtrasValidaciones');
    feedbackOtrasValidaciones.classList.remove('d-none');        
    if (error.response.data) {
        feedbackOtrasValidaciones.innerHTML = error.response.data.msg;
    }else {
      feedbackOtrasValidaciones.innerHTML = 'No se pudo registrar el usuario. Ocurrió un problema de comunicación';
    }
  });
}