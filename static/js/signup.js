// Validación de formulario de SignUp
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

const sign_up = (csrf_token) => {
    let email = document.getElementById('floatingEmailInput').value;
    let nombre = document.getElementById('floatingNombreInput').value;
    let apellido = document.getElementById('floatingApellidoInput').value;    
    let password = document.getElementById('floatingPassword').value;
    let password2 = document.getElementById('floatingPassword2').value;

    axios.post('/signup/',
      {'nombre': nombre, 'apellido': apellido, 'email': email, 'password': password},
      {headers: {'X-CSRFToken': csrf_token}}
    ).then(resultado => {
        alert('El usuario se registró exitosamente. Inicie sesión.');
        document.location.href = '/login';
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