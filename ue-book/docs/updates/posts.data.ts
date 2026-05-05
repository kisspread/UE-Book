import { createContentLoader } from 'vitepress'

export interface Post {
  title: string
  url: string
  date: string
  excerpt: string | undefined
}

declare const data: Post[]
export { data }

export default createContentLoader('updates/*.md', {
  excerpt: true,
  transform(raw): Post[] {
    return raw
      .filter(p => p.url !== '/updates/')
      .map(({ url, frontmatter, excerpt }) => ({
        title: frontmatter.title || url.split('/').pop()?.replace(/-/g, ' ') || '',
        url,
        date: frontmatter.date || url.split('/').pop()?.replace('.html', '') || '',
        excerpt: excerpt?.replace(/<[^>]+>/g, '').substring(0, 120) || '',
      }))
      .sort((a, b) => b.date.localeCompare(a.date))
  }
})
