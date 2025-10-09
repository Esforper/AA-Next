import React from 'react';

interface ArticleContentProps {
  content: string;
  images: string[];
  imageEvery?: number; // kaç paragrafta bir resim yerleştirilsin
}

export const ArticleContent: React.FC<ArticleContentProps> = ({ content, images, imageEvery = 2 }) => {
  const parts = (content || '')
    .split(/\n{2,}|<\/p>|<br\s*\/?>/i)
    .map(s => s.trim())
    .filter(Boolean);

  let imageIdx = 0;
  const blocks: React.ReactNode[] = [];

  parts.forEach((p, idx) => {
    blocks.push(
      <p key={`p-${idx}`} className="mb-4 leading-7 text-[15px] text-gray-100">
        {p}
      </p>
    );
    if ((idx + 1) % imageEvery === 0 && imageIdx < images.length) {
      const src = images[imageIdx++];
      blocks.push(
        <figure key={`img-${idx}`} className="my-4">
          <img src={src} alt="" className="w-full rounded-lg" />
        </figure>
      );
    }
  });

  while (imageIdx < images.length) {
    const src = images[imageIdx++];
    blocks.push(
      <figure key={`img-tail-${imageIdx}`} className="my-4">
        <img src={src} alt="" className="w-full rounded-lg" />
      </figure>
    );
  }

  return <div>{blocks}</div>;
};

export default ArticleContent;

