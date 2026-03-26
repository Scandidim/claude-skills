# Astro Core — Components, Routing, and Content Collections

## Project Structure

```
src/
├── components/       # Reusable .astro and framework components
├── layouts/          # Page wrapper layouts
├── pages/            # File-based routing (.astro, .md, .mdx)
│   └── [...slug].astro  # Dynamic catch-all route
├── content/
│   ├── config.ts     # Collection schemas (required)
│   └── blog/         # Markdown/MDX files for 'blog' collection
├── styles/           # Global CSS (imported sparingly)
└── assets/           # Static assets processed by astro:assets
astro.config.mjs
```

## Component Syntax

```astro
---
// Frontmatter: TypeScript executed at build time (SSG) or request time (SSR)
import { getCollection } from 'astro:content';
import Layout from '../layouts/Base.astro';

const posts = await getCollection('blog', ({ data }) => !data.draft);
const { title } = Astro.props;
---

<!-- Template: HTML with expressions -->
<Layout title={title}>
  <ul>
    {posts.map(post => (
      <li>
        <a href={`/blog/${post.slug}`}>{post.data.title}</a>
        <time>{post.data.pubDate.toLocaleDateString()}</time>
      </li>
    ))}
  </ul>
</Layout>

<style>
  /* Scoped by default — no leakage */
  ul { list-style: none; }
</style>
```

## Content Collections

### Defining Collections (src/content/config.ts)

```typescript
import { defineCollection, reference, z } from 'astro:content';

const blog = defineCollection({
  type: 'content', // 'content' for MD/MDX, 'data' for JSON/YAML
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      description: z.string().max(160),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      heroImage: image().optional(),       // typed image reference
      author: reference('authors'),        // cross-collection reference
      tags: z.array(z.string()).default([]),
      draft: z.boolean().default(false),
    }),
});

const authors = defineCollection({
  type: 'data',
  schema: z.object({
    name: z.string(),
    bio: z.string(),
    avatar: z.string().url(),
  }),
});

export const collections = { blog, authors };
```

### Querying Collections

```typescript
import { getCollection, getEntry, render } from 'astro:content';

// All published posts, sorted by date
const posts = await getCollection('blog', ({ data }) => !data.draft);
posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());

// Single entry by slug
const post = await getEntry('blog', 'my-first-post');
if (!post) return Astro.redirect('/404');

// Render MDX/Markdown to component
const { Content, headings, remarkPluginFrontmatter } = await render(post);
```

### Dynamic Routes from Collections

```astro
---
// src/pages/blog/[...slug].astro
import { getCollection, render } from 'astro:content';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map(post => ({
    params: { slug: post.slug },
    props: { post },
  }));
}

const { post } = Astro.props;
const { Content, headings } = await render(post);
---

<article>
  <h1>{post.data.title}</h1>
  <Content />
</article>
```

## SSG vs SSR vs Hybrid

```typescript
// astro.config.mjs
export default defineConfig({
  output: 'static',    // default — full SSG, no server required
  // output: 'server', // full SSR — requires adapter
  // output: 'hybrid', // SSG by default, opt-in SSR per page
});
```

**Per-page SSR opt-in (hybrid mode):**

```astro
---
// This page renders on every request
export const prerender = false;

const data = await fetch('https://api.example.com/live').then(r => r.json());
---
<p>Live data: {data.value}</p>
```

## Island Architecture — Partial Hydration

```astro
---
import Counter from '../components/Counter.tsx'; // React/Vue/Svelte component
---

<!-- No JS — static HTML only -->
<Counter />

<!-- Hydrate immediately on load (use sparingly) -->
<Counter client:load />

<!-- Hydrate when visible in viewport -->
<Counter client:visible />

<!-- Hydrate when browser is idle -->
<Counter client:idle />

<!-- Hydrate only on media query match -->
<Counter client:media="(max-width: 768px)" />

<!-- Pass state; hydrate on visible -->
<Counter initialCount={5} client:visible />
```

**When to use each directive:**
- `client:visible` — default choice for most interactive components
- `client:idle` — low-priority widgets (chat bubbles, analytics)
- `client:load` — above-the-fold critical interactivity only
- `client:media` — responsive UI that differs by breakpoint

## Image Optimization

```astro
---
import { Image, Picture } from 'astro:assets';
import heroImg from '../assets/hero.png'; // local image — type-safe
---

<!-- Optimized local image -->
<Image src={heroImg} alt="Hero" width={800} height={400} format="webp" />

<!-- Art direction with multiple formats -->
<Picture
  src={heroImg}
  formats={['avif', 'webp']}
  alt="Hero"
  width={800}
/>

<!-- Remote image — requires allowedDomains config -->
<Image src="https://example.com/photo.jpg" alt="Remote" width={600} height={400} inferSize />
```

## View Transitions

```astro
---
// src/layouts/Base.astro
import { ViewTransitions } from 'astro:transitions';
---

<head>
  <ViewTransitions />
</head>

<!-- Named transition for cross-page animation -->
<img src={hero} transition:name={`hero-${post.slug}`} />
```

## Adapters for SSR

```bash
# Node.js
npx astro add node

# Vercel
npx astro add vercel

# Cloudflare Pages
npx astro add cloudflare

# Netlify
npx astro add netlify
```

```typescript
// astro.config.mjs (Node adapter example)
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

## Common Integrations

```bash
npx astro add react        # React islands
npx astro add vue          # Vue islands
npx astro add svelte       # Svelte islands
npx astro add tailwind     # Tailwind CSS
npx astro add mdx          # MDX support
npx astro add sitemap      # Automatic sitemap
npx astro add partytown    # Off-main-thread scripts
```

## Performance Checklist

- [ ] Images use `<Image />` from `astro:assets`
- [ ] Islands use `client:visible` or `client:idle` (not `client:load`)
- [ ] Content served from collections, not manual file reads
- [ ] External fonts use `display: swap` or `preload`
- [ ] `astro sync` run after schema changes
- [ ] `astro check` passes with no type errors
- [ ] Bundle size audited with `astro build --verbose`

## Anti-Patterns

```astro
---
// BAD — manual file reading instead of content collections
import fs from 'fs';
const posts = JSON.parse(fs.readFileSync('./data/posts.json'));

// GOOD
import { getCollection } from 'astro:content';
const posts = await getCollection('blog');
---

<!-- BAD — raw img tag bypasses optimization -->
<img src="/hero.png" alt="Hero" />

<!-- GOOD -->
<Image src={heroImg} alt="Hero" width={800} height={400} />
```
