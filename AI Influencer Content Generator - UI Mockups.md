# AI Influencer Content Generator - UI Mockups

## Dashboard Design

The dashboard will feature a clean, professional interface with a dark theme that highlights content and provides easy access to all main functions.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR                                 [User] ▼        │
├─────────────┬───────────────────────────────────────────────────────────┤
│             │                                                           │
│  DASHBOARD  │  MY PERSONAS                                   + CREATE   │
│             │                                                           │
│  PERSONAS   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│             │  │         │  │         │  │         │  │         │      │
│  IMAGES     │  │  Sophia │  │  Alex   │  │  Maya   │  │   New   │      │
│             │  │         │  │         │  │         │  │ Persona │      │
│  VIDEOS     │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│             │                                                           │
│  TEMPLATES  │  RECENT CONTENT                                           │
│             │                                                           │
│  SETTINGS   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐      │
│             │  │         │  │         │  │         │  │         │      │
│             │  │ Image 1 │  │ Image 2 │  │ Video 1 │  │ Video 2 │      │
│             │  │         │  │         │  │         │  │         │      │
│             │  └─────────┘  └─────────┘  └─────────┘  └─────────┘      │
│             │                                                           │
└─────────────┴───────────────────────────────────────────────────────────┘
```

## Persona Creation Interface

The persona creation interface will guide users through a step-by-step process with visual feedback.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR > CREATE PERSONA                    [User] ▼    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CREATE YOUR AI PERSONA                                                 │
│                                                                         │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │                       │  │                                       │  │
│  │                       │  │  PERSONA DETAILS                      │  │
│  │                       │  │                                       │  │
│  │                       │  │  Name: ___________________            │  │
│  │                       │  │                                       │  │
│  │   UPLOAD REFERENCE    │  │  Age: [18-25] [26-35] [36-45] [46+]   │  │
│  │        IMAGE          │  │                                       │  │
│  │                       │  │  Style:                               │  │
│  │         or            │  │  ○ Professional  ○ Casual             │  │
│  │                       │  │  ○ Artistic     ○ Athletic            │  │
│  │  DESCRIBE APPEARANCE  │  │  ○ Glamorous    ○ Custom              │  │
│  │                       │  │                                       │  │
│  │                       │  │  Personality traits:                  │  │
│  │                       │  │  ☑ Confident    ☑ Creative            │  │
│  │                       │  │  ☐ Serious      ☐ Playful             │  │
│  │                       │  │  ☐ Mysterious   ☐ Friendly            │  │
│  └───────────────────────┘  │                                       │  │
│                             └───────────────────────────────────────┘  │
│                                                                         │
│  [BACK]                                                      [NEXT]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Content Generation Interface

The content generation interface will provide intuitive controls for creating various types of content.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR > GENERATE CONTENT                  [User] ▼    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  GENERATE CONTENT                                                       │
│                                                                         │
│  Selected Persona: Sophia ▼                                             │
│                                                                         │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │                       │  │                                       │  │
│  │                       │  │  CONTENT SETTINGS                     │  │
│  │                       │  │                                       │  │
│  │                       │  │  Content Type:                        │  │
│  │                       │  │  ○ Portrait    ○ Full Body            │  │
│  │     PERSONA           │  │  ○ Action      ○ Social Post          │  │
│  │      PREVIEW          │  │                                       │  │
│  │                       │  │  Setting:                             │  │
│  │                       │  │  ○ Studio      ○ Outdoor              │  │
│  │                       │  │  ○ Urban       ○ Nature               │  │
│  │                       │  │  ○ Custom: _________________          │  │
│  │                       │  │                                       │  │
│  │                       │  │  Additional Prompt:                   │  │
│  │                       │  │  ┌─────────────────────────────────┐  │  │
│  │                       │  │  │                                 │  │  │
│  │                       │  │  └─────────────────────────────────┘  │  │
│  └───────────────────────┘  │                                       │  │
│                             │  Quantity: [1] [4] [9] [16]           │  │
│                             │                                       │  │
│                             └───────────────────────────────────────┘  │
│                                                                         │
│  [BACK]                                                  [GENERATE]     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Video Creation Interface

The video creation interface will provide options for animating images or performing face swaps.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR > CREATE VIDEO                      [User] ▼    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CREATE VIDEO                                                           │
│                                                                         │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │                       │  │                                       │  │
│  │                       │  │  VIDEO SETTINGS                       │  │
│  │                       │  │                                       │  │
│  │                       │  │  Video Type:                          │  │
│  │                       │  │  ○ Animate Image                      │  │
│  │     SELECTED          │  │  ○ Face Swap                          │  │
│  │      IMAGE            │  │                                       │  │
│  │                       │  │  For Animation:                       │  │
│  │                       │  │  Motion: ○ Subtle  ○ Medium  ○ Strong │  │
│  │                       │  │                                       │  │
│  │                       │  │  For Face Swap:                       │  │
│  │                       │  │  Template: _________________ [Browse] │  │
│  │                       │  │                                       │  │
│  │                       │  │  Duration: [5s] [10s] [15s] [Custom]  │  │
│  │                       │  │                                       │  │
│  │                       │  │  Quality: ○ Draft  ○ Standard  ○ High │  │
│  └───────────────────────┘  │                                       │  │
│                             └───────────────────────────────────────┘  │
│                                                                         │
│  [BACK]                                                  [CREATE]       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Gallery Interface

The gallery interface will provide organized access to all generated content with filtering and batch operations.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR > GALLERY                           [User] ▼    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  CONTENT GALLERY                        [FILTER ▼]  [SORT ▼]  [SEARCH] │
│                                                                         │
│  Persona: All ▼    Type: All ▼    Date: Newest First ▼                 │
│                                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │         │  │         │  │         │  │         │  │         │       │
│  │ Content │  │ Content │  │ Content │  │ Content │  │ Content │       │
│  │    1    │  │    2    │  │    3    │  │    4    │  │    5    │       │
│  │         │  │         │  │         │  │         │  │         │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │         │  │         │  │         │  │         │  │         │       │
│  │ Content │  │ Content │  │ Content │  │ Content │  │ Content │       │
│  │    6    │  │    7    │  │    8    │  │    9    │  │   10    │       │
│  │         │  │         │  │         │  │         │  │         │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                                         │
│  Selected: 0                                                            │
│                                                                         │
│  [SELECT ALL]  [DESELECT]  [DOWNLOAD]  [SHARE]  [DELETE]  [EDIT]       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Export Interface

The export interface will provide options for downloading or sharing content across platforms.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ AI INFLUENCER GENERATOR > EXPORT                            [User] ▼    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  EXPORT CONTENT                                                         │
│                                                                         │
│  Selected Items: 3                                                      │
│                                                                         │
│  ┌───────────────────────┐  ┌───────────────────────────────────────┐  │
│  │                       │  │                                       │  │
│  │  ┌─────┐  ┌─────┐     │  │  EXPORT SETTINGS                      │  │
│  │  │     │  │     │     │  │                                       │  │
│  │  │  1  │  │  2  │     │  │  Format:                              │  │
│  │  │     │  │     │     │  │  ○ Original  ○ Optimized for Web      │  │
│  │  └─────┘  └─────┘     │  │  ○ High Res  ○ Social Media Ready     │  │
│  │                       │  │                                       │  │
│  │  ┌─────┐              │  │  Platform Optimization:               │  │
│  │  │     │              │  │  ○ None      ○ Instagram              │  │
│  │  │  3  │              │  │  ○ TikTok    ○ YouTube                │  │
│  │  │     │              │  │  ○ Twitter   ○ Facebook               │  │
│  │  └─────┘              │  │                                       │  │
│  │                       │  │  Include Metadata:                    │  │
│  │  SELECTED ITEMS       │  │  ☑ Persona Info  ☑ Generation Details │  │
│  │                       │  │  ☐ Prompts       ☐ Technical Data     │  │
│  │                       │  │                                       │  │
│  └───────────────────────┘  └───────────────────────────────────────┘  │
│                                                                         │
│  [BACK]                [DOWNLOAD]    [SHARE DIRECTLY]                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Mobile Responsive Design

All interfaces will be responsive and optimized for mobile devices with simplified controls.

```
┌───────────────────────┐
│ AI INFLUENCER GEN ≡   │
├───────────────────────┤
│                       │
│  MY PERSONAS          │
│                       │
│  ┌─────┐  ┌─────┐     │
│  │     │  │     │     │
│  │  1  │  │  2  │     │
│  │     │  │     │     │
│  └─────┘  └─────┘     │
│                       │
│  RECENT CONTENT       │
│                       │
│  ┌─────┐  ┌─────┐     │
│  │     │  │     │     │
│  │  1  │  │  2  │     │
│  │     │  │     │     │
│  └─────┘  └─────┘     │
│                       │
│  [+ CREATE NEW]       │
│                       │
└───────────────────────┘
```

## Color Scheme and Visual Design

- **Primary Color**: Deep purple (#5D3FD3)
- **Secondary Color**: Teal accent (#00CED1)
- **Background**: Dark gradient (#121212 to #1E1E1E)
- **Text**: White (#FFFFFF) and light gray (#E0E0E0)
- **Accent**: Bright highlights for important actions (#FF5757)

## Typography

- **Headings**: Poppins, Semi-Bold
- **Body Text**: Inter, Regular
- **Buttons and UI Elements**: Inter, Medium

## Design Elements

- Subtle drop shadows for depth
- Rounded corners (8px radius) for cards and containers
- Minimal animations for transitions
- High-contrast icons for clarity
- Progress indicators for all processing operations
