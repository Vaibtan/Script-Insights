from pathlib import Path

import fitz


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "fixtures" / "sample_script.pdf"
SCRIPT_TEXT = """Title: The Last Message

Scene: A station platform just after sunset.
Riya: Why are you texting me now?
Arjun: Because I learned the truth today.
Riya: What truth?
Arjun: The accident was never your fault.
"""


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), SCRIPT_TEXT)
    document.save(OUTPUT_PATH)
    document.close()


if __name__ == "__main__":
    main()
