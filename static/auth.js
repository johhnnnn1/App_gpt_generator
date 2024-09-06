import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc, updateDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js";
import firebaseConfig from './config.js';



const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);
const storage = getStorage(app);

// Function to generate and upload avatar
async function generateAvatar(description, gender, userId) {
    try {
        const response = await fetch('/generate_avatar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description, gender }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        
        // Upload the image to Firebase Storage
        const storageRef = ref(storage, `avatars/${userId}`);
        await uploadBytes(storageRef, blob);

        // Get the permanent download URL
        const permanentUrl = await getDownloadURL(storageRef);

        return permanentUrl;
    } catch (error) {
        console.error("Error generating or uploading avatar:", error);
        throw error;
    }
}

// Login functionality
const submit = document.getElementById("submit");
const loadingMessage = document.getElementById("loadingMessage");

if (submit) {
    submit.addEventListener("click", async function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        // Email and password validation
        if (email.trim() === "" || password.trim() === "") {
            alert("Email and password cannot be empty");
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

        try {
            loadingMessage.style.display = "block";
            submit.disabled = true;

            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;
            
            const docSnap = await getDoc(doc(db, 'users', user.uid));
            
            if (docSnap.exists()) {
                const userData = docSnap.data();
                let userDescription = userData.description || "A mysterious sci-fi character";
                let userGender=userData.gender;
                localStorage.setItem('userDescription', userDescription);
                
                if (!userData.avatarUrl || !userData.description) {
                    const avatarUrl = await generateAvatar(userDescription, userGender, user.uid);
                    await updateDoc(doc(db, 'users', user.uid), { 
                        avatarUrl: avatarUrl,
                        description: userDescription,
                        gender:userGender
                    });
                    localStorage.setItem('userAvatarUrl', avatarUrl);
                } else {
                    localStorage.setItem('userAvatarUrl', userData.avatarUrl);
                }
            } else {
                const defaultDescription = "A mysterious sci-fi character";
                const userGender=userData.gender;
                const avatarUrl = await generateAvatar(defaultDescription, userGender, user.uid);
                await setDoc(doc(db, 'users', user.uid), {
                    description: defaultDescription,
                    avatarUrl: avatarUrl,
                    gender:userGender
                });
                localStorage.setItem('userDescription', defaultDescription);
                localStorage.setItem('userAvatarUrl', avatarUrl);
                localStorage.setItem('userGender', userGender);
            }
            
            loadingMessage.style.display = "none";
            window.location.href = '/index';
        } catch (error) {
            loadingMessage.style.display = "none";
            submit.disabled = false;
            alert(error.message);
        }
    });
}

// Monitor auth state and update UI
onAuthStateChanged(auth, (user) => {
    if (user) {
        const userEmailElement = document.getElementById('user-email');
        const userAvatarElement = document.getElementById('user-avatar');
        
        // Fetch user data from Firestore
        getDoc(doc(db, 'users', user.uid)).then((docSnap) => {
            if (docSnap.exists()) {
                const userData = docSnap.data();
                const userGenre = userData.genre;
                const username = userData.username;
                if (userEmailElement) {
                    userEmailElement.textContent = `Logged in as: ${username}`;
                }
                
                // Fetch and display the avatar
                if (userAvatarElement && userData.avatarUrl) {
                    userAvatarElement.src = userData.avatarUrl;
                }

                // Check the corresponding radio button if it exists
                const genreRadio = document.querySelector(`input[name="subgenre"][value="${userGenre}"]`);
                if (genreRadio) {
                    genreRadio.checked = true;
                }
            } else {
                console.log("No user data found!");
            }
        }).catch((error) => {
            console.error("Error fet error");
        });
    } else {
        // No user is signed in, redirect to login page if not already there
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
    }
});

// Sign out functionality
const logout = document.getElementById("sign-out");
if (logout) {
    logout.addEventListener("click", function (event) {
        event.preventDefault();
        signOut(auth).then(() => {
            console.log("Logged out successfully");
            window.location.href = '/';
        }).catch((error) => {
            console.error("Error logging out:", error);
        });
    });
}

