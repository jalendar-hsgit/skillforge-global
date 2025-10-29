import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <meta name="theme-color" content="#0B0A13" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}
