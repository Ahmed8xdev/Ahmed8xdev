# GitHub Pages and Google Search Console setup

The native GitHub profile README is already live at https://github.com/Ahmed8xdev.

The interactive 3D experience is prepared in `docs/index.html`. A separate public Pages site must be enabled once before browsers and search engines can access it.

## Publish the interactive 3D site

Open https://github.com/Ahmed8xdev/Ahmed8xdev/settings/pages and choose the following values:

| Setting | Value |
| :--- | :--- |
| Build and deployment source | Deploy from a branch |
| Branch | main |
| Folder | /docs |

Select **Save**. The expected public URL is https://ahmed8xdev.github.io/Ahmed8xdev/.

The public site is not considered deployed until that URL returns an actual HTTP 200 and the 3D viewer loads.

## Connect Google Search Console

Once the Pages URL is live, add a new URL prefix property:

`https://ahmed8xdev.github.io/Ahmed8xdev/`

Verify ownership using a Search Console method supported for the Pages site. An HTML file verification method can be implemented in `docs/` once Google provides the verification file. An HTML meta tag can also be placed in `docs/index.html` when Google supplies the exact tag.

Submit the existing sitemap:

`https://ahmed8xdev.github.io/Ahmed8xdev/sitemap.xml`

Use URL Inspection to request indexing of the root portfolio URL, then check coverage and search performance after Google processes it.

## Search content strategy

The public page currently has a descriptive title, an informative meta description, semantic HTML sections, a canonical link, Open Graph metadata, accessible content, Person / ProfilePage structured data, and a sitemap.

Relevant technical topics are written in meaningful prose and include Model Context Protocol server development, MCP integrations, AI agent development, Python automation, PHP, Laravel, reverse engineering, IDA Pro, backend APIs and full stack engineering.

Strengthen search visibility with genuinely helpful public examples, clear project descriptions, original tutorials, real demonstrations, and relevant links from sites you control. Revisit titles and content only when backed by useful page changes.

Google does not use the `meta keywords` tag for ranking. Repeated keyword lists do not substitute for useful content, and indexing or top ranking cannot be guaranteed.

Official references:

https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

https://developers.google.com/search/docs/fundamentals/seo-starter-guide

https://support.google.com/webmasters/answer/7451001
