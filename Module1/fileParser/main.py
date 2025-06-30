import argparse

def parse_file(file_path):
    try:
        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                # Process each line here (this example just prints it)
                print(f"{line_number}: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Simple file parser CLI.")
    parser.add_argument('filepath', help="Path to the input file")

    args = parser.parse_args()
    parse_file(args.filepath)

if __name__ == "__main__":
    main()
