# MDX and Content Authoring in Astro

## MDX Setup

```bash
npx astro add mdx
```

```typescript
// astro.config.mjs
import mdx from '@astrojs/mdx';
import remarkGfm from 'remark-gfm';
import rehypePrettyCode from 'rehype-pretty-code';

export default defineConfig({
  integrations: [
    mdx({
      remarkPlugins: [remarkGfm],
      rehypePlugins: [[rehypePrettyCode, { theme: 'github-dark' }]],
      optimize: true, // Tree-shake unused components
    }),
  ],
});
```

## Content Collection Schemas with Zod

```typescript
// src/content/config.ts
import { defineCollection, reference, z } from 'astro:content';

// Reusable schema fragments
const seoSchema = z.object({
  title: z.string().max(60),
  description: z.string().max(160),
  ogImage: z.string().url().optional(),
  noIndex: z.boolean().default(false),
});

const blog = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    seoSchema.extend({
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      heroImage: image().optional(),
      author: reference('authors'),
      categories: z.array(z.enum(['tutorial', 'news', 'release', 'guide'])),
      readingTime: z.number().optional(),  // computed in remark plugin
      draft: z.boolean().default(false),
      featured: z.boolean().default(false),
    }),
});

const changelog = defineCollection({
  type: 'data',   // JSON or YAML — no body rendering
  schema: z.object({
    version: z.string().regex(/^\d+\.\d+\.\d+$/),
    date: z.coerce.date(),
    breaking: z.boolean().default(false),
    changes: z.array(
      z.object({
        type: z.enum(['added', 'changed', 'fixed', 'removed', 'security']),
        description: z.string(),
      })
    ),
  }),
});

export const collections = { blog, changelog };
```

## Writing MDX

### Basic MDX File

```mdx
---
title: Getting Started
description: Learn how to use our SDK in 5 minutes
pubDate: 2024-01-15
author: jane-doe
categories:
  - tutorial
---

import { Steps, Aside } from '@astrojs/starlight/components';
import CodeSandbox from '../../components/CodeSandbox.astro';

## Overview

This guide walks you through installation and first use.

<Aside type="tip">
  You can also use the interactive sandbox below to follow along.
</Aside>

<Steps>
1. Install the package:
   ```bash
   npm install @my/sdk
   ```
2. Initialize the client:
   ```typescript
   import { createClient } from '@my/sdk';
   const client = createClient({ apiKey: process.env.API_KEY });
   ```
3. Make your first call:
   ```typescript
   const result = await client.query({ id: 'example' });
   console.log(result);
   ```
</Steps>

<CodeSandbox template="my-sdk-starter" />
```

### Dynamic Content in MDX

```mdx
---
title: API Reference
---

export const endpoints = [
  { method: 'GET', path: '/users', description: 'List all users' },
  { method: 'POST', path: '/users', description: 'Create a user' },
];

## Endpoints

<table>
  <thead>
    <tr><th>Method</th><th>Path</th><th>Description</th></tr>
  </thead>
  <tbody>
    {endpoints.map(({ method, path, description }) => (
      <tr key={path}>
        <td><code>{method}</code></td>
        <td><code>{path}</code></td>
        <td>{description}</td>
      </tr>
    ))}
  </tbody>
</table>
```

## Rendering Content in Pages

```astro
---
// src/pages/blog/[slug].astro
import { getCollection, getEntry, render } from 'astro:content';
import type { CollectionEntry } from 'astro:content';

export async function getStaticPaths() {
  const posts = await getCollection('blog', ({ data }) => !data.draft);
  return posts.map(post => ({ params: { slug: post.slug }, props: { post } }));
}

interface Props { post: CollectionEntry<'blog'> }

const { post } = Astro.props;
const { Content, headings, remarkPluginFrontmatter } = await render(post);
---

<article>
  <header>
    <h1>{post.data.title}</h1>
    <time datetime={post.data.pubDate.toISOString()}>
      {post.data.pubDate.toLocaleDateString('en-US', { dateStyle: 'long' })}
    </time>
  </header>

  <!-- Table of contents from headings -->
  <nav aria-label="Table of contents">
    <ul>
      {headings
        .filter(h => h.depth <= 3)
        .map(h => <li style={`padding-left: ${(h.depth - 2) * 1}rem`}>
          <a href={`#${h.slug}`}>{h.text}</a>
        </li>)
      }
    </ul>
  </nav>

  <Content />
</article>
```

## Custom Remark/Rehype Plugins

### Reading Time Plugin

```typescript
// src/plugins/reading-time.ts
import type { Root } from 'mdast';
import { toString } from 'mdast-util-to-string';
import getReadingTime from 'reading-time';

export function remarkReadingTime() {
  return function (tree: Root, { data }: { data: Record<string, unknown> }) {
    const textOnPage = toString(tree);
    const readingTime = getReadingTime(textOnPage);
    (data.astro as Record<string, unknown>).frontmatter = {
      ...(data.astro as Record<string, unknown>).frontmatter,
      readingTime: Math.ceil(readingTime.minutes),
    };
  };
}
```

```typescript
// astro.config.mjs
import { remarkReadingTime } from './src/plugins/reading-time.ts';

export default defineConfig({
  markdown: {
    remarkPlugins: [remarkReadingTime],
  },
});
```

## Global MDX Components

Register components available in all MDX files without importing:

```typescript
// astro.config.mjs
export default defineConfig({
  integrations: [
    mdx({
      components: {
        // Override standard HTML elements
        h2: './src/components/HeadingWithAnchor.astro',
        img: './src/components/ResponsiveImage.astro',
        a: './src/components/SmartLink.astro',
        // Add custom components
        Callout: './src/components/Callout.astro',
      },
    }),
  ],
});
```

## Content Querying Patterns

```typescript
// Pagination
const PAGE_SIZE = 10;
const page = Number(Astro.url.searchParams.get('page') ?? 1);
const allPosts = await getCollection('blog', ({ data }) => !data.draft);
const sorted = allPosts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
const posts = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
const totalPages = Math.ceil(sorted.length / PAGE_SIZE);

// Filter by category
const tutorials = await getCollection('blog', ({ data }) =>
  data.categories.includes('tutorial') && !data.draft
);

// Group by year
const byYear = allPosts.reduce<Record<number, typeof allPosts>>((acc, post) => {
  const year = post.data.pubDate.getFullYear();
  acc[year] = [...(acc[year] ?? []), post];
  return acc;
}, {});

// Cross-collection — resolve reference
const post = await getEntry('blog', 'my-post');
const author = await getEntry(post.data.author); // resolves reference
```

## Type Safety

```typescript
import type { CollectionEntry, CollectionKey } from 'astro:content';

// Typed component props
interface Props {
  post: CollectionEntry<'blog'>;
}

// Generic card component
interface CardProps<T extends CollectionKey> {
  entry: CollectionEntry<T>;
}

// Infer frontmatter type
type BlogFrontmatter = CollectionEntry<'blog'>['data'];
```

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Type errors after schema change | Stale type cache | Run `astro sync` |
| Component not found in MDX | Missing import | Import at top of `.mdx` file or register as global |
| Images not optimized in MDX | Using `<img>` directly | Use `<Image />` import or configure `img` override |
| Content not updating in dev | Cached collection | Restart `astro dev` |
| `reference()` returns undefined | Missing referenced entry | Check slug matches filename exactly |
| Remark plugin not applying | Wrong config location | Add to `markdown.remarkPlugins`, not integration options |
