
# Replace the existing chat endpoint in main.py with this:

@app.post("/chat")
async def chat_endpoint(request: dict):
    """Flexible chat endpoint that accepts various formats"""
    try:
        # Handle different possible request formats
        if isinstance(request, dict):
            message = request.get("message", "")
        else:
            message = str(request)
            
        if not message:
            raise HTTPException(status_code=400, detail="No message provided")
            
        # Demo AI response
        response = f"🤖 **AI Study Buddy Response:**\n\n"
        response += f"You asked: *'{message}'*\n\n"
        response += "📚 **Demo Features Working:**\n"
        response += "• ✅ User Authentication\n"
        response += "• ✅ Beautiful Student Interface\n" 
        response += "• ✅ Real-time Chat\n"
        response += "• ✅ Responsive Design\n\n"
        response += "💡 **Study Tips:**\n"
        response += "- Break study sessions into 25-minute chunks\n"
        response += "- Use active recall techniques\n"
        response += "- Connect new concepts to existing knowledge\n\n"
        response += "🎯 **Next:** Upload documents for personalized help!"
        
        return {
            "bot_response": response,
            "response_time_ms": 150,
            "context_documents": [],
            "metadata": {"model_used": "demo", "status": "success"}
        }
    except Exception as e:
        return {"bot_response": f"Error: {str(e)}", "response_time_ms": 0}

@app.post("/documents")
async def upload_document(request: dict):
    """Flexible document upload endpoint"""
    try:
        filename = request.get("filename", "document.txt")
        content = request.get("content", "")
        
        # Demo document analysis
        word_count = len(content.split()) if content else 0
        
        return {
            "id": 1,
            "filename": filename,
            "analysis": {
                "word_count": word_count,
                "keywords": ["learning", "study", "education"] if content else [],
                "entities_found": 2,
                "status": "processed"
            },
            "processing_time_ms": 200,
            "message": f"📄 Document '{filename}' uploaded successfully! ({word_count} words)"
        }
    except Exception as e:
        return {"error": str(e), "message": "Upload failed"}
