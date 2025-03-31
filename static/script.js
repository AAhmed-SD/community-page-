// Initialize Firebase services
const auth = firebase.auth();
const db = firebase.firestore();

// Check authentication state
auth.onAuthStateChanged(async (user) => {
    // Only redirect if we're on the login page and user is already authenticated
    if (user && window.location.pathname.includes('login.html')) {
        try {
            // Check if user exists in submissions
            const submissionsRef = db.collection('submissions');
            const query = submissionsRef.where('email', '==', user.email);
            const querySnapshot = await query.get();

            if (!querySnapshot.empty) {
                window.location.href = '/community.html';
            } else {
                // If no submission exists, sign them out
                await auth.signOut();
            }
        } catch (error) {
            console.error('Error checking submission:', error);
        }
    }
});

// Handle login form submission
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const submitButton = e.target.querySelector('button[type="submit"]');

    try {
        submitButton.disabled = true;
        submitButton.textContent = 'Logging in...';
        errorMessage.style.display = 'none';
        successMessage.style.display = 'none';

        // First check if email exists in submissions
        console.log('Checking submissions for:', email);
        const submissionsRef = db.collection('submissions');
        const query = submissionsRef.where('email', '==', email);
        const querySnapshot = await query.get();

        if (querySnapshot.empty) {
            console.log('No submission found for email:', email);
            throw new Error('No account found with this email. Please submit the form first.');
        }

        console.log('Submission found, attempting login');
        try {
            const userCredential = await auth.signInWithEmailAndPassword(email, password);
            console.log('Login successful:', userCredential.user.email);
            window.location.href = '/community.html';
        } catch (authError) {
            console.log('Auth error:', authError.code);
            if (authError.code === 'auth/user-not-found' || authError.code === 'auth/wrong-password') {
                errorMessage.textContent = 'Please set up your password using the "Forgot Password" link below to activate your account.';
                errorMessage.style.display = 'block';
            } else {
                throw authError;
            }
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Login';
    }
});

// Handle forgot password / account activation
window.handleForgotPassword = async () => {
    const email = document.getElementById('email').value;
    const errorMessage = document.getElementById('error-message');
    const successMessage = document.getElementById('success-message');
    const forgotPasswordBtn = document.getElementById('forgot-password-btn');

    if (!email) {
        errorMessage.textContent = 'Please enter your email address first.';
        errorMessage.style.display = 'block';
        successMessage.style.display = 'none';
        return;
    }

    try {
        // First check if email exists in submissions
        const submissionsRef = db.collection('submissions');
        const query = submissionsRef.where('email', '==', email);
        const querySnapshot = await query.get();

        if (querySnapshot.empty) {
            throw new Error('No account found with this email. Please submit the form first.');
        }

        forgotPasswordBtn.disabled = true;
        forgotPasswordBtn.textContent = 'Sending...';
        
        // Send password reset/setup email
        await auth.sendPasswordResetEmail(email);
        
        successMessage.textContent = 'Account activation email sent! Please check your inbox to set up your password.';
        successMessage.style.display = 'block';
        errorMessage.style.display = 'none';
    } catch (error) {
        console.error('Error sending activation email:', error);
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
        successMessage.style.display = 'none';
    } finally {
        forgotPasswordBtn.disabled = false;
        forgotPasswordBtn.textContent = 'Activate Account / Set Password';
    }
};

// Handle waitlist form submission
const waitlistForm = document.getElementById('waitlist-form');
if (waitlistForm) {
    waitlistForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errorMessage = document.getElementById('error-message');
        errorMessage.style.display = 'none';

        // Get form data
        const formData = new FormData(waitlistForm);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password'),
            spiritual_routines: formData.get('spiritual_routines'),
            current_apps: formData.get('current_apps'),
            feature: formData.get('feature'),
            helpful_feature: formData.get('helpful_feature'),
            tester: formData.get('tester')
        };

        // Validate passwords match
        if (data.password !== formData.get('confirmPassword')) {
            errorMessage.textContent = 'Passwords do not match';
            errorMessage.style.display = 'block';
            return;
        }

        try {
            // Create user account
            const userCredential = await auth.createUserWithEmailAndPassword(data.email, data.password);
            
            // Submit form data to Firestore
            await db.collection('submissions').doc(userCredential.user.uid).set({
                ...data,
                timestamp: firebase.firestore.FieldValue.serverTimestamp()
            });
            
            // Redirect to thank you page
            window.location.href = '/thank-you.html';
        } catch (error) {
            console.error('Error:', error);
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
        }
    });
} 