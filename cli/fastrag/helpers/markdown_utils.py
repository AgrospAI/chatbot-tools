import re
import frontmatter

def clean_markdown(content: str) -> tuple[str, dict]:
    """
    Cleans navigation noise, extracts frontmatter, and strips base64 images.
    Returns: (cleaned_text, metadata_dict)
    """
    # Use frontmatter library to parse YAML frontmatter
    try:
        post = frontmatter.loads(content)
        metadata = post.metadata
        cleaned_content = post.content
    except Exception:
        return content, {}

    # Matches "# Title" or "Title \n ===="
    header_pattern = r"(^#\s.*)|(^.*?\n={3,}$)"
    header_match = re.search(header_pattern, cleaned_content, re.MULTILINE)
    if header_match:
        cleaned_content = cleaned_content[header_match.start():]
        
    # Remove Base64 Images
    cleaned_content = re.sub(r"!\[.*?\]\(data:image\/.*?\)", "", cleaned_content)
    
    # Remove Bullet-Links (* [Link](url))
    bullet_link_pattern = r"^\s*[*+-]\s+\[.*?\]\(.*?\)\s*$"
    cleaned_content = re.sub(bullet_link_pattern, "", cleaned_content, flags=re.MULTILINE)

    # Remove Standalone Links ([Link](url))
    standalone_link_pattern = r"^\s*\[.*?\]\(.*?\)\s*$"
    cleaned_content = re.sub(standalone_link_pattern, "", cleaned_content, flags=re.MULTILINE)
    
    # Remove Link Clusters ([A][B][C])
    cluster_pattern = r"(?:\[.*?\]\(.*?\)\s*){3,}"
    cleaned_content = re.sub(cluster_pattern, "", cleaned_content)
    
    # Remove Horizontal Nav ([A] * [B] * [C])
    multi_link_pattern = r"(?:\[.*?\]\(.*?\)\s*[\*\-]?\s*){3,}"
    cleaned_content = re.sub(multi_link_pattern, "", cleaned_content)
    
    # Remove Footer/Copyright
    cleaned_content = re.sub(r"^.*?Copyright ©.*$", "", cleaned_content, flags=re.MULTILINE | re.IGNORECASE)

    # Fix escaped hyphens
    cleaned_content = cleaned_content.replace(r"\-", "-")
    
    # Remove empty Docusaurus anchor links [​](url)
    cleaned_content = re.sub(r"\[[\s\u200b]*\]\(.*?\)", "", cleaned_content)
    
    # Normalize Headers
    cleaned_content = re.sub(r"^(.+?)\n={3,}\s*$", r"# \1", cleaned_content, flags=re.MULTILINE)
    cleaned_content = re.sub(r"^(.+?)\n-{3,}\s*$", r"## \1", cleaned_content, flags=re.MULTILINE)
    
    # Delete newlines
    cleaned_content = re.sub(r"\n{3,}", "\n\n", cleaned_content)
    
    return cleaned_content.strip(), metadata

def normalize_metadata(raw_meta: dict, uri: str) -> dict:
    """
    Standardizes keys (lang, title) and filters useful fields.
    """
    lang = raw_meta.get("meta-docsearch-language") or \
           raw_meta.get("meta-docusaurus_locale") or \
           raw_meta.get("lang") or "en"
           
    return {
        "source": raw_meta.get("canonical") or uri,
        "title": raw_meta.get("title", ""),
        "lang": lang,
        "keywords": raw_meta.get("meta-keywords", ""),
        "description": raw_meta.get("meta-description", "")
    }