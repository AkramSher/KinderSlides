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
        "A - Apple": "apple cartoon",
        "B - Ball": "ball cartoon",
        "C - Cat": "cat cartoon",
        "D - Dog": "dog cartoon",
        "E - Elephant": "elephant cartoon",
        "F - Fish": "fish cartoon",
        "G - Giraffe": "giraffe cartoon",
        "H - House": "house cartoon",
        "I - Ice cream": "ice cream cartoon",
        "J - Jellyfish": "jellyfish cartoon",
        "K - Kite": "kite cartoon",
        "L - Lion": "lion cartoon",
        "M - Moon": "moon cartoon",
        "N - Nest": "nest cartoon",
        "O - Orange": "orange fruit cartoon",
        "P - Penguin": "penguin cartoon",
        "Q - Queen": "queen cartoon",
        "R - Rainbow": "rainbow cartoon",
        "S - Sun": "sun cartoon",
        "T - Tree": "tree cartoon",
        "U - Umbrella": "umbrella cartoon",
        "V - Violin": "violin cartoon",
        "W - Whale": "whale cartoon",
        "X - X-ray": "x-ray cartoon",
        "Y - Yacht": "yacht cartoon",
        "Z - Zebra": "zebra cartoon"
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

def search_pixabay_image(search_term):
    """Search for an image on Pixabay API"""
    try:
        params = {
            'key': PIXABAY_API_KEY,
            'q': search_term,
            'image_type': 'illustration',
            'category': 'education',
            'safesearch': 'true',
            'per_page': 5,
            'min_width': 640,
            'min_height': 480
        }
        
        response = requests.get(PIXABAY_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('hits') and len(data['hits']) > 0:
            # Get the first suitable image
            image_url = data['hits'][0]['webformatURL']
            return download_image(image_url)
        else:
            logging.warning(f"No images found for search term: {search_term}")
            return None
            
    except Exception as e:
        logging.error(f"Error searching Pixabay for '{search_term}': {str(e)}")
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
                image_stream = search_pixabay_image(search_term)
                
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
    """Generate PowerPoint presentation based on selected topic"""
    try:
        topic = request.form.get('topic')
        
        if not topic or topic not in TOPICS:
            flash('Please select a valid topic.', 'error')
            return redirect(url_for('index'))
        
        if not PIXABAY_API_KEY or PIXABAY_API_KEY == "your-pixabay-api-key":
            flash('Pixabay API key is not configured. Please contact your administrator.', 'error')
            return redirect(url_for('index'))
        
        # Get items and search terms for the topic
        items = TOPICS[topic]
        search_terms = SEARCH_TERMS[topic]
        
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
        filename = f"KinderSlides_{topic.replace(' ', '_')}_{uuid.uuid4().hex[:8]}.pptx"
        
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
