# Yushufang website

The site uses Jekyll and GitHub Pages. The production domain is https://yushufang.org.

Pages share `_layouts/default.html`, the navigation data in `_data/navigation.json`, and `assets/site.css`. Articles are Markdown files under `_posts/`, with explicit stable `/essays/<slug>/` URLs, author, publication date, revision date and version metadata.

The `Site checks` workflow builds Jekyll and validates rendered links, metadata and publication boundaries before changes are merged. The existing GitHub Pages publishing source remains the root of `main`.

Only approved public content and site implementation belong in this public repository. Research snapshots, manuscript drafts and review records belong in the private authoring environment.
