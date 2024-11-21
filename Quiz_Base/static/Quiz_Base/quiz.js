document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('#quiz-form');
    const submitButton = document.querySelector('#submit-quiz');

    submitButton.addEventListener('click', function (e) {
        e.preventDefault(); // Prevent default form behavior
        form.submit(); // Submit the form normally
    });
});
