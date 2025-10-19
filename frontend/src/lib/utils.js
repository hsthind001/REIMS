import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge Tailwind CSS classes with proper precedence
 * This is the standard shadcn/ui utility function
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

















