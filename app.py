import os
import logging
import requests
from io import BytesIO
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "kindergarten-slides-secret-key")

# Pixabay API configuration
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "your-pixabay-api-key")
PIXABAY_BASE_URL = "https://pixabay.com/api/"

# Topic definitions
TOPICS = {
    "ABC": ["A - Apple", "B - Ball", "C - Cat", "D - Dog", "E - Elephant", "F - Fish", "G - Giraffe", 
            "H - House", "I - Ice cream", "J - Jellyfish", "K - Kite", "L - Lion", "M - Moon", 
            "N - Nest", "O - Orange", "P - Penguin", "Q - Queen", "R - Rainbow", "S - Sun", 
            "T - Tree", "U - Umbrella", "V - Violin", "W - Whale", "X - X-ray", "Y - Yacht", "Z - Zebra"],
    "Numbers 1-5": ["1 - One", "2 - Two", "3 - Three", "4 - Four", "5 - Five"],
    "Shapes": ["Circle", "Square", "Triangle", "Rectangle", "Star", "Heart"],
    "Colors": ["Red", "Blue", "Yellow", "Green", "Orange", "Purple", "Pink", "Brown"]
}

# Search terms for Pixabay
SEARCH_TERMS = {
    "ABC": {
        "A - Apple": "red apple fruit illustration",
        "B - Ball": "colorful ball toy illustration",
        "C - Cat": "cute cat animal illustration",
        "D - Dog": "friendly dog pet illustration",
        "E - Elephant": "gray elephant animal illustration",
        "F - Fish": "colorful fish swimming illustration",
        "G - Giraffe": "tall giraffe animal illustration",
        "H - House": "simple house home illustration",
        "I - Ice cream": "ice cream cone dessert illustration",
        "J - Jellyfish": "jellyfish ocean animal illustration",
        "K - Kite": "colorful kite flying illustration",
        "L - Lion": "lion king animal illustration",
        "M - Moon": "crescent moon night illustration",
        "N - Nest": "bird nest with eggs illustration",
        "O - Orange": "orange citrus fruit illustration",
        "P - Penguin": "cute penguin bird illustration",
        "Q - Queen": "royal queen crown illustration",
        "R - Rainbow": "colorful rainbow arch illustration",
        "S - Sun": "bright yellow sun illustration",
        "T - Tree": "green tree nature illustration",
        "U - Umbrella": "colorful umbrella rain illustration",
        "V - Violin": "musical violin instrument illustration",
        "W - Whale": "blue whale ocean animal illustration",
        "X - X-ray": "x-ray medical skeleton illustration",
        "Y - Yacht": "sailing boat yacht illustration",
        "Z - Zebra": "black white zebra animal illustration"
    },
    "Numbers 1-5": {
        "1 - One": "number 1 cartoon",
        "2 - Two": "number 2 cartoon",
        "3 - Three": "number 3 cartoon",
        "4 - Four": "number 4 cartoon",
        "5 - Five": "number 5 cartoon"
    },
    "Shapes": {
        "Circle": "circle shape cartoon",
        "Square": "square shape cartoon",
        "Triangle": "triangle shape cartoon",
        "Rectangle": "rectangle shape cartoon",
        "Star": "star shape cartoon",
        "Heart": "heart shape cartoon"
    },
    "Colors": {
        "Red": "red color cartoon",
        "Blue": "blue color cartoon",
        "Yellow": "yellow color cartoon",
        "Green": "green color cartoon",
        "Orange": "orange color cartoon",
        "Purple": "purple color cartoon",
        "Pink": "pink color cartoon",
        "Brown": "brown color cartoon"
    }
}

def search_pixabay_image(search_term, item_name=None):
    """Search for an image on Pixabay API with improved accuracy"""
    
    # Extract base word for better searching
    base_word = search_term
    if item_name:
        base_word = item_name.split(' - ')[-1] if ' - ' in item_name else item_name
    
    # Create multiple search variations for better results
    search_variations = [search_term]
    
    if item_name:
        # Add more specific search terms
        search_variations = [
            f"{base_word} cartoon illustration",
            f"{base_word} vector illustration",
            f"{base_word} cartoon kids",
            f"{base_word} simple illustration",
            search_term,  # Original search term as fallback
        ]
    
    for search in search_variations:
        try:
            # Try with education category first
            params = {
                'key': PIXABAY_API_KEY,
                'q': search,
                'image_type': 'illustration',
                'category': 'education',
                'safesearch': 'true',
                'per_page': 10,
                'min_width': 400,
                'min_height': 300
            }
            
            response = requests.get(PIXABAY_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Filter results to find relevant images
            if data.get('hits'):
                for hit in data['hits']:
                    tags = hit.get('tags', '').lower()
                    # Check if the image tags are relevant to our search
                    if any(word in tags for word in base_word.lower().split() if len(word) > 2):
                        image_url = hit['webformatURL']
                        downloaded_image = download_image(image_url)
                        if downloaded_image:
                            logging.info(f"Found relevant image for '{item_name}' with search: '{search}'")
                            return downloaded_image
                
                # If no relevant images found, try the first result as fallback
                if len(data['hits']) > 0:
                    image_url = data['hits'][0]['webformatURL']
                    downloaded_image = download_image(image_url)
                    if downloaded_image:
                        logging.info(f"Using fallback image for '{item_name}' with search: '{search}'")
                        return downloaded_image
            
            # If education category doesn't work, try without category restriction
            if not data.get('hits'):
                params.pop('category', None)
                response = requests.get(PIXABAY_BASE_URL, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data.get('hits'):
                    for hit in data['hits']:
                        tags = hit.get('tags', '').lower()
                        if any(word in tags for word in base_word.lower().split() if len(word) > 2):
                            image_url = hit['webformatURL']
                            downloaded_image = download_image(image_url)
                            if downloaded_image:
                                logging.info(f"Found relevant image for '{item_name}' with search: '{search}' (no category)")
                                return downloaded_image
                            
        except Exception as e:
            logging.error(f"Error searching Pixabay for '{search}': {str(e)}")
            continue
    
    logging.warning(f"No relevant images found for: {item_name or search_term}")
    return None

def download_image(image_url):
    """Download image from URL and return as BytesIO object"""
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        
        image_stream = BytesIO(response.content)
        return image_stream
        
    except Exception as e:
        logging.error(f"Error downloading image from {image_url}: {str(e)}")
        return None

def create_presentation(topic, items, search_terms):
    """Create PowerPoint presentation for the given topic"""
    try:
        # Create presentation
        prs = Presentation()
        
        # Set slide dimensions (16:9 aspect ratio)
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)
        
        # Title slide
        title_slide_layout = prs.slide_layouts[0]
        title_slide = prs.slides.add_slide(title_slide_layout)
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        title.text = f"Learning {topic}"
        subtitle.text = "KinderSlides Presentation"
        
        # Style title slide
        title_para = title.text_frame.paragraphs[0]
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = RGBColor(255, 87, 51)  # Orange-red
        
        subtitle_para = subtitle.text_frame.paragraphs[0]
        subtitle_para.font.size = Pt(32)
        subtitle_para.font.color.rgb = RGBColor(52, 152, 219)  # Blue
        
        # Create slides for each item
        for item in items:
            try:
                # Use blank slide layout
                blank_slide_layout = prs.slide_layouts[6]
                slide = prs.slides.add_slide(blank_slide_layout)
                
                # Add title text box
                title_left = Inches(0.5)
                title_top = Inches(0.5)
                title_width = Inches(12.33)
                title_height = Inches(2)
                
                title_box = slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
                title_frame = title_box.text_frame
                title_frame.text = item
                
                # Style title
                title_paragraph = title_frame.paragraphs[0]
                title_paragraph.font.size = Pt(72)
                title_paragraph.font.bold = True
                title_paragraph.font.color.rgb = RGBColor(46, 125, 50)  # Green
                title_paragraph.alignment = PP_ALIGN.CENTER
                
                # Search and add image
                search_term = search_terms.get(item, item + " cartoon")
                image_stream = search_pixabay_image(search_term, item)
                
                if image_stream:
                    # Add image to slide
                    image_left = Inches(2)
                    image_top = Inches(2.5)
                    image_width = Inches(9.33)
                    image_height = Inches(4.5)
                    
                    slide.shapes.add_picture(image_stream, image_left, image_top, image_width, image_height)
                    logging.info(f"Added image for {item}")
                else:
                    # Add placeholder text if no image found
                    placeholder_left = Inches(2)
                    placeholder_top = Inches(3)
                    placeholder_width = Inches(9.33)
                    placeholder_height = Inches(3)
                    
                    placeholder_box = slide.shapes.add_textbox(placeholder_left, placeholder_top, placeholder_width, placeholder_height)
                    placeholder_frame = placeholder_box.text_frame
                    placeholder_frame.text = f"Image for {item}\n(Not available)"
                    
                    placeholder_paragraph = placeholder_frame.paragraphs[0]
                    placeholder_paragraph.font.size = Pt(48)
                    placeholder_paragraph.font.color.rgb = RGBColor(155, 155, 155)  # Gray
                    placeholder_paragraph.alignment = PP_ALIGN.CENTER
                    
                    logging.warning(f"No image found for {item}, added placeholder")
                    
            except Exception as e:
                logging.error(f"Error creating slide for {item}: {str(e)}")
                continue
        
        return prs
        
    except Exception as e:
        logging.error(f"Error creating presentation: {str(e)}")
        return None

@app.route('/')
def index():
    """Main page with topic selection form"""
    return render_template('index.html', topics=list(TOPICS.keys()))

@app.route('/generate', methods=['POST'])
def generate_presentation():
    """Generate PowerPoint presentation based on selected or custom topic"""
    try:
        topic = request.form.get('topic')
        custom_topic = request.form.get('custom_topic', '').strip()
        custom_items = request.form.get('custom_items', '').strip()
        
        # Handle custom topic
        if topic == "custom" and custom_topic and custom_items:
            topic = custom_topic
            # Parse custom items (comma-separated)
            items = [item.strip() for item in custom_items.split(',') if item.strip()]
            if not items:
                flash('Please provide at least one item for your custom topic.', 'error')
                return redirect(url_for('index'))
            
            # Generate search terms for custom items
            search_terms = {}
            for item in items:
                # Create more specific search terms based on common categories
                item_lower = item.lower()
                if any(word in item_lower for word in ['car', 'bus', 'truck', 'train', 'plane', 'bike', 'auto', 'lorry', 'helicopter']):
                    search_terms[item] = f"{item} vehicle transport illustration"
                elif any(word in item_lower for word in ['dog', 'cat', 'bird', 'fish', 'lion', 'tiger', 'elephant', 'horse']):
                    search_terms[item] = f"{item} animal cute illustration"
                elif any(word in item_lower for word in ['apple', 'banana', 'orange', 'grape', 'strawberry', 'mango']):
                    search_terms[item] = f"{item} fresh fruit illustration"
                elif any(word in item_lower for word in ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink']):
                    search_terms[item] = f"{item} color bright illustration"
                else:
                    search_terms[item] = f"{item} simple children illustration"
            
        elif topic and topic in TOPICS:
            # Use predefined topic
            items = TOPICS[topic]
            search_terms = SEARCH_TERMS[topic]
        else:
            flash('Please select a valid topic or create a custom one.', 'error')
            return redirect(url_for('index'))
        
        if not PIXABAY_API_KEY or PIXABAY_API_KEY == "your-pixabay-api-key":
            flash('Pixabay API key is not configured. Please contact your administrator.', 'error')
            return redirect(url_for('index'))
        
        logging.info(f"Generating presentation for topic: {topic}")
        
        # Create presentation
        presentation = create_presentation(topic, items, search_terms)
        
        if not presentation:
            flash('Error creating presentation. Please try again.', 'error')
            return redirect(url_for('index'))
        
        # Save presentation to temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pptx')
        presentation.save(temp_file.name)
        temp_file.close()
        
        # Generate filename
        filename = f"KinderSlides_{topic.replace(' ', '_').replace('/', '_')}_{uuid.uuid4().hex[:8]}.pptx"
        
        logging.info(f"Presentation created successfully: {filename}")
        
        # Send file for download
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        logging.error(f"Error in generate_presentation: {str(e)}")
        flash('An error occurred while generating the presentation. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/api/progress/<topic>')
def get_progress(topic):
    """API endpoint to get generation progress (placeholder for future enhancement)"""
    return jsonify({'status': 'processing', 'progress': 50})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
