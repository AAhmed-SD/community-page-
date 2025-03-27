// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore, collection, addDoc, serverTimestamp } from "firebase/firestore";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAmsgL5-3Qzv0-cot0TzYDXZ5-QQYNO9BA",
  authDomain: "ibaadahvercelapp.firebaseapp.com",
  projectId: "ibaadahvercelapp",
  storageBucket: "ibaadahvercelapp.firebasestorage.app",
  messagingSenderId: "695618210097",
  appId: "1:695618210097:web:a94717ed95d604cacdc810",
  measurementId: "G-R0BCQDK76H"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
let analytics = null;

// Initialize analytics only in browser environment
if (typeof window !== 'undefined') {
  analytics = getAnalytics(app);
}

// Function to submit form data to Firestore
export async function submitToFirestore(formData) {
  try {
    const submissionsRef = collection(db, "submissions");
    
    // Add timestamp
    formData.timestamp = serverTimestamp();
    
    // Submit to Firestore
    const docRef = await addDoc(submissionsRef, formData);
    return {
      success: true,
      id: docRef.id
    };
  } catch (error) {
    console.error("Error submitting form: ", error);
    return {
      success: false,
      error: error.message
    };
  }
}

export { db, app, analytics }; 