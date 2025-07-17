// Get DOM elements
const inputBox = document.querySelector('.input-box');
const submitButton = document.querySelector('.prompt-submission');
const imageContainer = document.querySelector('.image-presentaion');

// Add event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Enter key event listener
    inputBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            generate_image();
        }
    });
    
    // Button click event listener
    submitButton.addEventListener('click', generate_image);
});

// Main image generation function
async function generate_image() {
    const prompt = inputBox.value.trim();
    
    if (!prompt) {
        showError("Please enter a valid prompt");
        return;
    }
    
    setLoading(true);
    hideMessages();
    
    try {
        const response = await fetch('http://localhost:5000/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Make sure to use the correct image URL
            const imageUrl = `http://localhost:5000${data.image_url}`;
            displayImage(imageUrl, prompt);
            showSuccess("Image generated successfully!");
        } else {
            showError(data.error || "Failed to generate image");
        }
        
    } catch (error) {
        console.error('Error generating image:', error);
        showError("Network error. Please check if the server is running.");
    } finally {
        setLoading(false);
    }
}

// UI Helper Functions
function setLoading(isLoading) {
    if (isLoading) {
        submitButton.disabled = true;
        submitButton.textContent = 'Wait...';
        inputBox.disabled = true;
        
        // Show loading spinner
        imageContainer.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Generating your image...</p>
            </div>
        `;
    } else {
        submitButton.disabled = false;
        submitButton.textContent = 'Send';
        inputBox.disabled = false;
    }
}

function displayImage(imageSrc, prompt) {
    console.log('Displaying image:', imageSrc); // Debug log
    
    // Clear the container first
    imageContainer.innerHTML = '';
    
    // Create image element and handle loading
    const img = new Image();
    img.onload = function() {
        console.log('Image loaded successfully'); // Debug log
        
        imageContainer.innerHTML = `
            <div class="image-result">
                <img src="${imageSrc}" alt="Generated image for: ${prompt}" class="generated-image">
                <div class="image-info">
                    <p class="prompt-text"><strong>Prompt:</strong> ${prompt}</p>
                    <div class="image-actions">
                        <button onclick="downloadImage('${imageSrc}', '${prompt.replace(/'/g, "\\\'")}')" class="download-btn">
                            Download Image
                        </button>
                        <button onclick="generateAnother()" class="generate-another-btn">
                            Generate Another
                        </button>
                    </div>
                </div>
            </div>
        `;
    };
    
    img.onerror = function() {
        console.error('Failed to load image:', imageSrc); // Debug log
        showError("Failed to load the generated image");
        imageContainer.innerHTML = `
            <div class="error-result">
                <p>Image could not be loaded. Please try again.</p>
                <button onclick="generateAnother()" class="generate-another-btn">
                    Try Again
                </button>
            </div>
        `;
    };
    
    // Start loading the image
    img.src = imageSrc;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    // Remove existing messages
    hideMessages();
    
    // Add error message
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    
    // Remove existing messages
    hideMessages();
    
    // Add success message
    document.body.appendChild(successDiv);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 3000);
}

function hideMessages() {
    const messages = document.querySelectorAll('.error-message, .success-message');
    messages.forEach(msg => {
        if (msg.parentNode) {
            msg.remove();
        }
    });
}


function downloadImage(imageSrc, prompt) {
    console.log('Downloading image:', imageSrc); // Debug log
    
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `generated_image_${prompt.substring(0, 30).replace(/[^a-z0-9]/gi, '_')}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function generateAnother() {
    inputBox.value = '';
    inputBox.focus();
    // Don't clear the image container immediately - let user see the previous image
    // imageContainer.innerHTML = '';
}