# Senior Engineering Instructions: Speed Bump Tracker (Text-Only MVP)

## 1. Role & Context
You are a Senior Frontend Engineer building a "Text-Only" Progressive Web App (PWA) for field maintenance workers. The app focuses on high contrast, large touch targets, and offline resilience. You must prioritize code readability, strict TypeScript typing, and component modularity.

## 2. Technical Stack (Strict)
- **Framework:** Next.js 14+ (App Router).
- **Language:** TypeScript (Strict mode).
- **Styling:** Tailwind CSS (Mobile-first).
- **Icons:** `lucide-react`.
- **Backend:** Supabase (Client-side fetching via `supabase-js`).
- **Utilities:** `clsx` and `tailwind-merge` for dynamic classes.
- **Notifications:** `sonner` (or simple toast logic) for user feedback.
- **Constraint:** Do NOT use React Query/TanStack Query. Use `useEffect` and standard `fetch`.

## 3. Database & Type Definitions
### SQL Schema
```sql
create table speed_bumps (
  id uuid default gen_random_uuid() primary key,
  street_name text not null,
  exact_location text,
  status text default 'Good', -- 'Good' | 'Damaged' | 'Critical'
  last_updated timestamptz default now()
  car_count integer default 0,
);


TypeScript Interface
Create a types/index.ts file.

export type BumpStatus = 'Good' | 'Damaged' | 'Critical';

export interface SpeedBump {
  id: string;
  street_name: string;
  exact_location: string;
  status: BumpStatus;
  last_updated: string;
}

## 4. Architecture & File Structure
Do not dump everything in page.tsx. Use this modular structure:
/src
  /components
    /ui             # Reusable primitives (Button, Card, Input)
    /features       # Logic-heavy components (BumpList, BumpForm)
  /lib
    supabase.ts     # Client initialization
    utils.ts        # cn() helper for tailwind
  /app
    page.tsx        # Main Entry
    layout.tsx      # Global styles & fonts

This "Complex" version does not change your app's features (it's still text-only and uses simple fetching), but it forces Cursor to write Production-Grade Code.

It adds TypeScript interfaces, Error Handling (Toasts), Modular Component Structure, and Strict UI patterns.

Copy the content below into a file named instructions.md (or directly into Cursor).

Markdown

# Senior Engineering Instructions: Speed Bump Tracker (Text-Only MVP)

## 1. Role & Context
You are a Senior Frontend Engineer building a "Text-Only" Progressive Web App (PWA) for field maintenance workers. The app focuses on high contrast, large touch targets, and offline resilience. You must prioritize code readability, strict TypeScript typing, and component modularity.

## 2. Technical Stack (Strict)
- **Framework:** Next.js 14+ (App Router).
- **Language:** TypeScript (Strict mode).
- **Styling:** Tailwind CSS (Mobile-first).
- **Icons:** `lucide-react`.
- **Backend:** Supabase (Client-side fetching via `supabase-js`).
- **Utilities:** `clsx` and `tailwind-merge` for dynamic classes.
- **Notifications:** `sonner` (or simple toast logic) for user feedback.
- **Constraint:** Do NOT use React Query/TanStack Query. Use `useEffect` and standard `fetch`.

## 3. Database & Type Definitions
### SQL Schema
```sql
create table speed_bumps (
  id uuid default gen_random_uuid() primary key,
  street_name text not null,
  exact_location text,
  status text default 'Good', -- 'Good' | 'Damaged' | 'Critical'
  last_updated timestamptz default now()
);```
TypeScript Interfaces (Enforce this)
Create a types/index.ts file.

TypeScript

export type BumpStatus = 'Good' | 'Damaged' | 'Critical';

export interface SpeedBump {
  id: string;
  street_name: string;
  exact_location: string;
  status: BumpStatus;
  last_updated: string;
}

## 4. Architecture & File Structure
Do not dump everything in page.tsx. Use this modular structure:

Plaintext

/src
  /components
    /ui             # Reusable primitives (Button, Card, Input)
    /features       # Logic-heavy components (BumpList, BumpForm)
  /lib
    supabase.ts     # Client initialization
    utils.ts        # cn() helper for tailwind
  /app
    page.tsx        # Main Entry
    layout.tsx      # Global styles & fonts
## 5. Coding Standards & Rules
A. Data Fetching (Pattern)
Always use try/catch blocks inside useEffect.

Handle 3 states explicitly: loading (bool), error (string | null), data (SpeedBump[]).

Crucial: When a user updates a bumper, re-fetch the data list immediately to ensure UI consistency.

B. UI Component Rules
Status Colors: Create a centralized configuration object for colors to ensure consistency across the app.

TypeScript

const STATUS_CONFIG = {
  Good: 'bg-green-500 text-white',
  Damaged: 'bg-yellow-500 text-black',
  Critical: 'bg-red-600 text-white',
};
Touch Targets: All clickable elements (Buttons, List Rows) must have min-h-[60px] and py-4 to accommodate gloved hands.

Feedback:

Show a "Loading..." spinner/text during fetch.

Show a Toast/Alert on successful update ("Status Updated!").

Show a Red Alert on error.

C. The "Text-Only" Aesthetic
No Images: Do not use <img> tags. Visual hierarchy is established solely through Typography (Font Weight/Size) and Color Badges.

Typography:

Street Name: text-lg font-bold text-gray-900

Location: text-sm text-gray-500

6. Implementation Checklist for Cursor
Setup: Scaffold Next.js, install lucide-react clsx tailwind-merge @supabase/supabase-js.

Utils: Create lib/supabase.ts and lib/utils.ts (for class merging).

Components:

StatusBadge.tsx: Displays the colored strip/pill.

BumperCard.tsx: The list item component.

FilterTabs.tsx: The [All | Damaged] toggle.

Feature - List: Build BumperList.tsx that handles the fetching logic and state.

Feature - Edit: Build BumperActionModal.tsx that handles the update logic.