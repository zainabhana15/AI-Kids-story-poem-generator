import streamlit as st
import openai
from PIL import Image
import io
import requests
from fpdf import FPDF
import base64

class CreativeGenerator:
    def __init__(self, api_key):
        openai.api_key = api_key
        
    def generate_content(self, theme, content_type, age_range="5-10", specific_element=None):
        if content_type == "Story":
            prompt = f"""Write a short, engaging {age_range} year old children's story about {theme}.
            {'Include ' + specific_element + ' in the story.' if specific_element else ''}
            The story should be imaginative, age-appropriate, and positive.
            Keep it between 100-150 words.
            Include some simple moral or learning element.
            Use simple language suitable for children."""
        else:  # Poem
            prompt = f"""Write a cheerful, rhyming poem for {age_range} year old children about {theme}.
            {'Include ' + specific_element + ' in the poem.' if specific_element else ''}
            The poem should be imaginative and fun.
            Keep it between 4-6 stanzas.
            Use simple, age-appropriate language.
            Make sure it has a clear rhythm and rhyme scheme."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a children's creative writer who creates engaging, imaginative content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def generate_image_prompt(self, content, style_element, specific_element=None):
        prompt = f"""Create an image prompt for DALL-E based on this children's content:
        {content}
        Style: {style_element}
        {'Include these specific elements: ' + specific_element if specific_element else ''}
        Make it colorful and appealing to children."""
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at creating detailed image generation prompts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def generate_image(self, prompt):
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url

    def create_pdf(self, content, image_url, content_type, output_path):
        # Download the image
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        img.save("temp_image.png")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", "B", 24)
        pdf.cell(0, 20, f"Your Special {content_type}", ln=True, align="C")
        
        # Add content
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, content)
        
        # Add image
        pdf.image("temp_image.png", x=15, w=180)
        
        pdf.output(output_path)
        return output_path

def main():
    st.set_page_config(page_title="Story & Poem Generator", layout="wide")
    
    st.title("Story & Poem Generator")
    st.write("Create your own personalized stories and poems with matching illustrations!")
    
    # API Key input
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if not api_key:
        st.warning("Please enter your OpenAI API key ")
        return
    
    # Initialize generator
    generator = CreativeGenerator(api_key)
    
    # User inputs
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.checkbox("What would you like to create?", ["Story", "Poem"])
    
    with col2:
        theme = st.text_input("What should your " + content_type.lower() + " be about?", 
                            placeholder="e.g., a magical forest, a friendly dragon")
    
    
    specific_element = st.text_input("Add specific elements to include (optional):",
                                   placeholder="e.g., a red-haired girl, a flying unicorn")
    
    if st.button(f"Generate {content_type} and Image! "):
        if theme:
            with st.spinner(f"Creating your magical {content_type.lower()}..."):
                # Generate content
                content = generator.generate_content(theme, content_type, specific_element=specific_element)
                st.subheader(f"Your {content_type}:")
                st.write(content)
                
                # Generate image
                with st.spinner("Crafting your illustration..."):
                    image_prompt = generator.generate_image_prompt(content, specific_element)
                    image_url = generator.generate_image(image_prompt)
                    st.image(image_url, caption=f"Your {content_type.lower()} illustration", use_column_width=True)
                
                # Create and offer PDF download
                pdf_path = f"{content_type.lower()}.pdf"
                generator.create_pdf(content, image_url, content_type, pdf_path)
                
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                    st.download_button(
                        label="Download ",
                        data=pdf_bytes,
                        file_name=f"your_magical_{content_type.lower()}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.error(f"Please enter a theme for your {content_type.lower()}!")

if __name__ == "__main__":
    main()