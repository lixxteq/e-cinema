const input = document.getElementById('password');
const validateChars = document.getElementById('validate-chars')
const validateNums = document.getElementById('validate-nums')
const validateLowercase = document.getElementById('validate-lowercase')
const confirmInput = document.getElementById('confirm_password')
const confirmState = document.getElementById('confirm-state')
const signUp = document.getElementById('signup')

let lowercaseState = false
let numsState = false
let charsState = false
let passwordValid = false
let confirmValid = false

input.onkeyup = () => {
    lowercaseState = input.value.match(/[a-z]/g);
    numsState = input.value.match(/[0-9]/g);
    charsState = input.value.length >= 8;
    if (lowercaseState) {
        validateLowercase.classList.add("v-valid");
    } else {
        validateLowercase.classList.remove("v-valid");
    }
    if (numsState) {
        validateNums.classList.add("v-valid");
    } else {
        validateNums.classList.remove("v-valid");
    }

    if (charsState) {
        validateChars.classList.add("v-valid");
    } else {
        validateChars.classList.remove("v-valid");
    }
    passwordValid = lowercaseState && numsState && charsState
    onInput()
}

confirmInput.onkeyup = () => {
    onInput()
}

const onInput = () => {
    confirmValid = confirmInput.value === input.value
    signUp.disabled = passwordValid && confirmValid ? false : true
    if (!confirmValid) {
        confirmState.classList.contains('d-none') ? confirmState.classList.remove('d-none') : null 
    }
    else {
        confirmState.classList.add('d-none')
    }
}