import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, setDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import firebaseConfig from './config.js';
// Your web app's Firebase configuration


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const firestore = getFirestore(app);

const submit = document.getElementById("submit");

submit.addEventListener("click", function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const username = document.getElementById("username").value;
    const genre = document.getElementById("genre").value;
    const description = document.getElementById("description").value;
    const gender = document.getElementById("gender").value;
    if (email.trim() === "" || password.trim() === "" || username.trim() === "") {
        alert("Email, password, and username cannot be empty");
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert("Invalid email format");
        return;
    }

    if (password.length < 6) {
        alert("Password must be at least 6 characters long");
        return;
    }

    createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;

            // Add user to Firestore
            setDoc(doc(firestore, 'users', user.uid), {
                email: email,
                username: username,
                genre: genre,
                description:description,
                gender:gender
            }).then(() => {
                alert("Creating Account.....");
                window.location.href = '/';
            }).catch((error) => {
                alert("Error adding user to database: " + error.message);
            });
        })
        .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            alert(errorMessage);
        });
});
