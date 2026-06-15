import React from 'react';

export default function LoadingState() {
  return (
    <section className="flex flex-col gap-md animate-fadeIn">
      <h2 className="font-title-md text-title-md text-on-surface font-semibold">Curating Recommendations...</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
        
        {/* Skeleton Card 1 */}
        <div className="glass-panel-2 rounded-xl overflow-hidden flex flex-col h-[400px]">
          <div className="h-[200px] bg-surface-variant skeleton-pulse w-full"></div>
          <div className="p-md flex flex-col gap-sm flex-1">
            <div className="flex justify-between items-start">
              <div className="h-6 w-2/3 bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-6 w-12 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="flex gap-2 mb-2">
              <div className="h-5 w-16 bg-surface-variant skeleton-pulse rounded-full"></div>
              <div className="h-5 w-20 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="pl-3 border-l-4 border-surface-variant h-full mt-auto flex flex-col gap-2 justify-end">
              <div className="h-4 w-full bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-4 w-5/6 bg-surface-variant skeleton-pulse rounded"></div>
            </div>
          </div>
        </div>

        {/* Skeleton Card 2 */}
        <div className="glass-panel-2 rounded-xl overflow-hidden flex flex-col h-[400px]">
          <div className="h-[200px] bg-surface-variant skeleton-pulse w-full opacity-80"></div>
          <div className="p-md flex flex-col gap-sm flex-1">
            <div className="flex justify-between items-start">
              <div className="h-6 w-3/4 bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-6 w-12 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="flex gap-2 mb-2">
              <div className="h-5 w-14 bg-surface-variant skeleton-pulse rounded-full"></div>
              <div className="h-5 w-24 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="pl-3 border-l-4 border-surface-variant h-full mt-auto flex flex-col gap-2 justify-end">
              <div className="h-4 w-11/12 bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-4 w-4/5 bg-surface-variant skeleton-pulse rounded"></div>
            </div>
          </div>
        </div>

        {/* Skeleton Card 3 */}
        <div className="glass-panel-2 rounded-xl overflow-hidden flex flex-col h-[400px]">
          <div className="h-[200px] bg-surface-variant skeleton-pulse w-full opacity-60"></div>
          <div className="p-md flex flex-col gap-sm flex-1">
            <div className="flex justify-between items-start">
              <div className="h-6 w-1/2 bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-6 w-12 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="flex gap-2 mb-2">
              <div className="h-5 w-20 bg-surface-variant skeleton-pulse rounded-full"></div>
              <div className="h-5 w-16 bg-surface-variant skeleton-pulse rounded-full"></div>
            </div>
            <div className="pl-3 border-l-4 border-surface-variant h-full mt-auto flex flex-col gap-2 justify-end">
              <div className="h-4 w-full bg-surface-variant skeleton-pulse rounded"></div>
              <div className="h-4 w-3/4 bg-surface-variant skeleton-pulse rounded"></div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
