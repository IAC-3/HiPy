import sys
import json
from pathlib import Path

# Add src/ to path so parser is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from parser import run_command


def main() -> None:
    output = run_command("/Users/marcomattiuz/Music/Music")
    data = json.loads(output)
    print(f"mediainfo output elements: {len(data)}")


if __name__ == "__main__":
    main()
    main()
