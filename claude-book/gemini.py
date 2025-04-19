import os
import datetime
import random
import string
import anthropic  # Assuming you have the Anthropic Python library installed

# Replace with your actual Anthropic API key
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY environment variable not set.")
    exit()

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def generate_session_name(length=8):
    """Generates a random session name."""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def create_session_folder(session_name):
    """Creates a folder for the session."""
    folder_path = os.path.join(os.getcwd(), session_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def log_output(folder_path, filename, content):
    """Logs the output to a file."""
    filepath = os.path.join(folder_path, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Output logged to: {filepath}")

def get_user_confirmation(prompt):
    """Prompts the user for confirmation."""
    while True:
        response = input(f"{prompt} (yes/no): ").lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def call_claude(prompt, model="claude-3-5-haiku-20241022", max_tokens=1024):
    """Calls the Claude AI model."""
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text.strip()
    except Exception as e:
        print(f"Error calling Claude: {e}")
        return None

def research_topic(topic, session_folder):
    """Conducts initial research on the topic."""
    prompt = f"Research the topic '{topic}'. Identify key aspects, potential themes, and interesting areas for a book. Provide a summary of your findings."
    print(f"\n--- Conducting Research on '{topic}' ---")
    research_output = call_claude(prompt, max_tokens=2048)
    if research_output:
        log_output(session_folder, "01_research_topic.txt", research_output)
    return research_output

def create_book_outline(topic, research_summary, session_folder):
    """Creates an initial book outline based on the research."""
    prompt = f"Based on the research summary:\n\n{research_summary}\n\nCreate a detailed book outline for a book on the topic '{topic}'. Include potential chapter titles and a brief description of what each chapter might cover."
    print(f"\n--- Creating Initial Book Outline for '{topic}' ---")
    outline = call_claude(prompt, max_tokens=2048)
    if outline:
        log_output(session_folder, "02_initial_book_outline.txt", outline)
    return outline

def critique_outline(outline, session_folder):
    """Critiques the book outline."""
    prompt = f"Critique the following book outline:\n\n{outline}\n\nIdentify any potential weaknesses, areas for improvement, logical flow issues, or missing elements. Provide specific suggestions for revision."
    print("\n--- Critiquing Book Outline ---")
    critique = call_claude(prompt, max_tokens=1024)
    if critique:
        log_output(session_folder, "03_critique_book_outline.txt", critique)
    return critique

def fix_outline(outline, critique, session_folder):
    """Revises the book outline based on the critique."""
    prompt = f"Revise the following book outline based on the critique provided:\n\n**Original Outline:**\n{outline}\n\n**Critique:**\n{critique}\n\nPresent the improved book outline."
    print("\n--- Revising Book Outline ---")
    revised_outline = call_claude(prompt, max_tokens=2048)
    if revised_outline:
        log_output(session_folder, "04_revised_book_outline.txt", revised_outline)
    return revised_outline

def process_chapter(chapter_title, book_topic, session_folder, chapter_number):
    """Processes a single chapter: research, outline, critique, write."""
    print(f"\n--- Processing Chapter {chapter_number}: '{chapter_title}' ---")

    # Chapter Research
    chapter_research_prompt = f"Research the topic of '{chapter_title}' in the context of the book '{book_topic}'. Identify key information, relevant examples, and potential subtopics for this chapter."
    print(f"Conducting research for Chapter {chapter_number}...")
    chapter_research = call_claude(chapter_research_prompt, max_tokens=2048)
    if chapter_research:
        log_output(session_folder, f"{chapter_number:02d}_chapter_{chapter_number}_research.txt", chapter_research)
    else:
        print(f"Failed to get research for Chapter {chapter_number}.")
        return None

    # Chapter Outline
    chapter_outline_prompt = f"Based on the research:\n\n{chapter_research}\n\nCreate a detailed outline for the chapter titled '{chapter_title}' for the book '{book_topic}'. Include sections and subsections with brief descriptions."
    print(f"Creating outline for Chapter {chapter_number}...")
    chapter_outline = call_claude(chapter_outline_prompt, max_tokens=1024)
    if chapter_outline:
        log_output(session_folder, f"{chapter_number:02d}_chapter_{chapter_number}_outline.txt", chapter_outline)
    else:
        print(f"Failed to create outline for Chapter {chapter_number}.")
        return None

    # Critique Chapter Outline
    chapter_critique_prompt = f"Critique the following chapter outline:\n\n{chapter_outline}\n\nIdentify any weaknesses, areas for improvement, logical flow issues, or missing elements. Provide specific suggestions for revision."
    print(f"Critiquing outline for Chapter {chapter_number}...")
    chapter_critique = call_claude(chapter_critique_prompt, max_tokens=1024)
    if chapter_critique:
        log_output(session_folder, f"{chapter_number:02d}_chapter_{chapter_number}_outline_critique.txt", chapter_critique)
    else:
        print(f"Failed to critique outline for Chapter {chapter_number}.")
        return None

    # Fix Chapter Outline
    chapter_fix_prompt = f"Revise the following chapter outline based on the critique provided:\n\n**Original Outline:**\n{chapter_outline}\n\n**Critique:**\n{chapter_critique}\n\nPresent the improved chapter outline."
    print(f"Revising outline for Chapter {chapter_number}...")
    revised_chapter_outline = call_claude(chapter_fix_prompt, max_tokens=1024)
    if revised_chapter_outline:
        log_output(session_folder, f"{chapter_number:02d}_chapter_{chapter_number}_outline_revised.txt", revised_chapter_outline)
    else:
        print(f"Failed to revise outline for Chapter {chapter_number}.")
        return None

    # Write Chapter
    chapter_writing_prompt = f"Write the content for the following chapter of the book '{book_topic}', following this outline:\n\n{revised_chapter_outline}\n\nEnsure the writing is engaging, informative, and in a humanized style. Incorporate details from the initial research where appropriate."
    print(f"Writing Chapter {chapter_number}...")
    chapter_content = call_claude(chapter_writing_prompt, max_tokens=3000) # Increased max tokens for writing
    if chapter_content:
        log_output(session_folder, f"{chapter_number:02d}_chapter_{chapter_number}_content.txt", chapter_content)
        return chapter_content
    else:
        print(f"Failed to write content for Chapter {chapter_number}.")
        return None

def main():
    """Main function to orchestrate the book writing process."""
    session_name = generate_session_name()
    session_folder = create_session_folder(session_name)
    print(f"Session started. Output will be saved in folder: {session_folder}")

    # --- Decide on Book Topic ---
    user_topic_suggestion = input("Do you have any ideas for the book topic? (Enter your suggestion or leave blank): ").strip()
    if user_topic_suggestion:
        proposed_topic = user_topic_suggestion
        print(f"Using your suggested topic: '{proposed_topic}'")
    else:
        print("Asking Claude for topic suggestions...")
        topic_suggestion_prompt = "Suggest a few interesting and potentially engaging book topics."
        topic_suggestions = call_claude(topic_suggestion_prompt)
        if topic_suggestions:
            print("Claude's topic suggestions:\n", topic_suggestions)
            proposed_topic = input("Please choose a topic from the suggestions above or enter your own: ").strip()
        else:
            proposed_topic = input("Claude failed to suggest topics. Please enter your desired book topic: ").strip()

    if not get_user_confirmation(f"Do you confirm the book topic: '{proposed_topic}'?"):
        proposed_topic = input("Please enter the desired book topic: ").strip()
        if not get_user_confirmation(f"Do you confirm the book topic: '{proposed_topic}'?"):
            print("Topic not confirmed. Exiting.")
            return
    book_topic = proposed_topic
    log_output(session_folder, "00_book_topic.txt", book_topic)

    # --- Research Book Topic ---
    research_summary = research_topic(book_topic, session_folder)
    if not research_summary:
        print("Failed to complete initial research. Exiting.")
        return
    if not get_user_confirmation("Do you want to proceed with the book outline based on this research?"):
        print("Research not confirmed. Exiting.")
        return

    # --- Create, Critique, and Fix Book Outline ---
    initial_outline = create_book_outline(book_topic, research_summary, session_folder)
    if not initial_outline:
        print("Failed to create initial book outline. Exiting.")
        return
    if not get_user_confirmation("Do you want to critique this book outline?"):
        print("Initial outline not confirmed. Exiting.")
        return

    outline_critique = critique_outline(initial_outline, session_folder)
    if not outline_critique:
        print("Failed to critique the book outline. Exiting.")
        return
    if not get_user_confirmation("Do you want to revise the book outline based on this critique?"):
        print("Critique not confirmed. Proceeding with the initial outline.")
        revised_outline = initial_outline
    else:
        revised_outline = fix_outline(initial_outline, outline_critique, session_folder)
        if not revised_outline:
            print("Failed to revise the book outline. Exiting.")
            return
    log_output(session_folder, "05_final_book_outline.txt", revised_outline)
    print("\n--- Final Book Outline ---")
    print(revised_outline)
    if not get_user_confirmation("Do you confirm this final book outline and want to proceed with writing chapters?"):
        print("Book outline not confirmed. Exiting.")
        return

    # --- Process Each Chapter ---
    chapters = [line.split('.')[1].strip() for line in revised_outline.splitlines() if line.strip() and line[0].isdigit() and '.' in line]
    print(f"\n--- Starting Chapter Generation ({len(chapters)} chapters) ---")
    book_content = {}
    for i, chapter_title in enumerate(chapters, 1):
        print(f"\n--- Preparing to process Chapter {i}: '{chapter_title}' ---")
        if get_user_confirmation(f"Do you want to proceed with writing Chapter {i}: '{chapter_title}'?"):
            chapter_content_result = process_chapter(chapter_title, book_topic, session_folder, i)
            if chapter_content_result:
                book_content[chapter_title] = chapter_content_result
        else:
            print(f"Skipping Chapter {i}: '{chapter_title}'.")

    # --- Combine and Save the Book ---
    if book_content:
        full_book_text = f"# {book_topic}\n\n"
        for title, content in book_content.items():
            full_book_text += f"## {title}\n\n{content}\n\n"
        log_output(session_folder, "full_book.txt", full_book_text)
        print("\n--- Book Generation Complete! ---")
        print(f"The full book content has been saved in: {os.path.join(session_folder, 'full_book.txt')}")
    else:
        print("\n--- No chapters were written. Book generation incomplete. ---")

if __name__ == "__main__":
    main()