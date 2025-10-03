import React from 'react';
import clsx from 'clsx';

const palette = {
  navy: '#0C2340',
  red: '#E10600',
  white: '#FFFFFF',
  gray: '#F4F4F4'
};

export const NewsCard = ({
  title,
  description,
  imageUrl,
  onReadMore,
  className
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden group',
        'border border-gray-100',
        className
      )}
      style={{ backgroundColor: palette.white }}
    >
      {imageUrl ? (
        <div className="relative h-48 w-full overflow-hidden">
          <img
            src={imageUrl}
            alt={title}
            className="h-full w-full object-cover transform group-hover:scale-105 transition-transform duration-300"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
        </div>
      ) : null}

      <div className="p-4">
        <h3 className="text-lg font-semibold" style={{ color: palette.navy }}>
          {title}
        </h3>
        {description ? (
          <p className="mt-2 text-sm text-gray-700 line-clamp-3">{description}</p>
        ) : null}

        <button
          onClick={onReadMore}
          className={clsx(
            'mt-4 inline-flex items-center px-4 py-2 rounded-full text-sm font-medium',
            'hover:-translate-y-0.5 active:translate-y-0 transition-all duration-200',
            'shadow-sm'
          )}
          style={{ backgroundColor: palette.red, color: palette.white }}
        >
          Daha Fazla Oku
        </button>
      </div>
    </div>
  );
};

export default NewsCard;


