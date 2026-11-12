// @ts-check  PROTOTYPE — variant B
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://j-alencar.github.io',
	base: '/smell-wiki-prototype/starlight',
	trailingSlash: 'always',
	integrations: [
		starlight({
			title: 'Data Smell Wiki',
			customCss: ['./src/styles/tree.css'],
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/j-alencar/smell-wiki-prototype' }],
			sidebar: [
				{ label: 'Smell tree', link: '/' },
				{ label: 'Time-series', items: [{ autogenerate: { directory: 'time-series' } }] },
				{ label: 'Numeric', collapsed: true, items: [{ autogenerate: { directory: 'numeric' } }] },
				{ label: 'Text', collapsed: true, items: [{ autogenerate: { directory: 'text' } }] },
				{ label: 'Profiling tasks', collapsed: true, items: [{ autogenerate: { directory: 'tasks' } }] },
				{ label: 'Non-relational data', link: '/non-relational/' },
			],
		}),
	],
});
