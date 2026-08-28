import argparse
import sys
from pathlib import Path
from yamlrender import yamlrender


PACKAGE_DIR = Path(__file__).resolve().parent


def get_default_template_path() -> Path:
    return PACKAGE_DIR / "template.html"


def main():
    parser = argparse.ArgumentParser(
        description="Generate a PDF resume from a YAML file"
    )
    parser.add_argument(
        "yaml_file",
        type=Path,
        help="Path to the input YAML resume file"
    )
    parser.add_argument(
        "-t", "--template",
        type=Path,
        default=None,
        help="Path to a custom HTML template (default: built-in template)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Path to the output HTML or PDF file (default: replace input extension with .pdf)"
    )

    args = parser.parse_args()

    input_path: Path = args.yaml_file

    if not input_path.exists():
        print(f"Error: File not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if not input_path.is_file():
        print(f"Error: Not a file: {input_path}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        output_path = args.output
    else:
        output_path = input_path.with_suffix(".pdf")

    if args.template is not None:
        template_path = args.template
        if not template_path.exists():
            print(f"Error: Template file not found: {template_path}", file=sys.stderr)
            sys.exit(1)
    else:
        template_path = get_default_template_path()

    print(f"Input:    {input_path}")
    print(f"Template: {template_path}")
    print(f"Output:   {output_path}")

    yamlrender(input_path, template_path, output_path)

    print(f"\nSuccessfully generated: {output_path}")


if __name__ == "__main__":
    main()
