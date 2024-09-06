import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth,signInWithPopup, FacebookAuthProvider } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDMwD8yTOmfAh3cANY6pcwjPYHQCj1yJXw",
  authDomain: "scifigen-5154f.firebaseapp.com",
  projectId: "scifigen-5154f",
  storageBucket: "scifigen-5154f.appspot.com",
  messagingSenderId: "968222875826",
  appId: "1:968222875826:web:3ffc4e988686f6f39c69ab",
  measurementId: "G-DKZ42Q7YY3"
};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

const provider = new FacebookAuthProvider();
auth.languageCode = 'en';


const facebook = document.getElementById("facebook");
facebook.addEventListener("click", function (event) {
 event.preventDefault()

 signInWithPopup(auth, provider)
  .then((result) => {
   // The signed-in user info.
   const user = result.user;

   // This gives you a Facebook Access Token. You can use it to access the Facebook API.
   const credential = FacebookAuthProvider.credentialFromResult(result);
   const accessToken = credential.accessToken;

   // IdP data available using getAdditionalUserInfo(result)
   // ...
  })
  .catch((error) => {
   // Handle Errors here.
   const errorCode = error.code;
   const errorMessage = error.message;
   // The email of the user's account used.
   const email = error.customData.email;
   // The AuthCredential type that was used.
   const credential = FacebookAuthProvider.credentialFromError(error);

   // ...
  });
})


