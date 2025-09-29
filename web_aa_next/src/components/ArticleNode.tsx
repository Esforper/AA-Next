// src/components/ArticleNode.tsx

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import clsx from 'clsx';
import { ArticleData } from '../models';
import { Card } from './Card'; // Mevcut Card component'ini kullanıyoruz

// Component'in alacağı props'ları tanımlıyoruz.
// React Flow, 'data' prop'u içinde node oluştururken verdiğimiz veriyi gönderir.
interface ArticleNodeProps {
  data: {
    article: ArticleData;
  };
  // 'isConnectable' prop'u React Flow tarafından otomatik olarak sağlanır.
  isConnectable: boolean;
}

// React.memo kullanarak component'in gereksiz yere yeniden render edilmesini engelliyoruz.
// Bu, özellikle büyük grafiklerde performansı artırır.
export const ArticleNode: React.FC<ArticleNodeProps> = memo(({ data, isConnectable }) => {
  const { article } = data;

  if (!article) {
    return null; // Eğer bir nedenle article verisi yoksa, hiçbir şey render etme.
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <>
      {/* 
        Handle component'leri, bu düğümün diğer düğümlerle nereden bağlanacağını belirtir.
        'Top' handle, gelen bağlantılar için. 'Bottom' handle, giden bağlantılar için.
      */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        className="!bg-gray-400"
      />

      <Card
        padding="sm"
        shadow="md"
        rounded="lg"
        className={clsx(
          'w-64 border-2 border-transparent hover:border-blue-500 transition-all duration-200 ease-in-out',
          'cursor-pointer group' // Grup olarak hover efektlerini yönetmek için
        )}
      >
        {article.main_image && (
          <div className="relative h-24 mb-2 rounded-md overflow-hidden">
            <img
              src={article.main_image}
              alt={article.title}
              className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
            <span className="absolute top-1.5 left-1.5 px-2 py-0.5 text-xs font-semibold bg-blue-600/90 text-white rounded-full">
              {article.category}
            </span>
          </div>
        )}

        <div className="px-1">
          <h3 className="text-sm font-semibold text-gray-900 line-clamp-2 leading-tight mb-1">
            {article.title}
          </h3>
          <p className="text-xs text-gray-600 line-clamp-3 mb-2">
            {article.summary}
          </p>
        </div>

        <div className="flex justify-between items-center text-xs text-gray-400 pt-2 border-t border-gray-100 px-1">
          <span>{formatDate(article.published_date)}</span>
          <div className="flex flex-wrap gap-1 justify-end">
            {article.tags.slice(0, 2).map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600">
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </Card>

      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        className="!bg-gray-400"
      />
    </>
  );
});