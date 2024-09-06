import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore, doc, getDoc, setDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js";

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

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const firestore = getFirestore(app);
const storage = getStorage(app);

async function uploadImageToFirebase(imageData, userId, title) {
    const storageRef = ref(storage, `generated_images/${userId}/${title}`);
    await uploadBytes(storageRef, imageData);
    return await getDownloadURL(storageRef);
}
// Function to generate and upload avatar
async function generateAvatar(description, userId) {
    try {
        const response = await fetch('/generate_avatar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description }),
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

// Monitor auth state and update UI accordingly
onAuthStateChanged(auth, async (user) => {
    if (user) {
        const userEmailElement = document.getElementById('user-email');
        const userAvatarElement = document.getElementById('user-avatar');
        
        // Fetch the user's document from Firestore
        const userDocRef = doc(firestore, 'users', user.uid);
        const userDocSnap = await getDoc(userDocRef);
        
        if (userDocSnap.exists()) {
            const userData = userDocSnap.data();
            userEmailElement.textContent = `Logged in as: ${userData.username}`;
            
            if (userAvatarElement && userData.avatarUrl) {
                userAvatarElement.src = userData.avatarUrl;
            } else if (userAvatarElement) {
                // Generate avatar if it doesn't exist
                const defaultDescription = "A mysterious sci-fi character";
                const avatarUrl = await generateAvatar(defaultDescription, user.uid);
                await setDoc(userDocRef, { ...userData, avatarUrl: avatarUrl }, { merge: true });
                userAvatarElement.src = avatarUrl;
            }
        } else {
            userEmailElement.textContent = `Logged in as: ${user.email}`;
            if (userAvatarElement) {
                const defaultDescription = "A mysterious sci-fi character";
                const avatarUrl = await generateAvatar(defaultDescription, user.uid);
                await setDoc(userDocRef, {
                    username: user.email,
                    avatarUrl: avatarUrl,
                    description: defaultDescription
                });
                userAvatarElement.src = avatarUrl;
            }
        }
    } else {
        // No user is signed in, redirect to login page
        window.location.href = '/';
    }
});

// Sign out functionality
const logout = document.getElementById("sign-out");
logout.addEventListener("click", function (event) {
    event.preventDefault();
    signOut(auth).then(
        function () {
            alert("Logging out...");
            window.location.href = '/';
        }
    ).catch(function () {
        alert("Error, can't logout...");
    });
});

// Save generated text to Firestore
const saveToFirestoreButton = document.querySelector('.save-to-firestore-button');
saveToFirestoreButton.addEventListener('click', async () => {
    const user = auth.currentUser;
    if (user) {
        const generatedText = document.querySelector('.generated-text').textContent;
        const generatedTitle = document.querySelector('h3.text-center.mb-4').textContent;
        const generatedImageElement = document.querySelector('img.generated-image');
        
        try {
            // Fetch the image data
            const response = await fetch(generatedImageElement.src);
            const blob = await response.blob();
            
            // Upload image to Firebase Storage
            const permanentImageURL = await uploadImageToFirebase(blob, user.uid, generatedTitle);
            
            // Save to Firestore
            const userDocRef = doc(firestore, `users/${user.uid}/generatedContent/${generatedTitle}`);
            await setDoc(userDocRef, {
                title: generatedTitle,
                text: generatedText,
                imageURL: permanentImageURL,
                timestamp: new Date()
            });
            alert('Generated content saved successfully!');
        } catch (error) {
            console.error('Error saving content:', error);
            alert('Failed to save content.');
        }
    } else {
        alert('No user is signed in.');
    }
});