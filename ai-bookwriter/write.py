import openai
import time
import os

# 1. Configure your API key
client = openai.OpenAI(api_key="<key>")

# 2. Set basic parameters
BOOK_TITLE = "The Future of Artificial Intelligence"
CHAPTER_TITLES = [
    "The Origins of AI",
    "Milestones in Machine Learning",
    "Neural Networks Demystified",
    "The Ethics of Automation",
    "The Future of Work",
    "AI and Creativity",
    "Where Do We Go From Here?"
]

# 3. Helper function to generate text
def generate_text(prompt, max_tokens=800, temperature=0.7):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful book-writing assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error: {e}")
        return ""

# 4. Book writing function
def write_book():
    book_content = f"# {BOOK_TITLE}\n\n"

    for i, title in enumerate(CHAPTER_TITLES, 1):
        print(f"Generating Chapter {i}: {title}")
        chapter_prompt = (
            f"Write a detailed and well-structured chapter titled '{title}' for a book "
            f"called '{BOOK_TITLE}'. Include a short intro, 2–3 subsections with headers, "
            f"and a brief conclusion."
        )
        chapter_text = generate_text(chapter_prompt)
        book_content += f"\n\n## Chapter {i}: {title}\n\n{chapter_text}\n"
        time.sleep(2)  # Optional: avoid rate limit

    with open("generated_book.md", "w", encoding="utf-8") as f:
        f.write(book_content)

    print("✅ Book writing complete. Saved as 'generated_book.md'")

# 5. Run it
if __name__ == "__main__":
    write_book()
