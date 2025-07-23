import yaml
from markdown_it import MarkdownIt
from typing import Tuple

# Custom YAML loader to treat dates as plain strings
class NoDateSafeLoader(yaml.SafeLoader):
    @classmethod
    def remove_implicit_resolver(cls, tag_to_remove):
        if 'yaml_implicit_resolvers' not in cls.__dict__:
            cls.yaml_implicit_resolvers = cls.yaml_implicit_resolvers.copy()
        for first_letter, mappings in cls.yaml_implicit_resolvers.items():
            cls.yaml_implicit_resolvers[first_letter] = [
                (tag, regexp) for tag, regexp in mappings if tag != tag_to_remove
            ]

NoDateSafeLoader.remove_implicit_resolver('tag:yaml.org,2002:timestamp')

def split_frontmatter(markdown_text: str) -> Tuple[dict, str]:
    """
    Parses frontmatter and content from a Markdown document manually.
    """
    if not markdown_text.strip().startswith('---'):
        return {}, markdown_text

    # Split the document at the frontmatter delimiters
    parts = markdown_text.split('---', 2)
    if len(parts) < 3:
        # This means there's no valid frontmatter block
        return {}, markdown_text

    # The first part is empty, the second is the frontmatter, the third is content
    _, frontmatter_str, content = parts
    
    metadata = {}
    try:
        # Load the YAML from the frontmatter string
        parsed_yaml = yaml.load(frontmatter_str, Loader=NoDateSafeLoader)
        if isinstance(parsed_yaml, dict):
            metadata = parsed_yaml
    except yaml.YAMLError:
        # If parsing fails, return empty metadata and the original text
        return {}, markdown_text

    return metadata, content.strip()

def split_markdown_document_by_top_level_heading(markdown_text: str, max_segments: int = 2) -> list[str]:
    """
    Splits a Markdown document into a specified number of segments based on top-level paragraphs.

    The function identifies top-level paragraphs and splits the document into
    up to `max_segments`, working from the bottom up. For example, with `max_segments`=3,
    the document is split at the last two top-level paragraphs.

    Args:
        markdown_text: The Markdown document as a string.
        max_segments: The maximum desired number of segments.

    Returns:
        A list of strings, where each string is a segment of the document.
        If there are fewer top-level paragraphs than needed, the document will be
        split into fewer than `max_segments`.
    """
    if not markdown_text.strip() or max_segments < 2:
        return [markdown_text]

    md = MarkdownIt()
    tokens = md.parse(markdown_text)

    # Find the line numbers of all top-level paragraphs
    para_line_numbers = []
    for token in tokens:
        if token.type == 'paragraph_open' and token.level == 0 and token.map:
            para_line_numbers.append(token.map[0])

    # If there are not enough paragraphs to create the desired number of segments,
    # the document will be split into fewer segments using all available paragraph markers.
    if not para_line_numbers:
        return [markdown_text]
    
    # Determine the split points. These are the start lines of the last `max_segments` - 1 paragraphs.
    split_points = sorted(para_line_numbers[-(max_segments - 1):])

    # Split the document at the identified line numbers
    lines = markdown_text.splitlines()
    segments = []
    last_split = 0
    for point in split_points:
        segments.append("\n".join(lines[last_split:point]))
        last_split = point
    
    # Add the final segment
    segments.append("\n".join(lines[last_split:]))

    return segments
