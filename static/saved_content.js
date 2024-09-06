    import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
    import { getAuth, onAuthStateChanged, signOut } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
    import { getFirestore, collection, query, where, getDocs, deleteDoc,doc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
    import firebaseConfig from './config.js';

    
    // Initialize Firebase
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);
    const firestore = getFirestore(app);

    // Monitor auth state and update UI accordingly
    // Monitor auth state and update UI accordingly
    onAuthStateChanged(auth, async (user) => {
        if (user) {
            const userEmailElement = document.getElementById('user-email');
            userEmailElement.textContent = `Logged in as: ${user.email}`;
    
            const generatedContentList = document.getElementById('generated-content-list');
            generatedContentList.innerHTML = '';
    
            try {
                const userContentRef = collection(firestore, `users/${user.uid}/generatedContent`);
                const querySnapshot = await getDocs(userContentRef);
                
                querySnapshot.forEach((doc) => {
                    const content = doc.data();
                    const contentElement = document.createElement('div');
                    contentElement.classList.add('generated-content-item');
                    contentElement.innerHTML = `
                        <h3>${content.title}</h3>
                        <p>${content.text}</p>
                        <img src="${content.imageURL}" alt="Generated Image">
                        <p class="timestamp">Timestamp: ${content.timestamp.toDate().toLocaleString()}</p>
                        <button class="futuristic-btn delete-btn" data-docid="${doc.id}">Delete</button>
                    `;
                    generatedContentList.appendChild(contentElement);

                    // Add click event listener for expansion
                    contentElement.addEventListener('click', function(event) {
                        if (!event.target.classList.contains('delete-btn')) {
                            this.classList.toggle('expanded');
                        }
                    });

                    // Add event listener for delete button
                    const deleteBtn = contentElement.querySelector('.delete-btn');
                    deleteBtn.addEventListener('click', async (event) => {
                        event.stopPropagation(); // Prevent triggering the parent's click event
                        const docId = event.target.getAttribute('data-docid');
                        await deleteContent(user.uid, docId);
                        contentElement.remove();
                    });
                });
    
            } catch (error) {
                console.error('Error fetching user-generated content:', error);
            }
        } else {
            window.location.href = '/';
        }
    });
    
    // Function to delete content
    async function deleteContent(userId, docId) {
        try {
            await deleteDoc(doc(firestore, `users/${userId}/generatedContent`, docId));
            console.log('Document successfully deleted');
        } catch (error) {
            console.error('Error deleting document: ', error);
        }
    }




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
