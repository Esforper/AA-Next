import React from 'react';
import clsx from 'clsx';

const palette = {
  navy: '#0C2340',
  red: '#E10600',
  white: '#FFFFFF',
  gray: '#F4F4F4',
  blue: '#005799'
};

export const NewsCard = ({
  id,
  title,
  description,
  imageUrl,
  onReadMore,
  className
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer',
        'border border-gray-200 hover:border-gray-300',
        'transform hover:-translate-y-1',
        className
      )}
      style={{ backgroundColor: palette.white }}
      onClick={onReadMore}
    >
      {imageUrl ? (
        <div className="relative h-52 w-full overflow-hidden">
          <img
            src={imageUrl}
            alt={title}
            className="h-full w-full object-cover transform group-hover:scale-110 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent" />
          <div className="absolute top-3 right-3">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      ) : (
        <div className="h-52 w-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
          <div className="text-gray-400 text-4xl">📰</div>
        </div>
      )}

      <div className="p-5">
        <h3 className="text-lg font-bold leading-tight" style={{ color: palette.navy }}>
          {title}
        </h3>
        {description ? (
          <p className="mt-3 text-sm text-gray-600 line-clamp-3 leading-relaxed">{description}</p>
        ) : null}

        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onReadMore();
            }}
            className={clsx(
              'inline-flex items-center px-5 py-2.5 rounded-full text-sm font-semibold',
              'hover:scale-105 active:scale-95 transition-all duration-200',
              'shadow-md hover:shadow-lg',
              'text-white'
            )}
            style={{
              background: `linear-gradient(135deg, ${palette.blue} 0%, #003d73 100%)`,
              '&:hover': {
                background: `linear-gradient(135deg, #003d73 0%, ${palette.blue} 100%)`
              }
            }}
          >
            <span>Daha Fazla Oku</span>
            <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          
          <div className="flex items-center text-xs text-gray-400">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Şimdi</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsCard;


