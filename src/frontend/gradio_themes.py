import gradio as gr
import requests
import time
from typing import List, Tuple

# Student-friendly theme configurations
STUDENT_THEMES = {
    "Ocean Breeze": {
        "theme": gr.themes.Ocean(),
        "css": """
            .gradio-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.1) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: 20px !important;
            }
        """
    },
    
    "Sunset Glow": {
        "theme": gr.themes.Soft(
            primary_hue=gr.themes.colors.orange,
            secondary_hue=gr.themes.colors.pink,
            neutral_hue=gr.themes.colors.gray
        ),
        "css": """
            .gradio-container {
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%) !important;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.2) !important;
                backdrop-filter: blur(15px) !important;
                border-radius: 25px !important;
            }
        """
    },
    
    "Forest Green": {
        "theme": gr.themes.Base(
            primary_hue=gr.themes.colors.green,
            secondary_hue=gr.themes.colors.teal,
            neutral_hue=gr.themes.colors.slate
        ),
        "css": """
            .gradio-container {
                background: linear-gradient(135deg, #134e5e 0%, #71b280 100%) !important;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.15) !important;
                backdrop-filter: blur(12px) !important;
                border-radius: 20px !important;
            }
        """
    },
    
    "Purple Dreams": {
        "theme": gr.themes.Glass(
            primary_hue=gr.themes.colors.purple,
            secondary_hue=gr.themes.colors.violet,
            neutral_hue=gr.themes.colors.gray
        ),
        "css": """
            .gradio-container {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            }
            .main-container {
                background: rgba(255, 255, 255, 0.12) !important;
                backdrop-filter: blur(18px) !important;
                border-radius: 22px !important;
            }
        """
    }
}

def create_theme_showcase():
    """Create a theme showcase for students to choose their preferred style"""
    
    with gr.Blocks(
        title="🎨 Choose Your Study Theme!",
        theme=gr.themes.Soft(primary_hue=gr.themes.colors.blue)
    ) as demo:
        
        gr.HTML("""
            <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 20px;">
                <h1>🎨 AI Study Buddy Theme Gallery</h1>
                <p>Choose your favorite theme to personalize your learning experience!</p>
            </div>
        """)
        
        with gr.Row():
            for theme_name, theme_config in STUDENT_THEMES.items():
                with gr.Column():
                    gr.HTML(f"""
                        <div style="background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 10px;">
                            <h3>{theme_name}</h3>
                        </div>
                    """)
                    
                    # Theme preview
                    with gr.Group():
                        gr.Textbox(label="Sample Text Input", placeholder=f"Preview of {theme_name} theme")
                        gr.Button(f"Try {theme_name}", variant="primary")
                        gr.Slider(label="Sample Slider", minimum=0, maximum=100, value=50)
        
        gr.HTML("""
            <div style="text-align: center; margin-top: 30px; padding: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 15px;">
                <h3>🌟 Features of Each Theme:</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div style="background: rgba(102, 126, 234, 0.2); padding: 15px; border-radius: 10px;">
                        <h4>🌊 Ocean Breeze</h4>
                        <p>Calming blue gradients perfect for focused study sessions</p>
                    </div>
                    <div style="background: rgba(255, 154, 158, 0.2); padding: 15px; border-radius: 10px;">
                        <h4>🌅 Sunset Glow</h4>
                        <p>Warm and energizing colors to boost creativity</p>
                    </div>
                    <div style="background: rgba(113, 178, 128, 0.2); padding: 15px; border-radius: 10px;">
                        <h4>🌲 Forest Green</h4>
                        <p>Natural green tones for a refreshing study environment</p>
                    </div>
                    <div style="background: rgba(118, 75, 162, 0.2); padding: 15px; border-radius: 10px;">
                        <h4>💜 Purple Dreams</h4>
                        <p>Mystical purple shades for inspiring deep thinking</p>
                    </div>
                </div>
            </div>
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_theme_showcase()
    demo.launch()

