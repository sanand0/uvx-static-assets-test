from pathlib import Path; import sys
def main():
    p = Path(sys.prefix) / "messages.txt"; print(p.read_text().format(name=sys.argv[1]), end=""); print(p)
if __name__ == "__main__": main()
