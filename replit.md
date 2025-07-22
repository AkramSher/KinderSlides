# KinderSlides - Kindergarten PowerPoint Generator

## Overview

KinderSlides is a Flask web application that automatically generates educational PowerPoint presentations for kindergarten students. The application creates visually appealing slides with images and text covering topics like ABC letters, numbers, shapes, and colors. It integrates with the Pixabay API to fetch appropriate child-friendly images for each topic.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: HTML5 with Bootstrap 5 (Dark Theme variant)
- **Styling**: Custom CSS with kindergarten-friendly color schemes and animations
- **JavaScript**: Vanilla JavaScript for form interactions and UI feedback
- **UI Components**: Bootstrap modals, cards, and form elements with custom kindergarten styling
- **Icons**: Font Awesome 6.4.0 for visual elements

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Single-file application architecture with `app.py` as main module
- **Entry Point**: `main.py` serves as the application runner
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **Static Files**: Organized in `/static/` directory (CSS, JS)
- **Templates**: HTML templates in `/templates/` directory

## Key Components

### Topic Management System
- **Problem**: Need to organize different educational topics for kindergarten students
- **Solution**: Dictionary-based topic definitions with predefined content for ABC, Numbers, Shapes, and Colors
- **Benefits**: Easy to maintain and extend with new topics

### Image Integration
- **Problem**: Need high-quality, child-appropriate images for presentations
- **Solution**: Pixabay API integration with curated search terms
- **Configuration**: Environment-based API key management
- **Search Strategy**: Topic-specific search terms optimized for cartoon/child-friendly results

### Presentation Generation
- **Library**: python-pptx for PowerPoint file creation
- **Features**: Custom formatting, colors, fonts, and layouts
- **Output**: Downloadable .pptx files with professional kindergarten-appropriate design

### User Interface Design
- **Theme**: Dark theme with bright, kindergarten-friendly accent colors
- **Color Scheme**: Custom CSS variables for consistent theming
- **Interactions**: Hover effects, animations, and visual feedback
- **Accessibility**: Clear typography and intuitive navigation

## Data Flow

1. **User Selection**: User selects a topic from the dropdown menu
2. **Form Submission**: POST request sent to Flask backend
3. **Topic Processing**: Backend retrieves topic content from predefined dictionaries
4. **Image Fetching**: System queries Pixabay API for relevant images
5. **Presentation Creation**: python-pptx generates PowerPoint slides
6. **File Delivery**: Completed presentation sent as downloadable file

## External Dependencies

### APIs
- **Pixabay API**: For fetching child-appropriate images
  - Authentication via API key (environment variable)
  - RESTful API integration
  - Image search and retrieval

### Python Libraries
- **Flask**: Web framework and routing
- **python-pptx**: PowerPoint file generation
- **requests**: HTTP client for API calls
- **tempfile**: Temporary file management
- **uuid**: Unique identifier generation

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome 6**: Icon library
- **Vanilla JavaScript**: No additional frameworks required

## Deployment Strategy

### Environment Configuration
- **Secret Management**: Environment variables for API keys and session secrets
- **Development**: Debug mode enabled via `main.py`
- **Host Configuration**: Configured for 0.0.0.0:5000 (Replit-compatible)

### File Management
- **Static Assets**: Served directly by Flask
- **Temporary Files**: Created and cleaned up automatically
- **Downloads**: Direct file streaming to user

### Security Considerations
- **Session Security**: Secret key configuration
- **Input Validation**: Topic selection limited to predefined options
- **API Security**: Pixabay API key stored as environment variable

### Scalability Notes
- Current architecture suitable for small to medium usage
- Single-file structure allows easy deployment but may need refactoring for larger scale
- Image caching could be implemented for better performance