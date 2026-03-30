import type { Config } from 'tailwindcss'

const config: Config = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                background: '#0f172a',
                foreground: '#f8fafc',
                primary: '#3b82f6',
                secondary: '#1e293b',
                accent: '#10b981',
                warning: '#f59e0b',
                danger: '#ef4444'
            },
        },
    },
    plugins: [],
}
export default config
