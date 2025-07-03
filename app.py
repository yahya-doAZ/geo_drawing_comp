import streamlit as st
from openai import OpenAI
import os
import base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from prompts import COMP_PROMPT

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API Key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
# Function to encode image to base64
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  # Save the image in memory
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Function to compare the drawings using OpenAI API
def compare_drawings(previous_image_base64, current_image_base64):
    try:
        # Send request to OpenAI chat API
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[ {"role": "user",
                        "content": [
                { "type": "text", "text": COMP_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{previous_image_base64}",
                        "detail": "high"
                    }
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{current_image_base64}",
                        "detail": "high"
                            }
                }]
                        }  ,                ]
                      
                    
        )

        # Return the result from the response
        return response.choices[0].message.content

    except Exception as e:
        return f"Error occurred: {str(e)}"

# Streamlit UI Setup
st.title("Geotechnical Drawing Comparison")

# Upload previous and current version of the drawing
previous_image = st.file_uploader("Upload Previous Version of Drawing", type=["jpg", "png", "jpeg"])
current_image = st.file_uploader("Upload Current Version of Drawing", type=["jpg", "png", "jpeg"])

# Check if both images are uploaded
if previous_image is not None and current_image is not None:
    previous_image_pil = Image.open(previous_image)  # Open the image with PIL
    current_image_pil = Image.open(current_image)    # Open the image with PIL
    
    # Show the uploaded images
    st.image(previous_image_pil, caption="Previous Version", use_container_width=True)
    st.image(current_image_pil, caption="Current Version", use_container_width=True)

    # Encode both images to base64
    previous_image_base64 = encode_image(previous_image_pil)
    current_image_base64 = encode_image(current_image_pil)

# Button to start comparison
if st.button("Start Comparison"):
    if not previous_image or not current_image:
        st.warning("Please upload both previous and current drawings before starting the comparison.")
    else:
        # Compare the drawings using OpenAI (with base64 images)
        comparison_result = compare_drawings(previous_image_base64, current_image_base64)

        # Display the comparison result
        st.subheader("Comparison Results:")
        st.text(comparison_result)

# Allow users to change images and re-click start for comparison
st.sidebar.subheader("Change Drawings")
new_previous_image = st.sidebar.file_uploader("Change Previous Drawing", type=["jpg", "png", "jpeg"])
new_current_image = st.sidebar.file_uploader("Change Current Drawing", type=["jpg", "png", "jpeg"])

if new_previous_image and new_current_image:
    st.sidebar.text("You can click 'Start Comparison' again after uploading the new drawings.")
