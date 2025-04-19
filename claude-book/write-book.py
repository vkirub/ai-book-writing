import os
import json
import time
import anthropic
from typing import List, Dict, Any, Optional

class ClaudeBookAgent:
    """Agent that uses Claude to write a book autonomously."""
    
    def __init__(self, api_key: str, model: str = "claude-3-7-sonnet-20250219"):
        """
        Initialize the Claude Book Agent.
        
        Args:
            api_key: Your Anthropic API key
            model: Claude model to use
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = 4000
        self.book_data = {
            "title": "",
            "author": "Claude AI", 
            "description": "",
            "chapters": []
        }
        self.conversation_history = []
        
    def _call_claude(self, prompt: str, temperature: float = 0.7) -> str:
        """Make a call to Claude API."""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system="You are a professional book writer and researcher. Your responses should be thorough, well-researched, and written in an engaging style.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return ""
    
    def choose_topic(self) -> str:
        """Have Claude choose an interesting book topic."""
        prompt = """
        I need you to select an interesting topic for a book. The topic should be:
        
        1. Interesting to a wide audience
        2. Something that can be well-researched online
        3. Have enough depth for a full book
        4. Creative and engaging
        
        Please provide:
        1. The book topic/title
        2. A brief description of what the book will cover
        3. Why this topic would make a compelling book
        
        Keep your response focused and concise.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def research_topic(self, topic: str) -> str:
        """Have Claude research a topic thoroughly."""
        prompt = f"""
        I need you to conduct thorough research on the topic: "{topic}"
        
        Please provide:
        1. Key facts, concepts, and information about this topic
        2. Important subtopics or related areas
        3. Different perspectives or approaches to this topic
        4. Any interesting data points, statistics, or examples
        5. The most important authors, experts, or sources on this topic
        
        Organize your research in a clear, structured way. Focus on providing accurate,
        comprehensive information that would be useful for writing a book.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def create_book_outline(self, topic: str, research: str) -> Dict[str, Any]:
        """Have Claude create a detailed book outline."""
        prompt = f"""
        Based on the topic "{topic}" and the research you've conducted, create a detailed outline for a book.
        
        Please provide:
        1. A compelling title for the book
        2. A brief description/summary of the book's purpose and content
        3. A list of chapters with:
           - Chapter titles
           - Brief description of each chapter's content
           - Key points to cover in each chapter
        
        The outline should be well-organized, logical, and cover the topic comprehensively.
        Format your response as a structured outline.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Parse the response to extract book structure
        # This is a simplified parsing - in a real app, you'd use more robust parsing
        lines = response.split('\n')
        book_outline = {"title": "", "description": "", "chapters": []}
        
        # Very simple parsing - you might want to implement a more robust approach
        for line in lines:
            if "title:" in line.lower() or "title " in line.lower():
                book_outline["title"] = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            
        current_chapter = None
        for line in lines:
            if "chapter" in line.lower() and ":" in line:
                if current_chapter:
                    book_outline["chapters"].append(current_chapter)
                chapter_title = line.split(":", 1)[1].strip()
                current_chapter = {"title": chapter_title, "description": "", "content": ""}
            elif current_chapter and line.strip() and not line.startswith("#"):
                current_chapter["description"] += line.strip() + " "
        
        if current_chapter:
            book_outline["chapters"].append(current_chapter)
            
        if not book_outline["title"] and len(book_outline["chapters"]) > 0:
            book_outline["title"] = "Book on " + topic
            
        return book_outline, response
    
    def critique_outline(self, outline: str) -> str:
        """Have Claude critique the book outline."""
        prompt = f"""
        Please critique the following book outline:
        
        {outline}
        
        Consider:
        1. Is the structure logical and well-organized?
        2. Are any important topics or perspectives missing?
        3. Is there a good flow between chapters?
        4. Is the scope appropriate (not too broad or too narrow)?
        5. Would this outline result in an engaging, informative book?
        
        Provide specific suggestions for improvement.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def improve_outline(self, outline: str, critique: str) -> Dict[str, Any]:
        """Have Claude improve the outline based on critique."""
        prompt = f"""
        Please improve the following book outline based on this critique:
        
        ORIGINAL OUTLINE:
        {outline}
        
        CRITIQUE:
        {critique}
        
        Provide a revised, improved book outline that addresses the issues in the critique.
        Format it clearly with a title, description, and well-structured chapters.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Parse the improved outline similar to before
        lines = response.split('\n')
        improved_outline = {"title": "", "description": "", "chapters": []}
        
        for line in lines:
            if "title:" in line.lower() or "title " in line.lower():
                improved_outline["title"] = line.split(":", 1)[1].strip() if ":" in line else line.strip()
            
        current_chapter = None
        for line in lines:
            if "chapter" in line.lower() and ":" in line:
                if current_chapter:
                    improved_outline["chapters"].append(current_chapter)
                chapter_title = line.split(":", 1)[1].strip()
                current_chapter = {"title": chapter_title, "description": "", "content": ""}
            elif current_chapter and line.strip() and not line.startswith("#"):
                current_chapter["description"] += line.strip() + " "
        
        if current_chapter:
            improved_outline["chapters"].append(current_chapter)
            
        # Extract description from the response
        description_markers = ["description:", "summary:", "about:"]
        for line in lines:
            lower_line = line.lower()
            if any(marker in lower_line for marker in description_markers):
                improved_outline["description"] = line.split(":", 1)[1].strip()
                break
        
        return improved_outline, response
    
    def write_chapter(self, chapter_title: str, chapter_description: str, book_context: str) -> str:
        """Have Claude write a full chapter."""
        prompt = f"""
        Write a complete chapter for a book with the following specifications:
        
        BOOK CONTEXT:
        {book_context}
        
        CHAPTER TITLE:
        {chapter_title}
        
        CHAPTER DESCRIPTION:
        {chapter_description}
        
        Please write this chapter in a engaging, well-structured way that a human author would write.
        Include relevant examples, stories, or data where appropriate.
        Avoid overly academic language and make the content accessible and interesting.
        Structure the chapter with clear sections and subsections where needed.
        
        Write the full chapter text now:
        """
        
        response = self._call_claude(prompt, temperature=0.8)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def critique_chapter(self, chapter_text: str, chapter_title: str) -> str:
        """Have Claude critique a chapter."""
        prompt = f"""
        Please critique the following chapter titled "{chapter_title}":
        
        {chapter_text[:2000]}... [truncated for brevity]
        
        Consider:
        1. Writing quality and engagement
        2. Structure and flow
        3. Content accuracy and depth
        4. Examples and illustrations
        5. Overall effectiveness
        
        Provide specific suggestions for improvement.
        """
        
        response = self._call_claude(prompt)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def improve_chapter(self, chapter_text: str, critique: str, chapter_title: str) -> str:
        """Have Claude improve a chapter based on critique."""
        prompt = f"""
        Please improve the following chapter titled "{chapter_title}" based on this critique:
        
        CRITIQUE:
        {critique}
        
        ORIGINAL CHAPTER:
        {chapter_text[:2000]}... [truncated for brevity]
        
        Rewrite the chapter to address the issues in the critique. Make it more engaging,
        well-structured, and comprehensive. Ensure it has a natural human-like writing style.
        
        Write the full improved chapter now:
        """
        
        response = self._call_claude(prompt, temperature=0.75)
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        return response
    
    def create_book(self) -> None:
        """Execute the full book creation process."""
        print("🤖 Claude Book Agent: Starting book creation process...")
        
        # Step 1: Choose a topic
        print("🔍 Choosing a book topic...")
        topic_response = self.choose_topic()
        print(f"📚 Selected topic:\n{topic_response}\n")
        
        # Step 2: Research the topic
        print("🔍 Researching the topic thoroughly...")
        research = self.research_topic(topic_response)
        print(f"📝 Research completed: {len(research)} characters")
        
        # Step 3: Create book outline
        print("📋 Creating initial book outline...")
        book_outline, outline_text = self.create_book_outline(topic_response, research)
        self.book_data["title"] = book_outline["title"]
        print(f"📑 Initial outline created for '{self.book_data['title']}'")
        
        # Step 4: Critique and improve outline
        print("🧐 Critiquing the outline...")
        critique = self.critique_outline(outline_text)
        print("✏️ Improving the outline based on critique...")
        improved_outline, improved_outline_text = self.improve_outline(outline_text, critique)
        
        # Update book data with improved outline
        self.book_data["title"] = improved_outline["title"] or book_outline["title"]
        self.book_data["description"] = improved_outline["description"] or book_outline["description"]
        self.book_data["chapters"] = improved_outline["chapters"]
        
        print(f"📕 Final book outline: '{self.book_data['title']}' with {len(self.book_data['chapters'])} chapters")
        
        # Step 5: Write each chapter
        for i, chapter in enumerate(self.book_data["chapters"]):
            print(f"✍️ Writing chapter {i+1}: {chapter['title']}...")
            
            # Create book context for the chapter
            book_context = f"Book Title: {self.book_data['title']}\nBook Description: {self.book_data['description']}\n"
            book_context += "Chapters: " + ", ".join([ch["title"] for ch in self.book_data["chapters"]])
            
            # Write initial chapter
            chapter_text = self.write_chapter(chapter["title"], chapter["description"], book_context)
            
            # Critique and improve chapter
            print(f"🧐 Critiquing chapter {i+1}...")
            critique = self.critique_chapter(chapter_text, chapter["title"])
            
            print(f"✏️ Improving chapter {i+1} based on critique...")
            improved_chapter = self.improve_chapter(chapter_text, critique, chapter["title"])
            
            # Save improved chapter
            self.book_data["chapters"][i]["content"] = improved_chapter
            print(f"✅ Completed chapter {i+1}: {len(improved_chapter)} characters")
            
            # Save progress after each chapter
            self.save_book_to_file()
            
            # Optional: Add a delay to avoid API rate limits
            time.sleep(2)
        
        print(f"🎉 Book '{self.book_data['title']}' has been completed!")
        print(f"📁 Book saved to 'claude_book.json' and 'claude_book.txt'")
    
    def save_book_to_file(self) -> None:
        """Save the book to JSON and text files."""
        # Save as JSON for structure
        with open("claude_book.json", "w") as f:
            json.dump(self.book_data, f, indent=2)
        
        # Save as plain text for reading
        with open("claude_book.txt", "w") as f:
            f.write(f"# {self.book_data['title']}\n\n")
            f.write(f"By {self.book_data['author']}\n\n")
            f.write(f"{self.book_data['description']}\n\n")
            
            # Table of contents
            f.write("## Table of Contents\n\n")
            for i, chapter in enumerate(self.book_data["chapters"]):
                f.write(f"{i+1}. {chapter['title']}\n")
            f.write("\n\n")
            
            # Chapters
            for i, chapter in enumerate(self.book_data["chapters"]):
                f.write(f"## Chapter {i+1}: {chapter['title']}\n\n")
                f.write(f"{chapter['content']}\n\n")

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = os.environ.get("ANTHROPIC_API_KEY", "<key>")
    
    # Create and run the agent
    book_agent = ClaudeBookAgent(api_key=API_KEY)
    book_agent.create_book()