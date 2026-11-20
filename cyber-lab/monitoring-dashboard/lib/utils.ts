import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function parsePaginationParams(
  searchParams: URLSearchParams,
  defaultLimit = 50,
  maxLimit = 100
) {
  const pageParam = searchParams.get('page');
  const limitParam = searchParams.get('limit');

  let page = 1;
  if (pageParam !== null) {
    const parsedPage = parseInt(pageParam, 10);
    if (!isNaN(parsedPage) && parsedPage >= 1) {
      page = Math.min(parsedPage, 1_000_000);
    }
  }

  let limit = defaultLimit;
  if (limitParam !== null) {
    const parsedLimit = parseInt(limitParam, 10);
    if (!isNaN(parsedLimit) && parsedLimit >= 1) {
      limit = Math.min(parsedLimit, maxLimit);
    }
  }

  const offset = (page - 1) * limit;

  return { page, limit, offset };
}
