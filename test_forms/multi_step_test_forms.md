# Multi-Step Forms for Testing FormGenius

This document contains a curated list of real multi-step forms found on the internet that can be used to test FormGenius's current capabilities and demonstrate its limitations with true multi-step form navigation.

## Real-World Multi-Step Forms

### 1. **Airbnb Registration**
- **URL**: https://www.airbnb.com/signup
- **Type**: User registration and profile completion
- **Steps**: 4-5 steps (Email → Verification → Profile → Preferences → Complete)
- **Features**: 
  - Progress indicator
  - Mobile-responsive design
  - Option to skip steps
  - Back/Next navigation
- **Test Focus**: User registration workflow

### 2. **Geico Insurance Quote**
- **URL**: https://www.geico.com/auto-insurance/
- **Type**: Auto insurance quote request
- **Steps**: 6-8 steps (Vehicle → Driver → Coverage → Contact → Quote)
- **Features**: 
  - Large radio buttons with images
  - Progress tracking
  - Conditional logic based on selections
  - Friendly mascot guidance
- **Test Focus**: Insurance quote generation

### 3. **N26 Bank Account Creation**
- **URL**: https://n26.com/en-us/bank-account
- **Type**: Digital bank account signup
- **Steps**: 5-7 steps (Country → Account Type → Personal Info → ID Verification → Complete)
- **Features**: 
  - Clear step list preview
  - Light/dark mode toggle
  - Conditional logic for different countries
  - Mobile-first design
- **Test Focus**: Financial services onboarding

### 4. **Stripe Account Setup**
- **URL**: https://dashboard.stripe.com/register
- **Type**: Payment processor account creation
- **Steps**: 4-6 steps (Business Info → Personal Info → Bank Details → Verification → Complete)
- **Features**: 
  - Real-time feedback at each step
  - Social proof elements
  - Security indicators
  - Clean, professional design
- **Test Focus**: Business account creation

### 5. **The Ordinary Skincare Quiz**
- **URL**: https://www.theordinary.com/en-us/regimen-builder
- **Type**: Product recommendation quiz
- **Steps**: 8-12 steps (Skin Type → Concerns → Routine → Preferences → Results)
- **Features**: 
  - Conversational format
  - Slider inputs
  - Time estimate display
  - Instant product recommendations
- **Test Focus**: Product recommendation workflow

### 6. **Ubersuggest SEO Tool Registration**
- **URL**: https://neilpatel.com/ubersuggest/
- **Type**: Lead magnet with tool access
- **Steps**: 3-5 steps (Website → Goals → Contact → Access)
- **Features**: 
  - One question per page
  - Personal guidance (Neil Patel's face)
  - Clear explanations for each question
  - Minimalist design
- **Test Focus**: Lead generation and tool access

### 7. **Little Passports Subscription Quiz**
- **URL**: https://www.littlepassports.com/
- **Type**: Product quiz and checkout
- **Steps**: 5-7 steps (Age Selection → Interests → Subscription → Checkout → Complete)
- **Features**: 
  - Colorful, kid-friendly design
  - Conditional product recommendations
  - Progress indicator
  - Playful interactions
- **Test Focus**: E-commerce subscription workflow

## SaaS Multi-Step Forms

### 8. **Zendesk Demo Request**
- **URL**: https://www.zendesk.com/demo/
- **Type**: Demo request form
- **Steps**: 8 steps
- **Features**: 
  - Overlaid on demo content
  - Single field per page
  - Casual, personable copy
- **Test Focus**: B2B demo request

### 9. **Intercom Setup**
- **URL**: https://www.intercom.com/
- **Type**: Customer communication platform setup
- **Steps**: 4-6 steps
- **Features**: 
  - Blue gradient background
  - Progress bar
  - One question per page minimalism
- **Test Focus**: SaaS onboarding

### 10. **Toptal Talent Application**
- **URL**: https://www.toptal.com/developers/join
- **Type**: Freelancer application
- **Steps**: 6-10 steps
- **Features**: 
  - Trust indicators with client logos
  - Single-choice questions
  - Meeting scheduling integration
- **Test Focus**: Professional application process

## CodePen Examples (For Development Testing)

### 11. **Modern Multi-Step Job Application**
- **URL**: https://codepen.io/bogdansandu/pen/[specific-pen-id]
- **Type**: Job application form demo
- **Features**: Modern UI, form validation, progress tracking

### 12. **Multi-Step Survey Form**
- **URL**: https://codepen.io/bogdansandu/pen/[specific-pen-id]
- **Type**: Survey/questionnaire demo
- **Features**: Clean design, multiple input types

### 13. **Course Enrollment Form**
- **URL**: https://codepen.io/bogdansandu/pen/[specific-pen-id]
- **Type**: Educational enrollment demo
- **Features**: Step-by-step course selection

## Testing Strategy

### Current FormGenius Limitations
Based on our previous analysis, FormGenius currently supports:
- ✅ Single-page multi-section forms
- ✅ Complex form field detection
- ✅ AI-powered data generation
- ❌ True multi-step navigation (Next/Previous buttons)
- ❌ Progress tracking across pages
- ❌ State management between steps

### Recommended Test Approach

1. **Start with Simple Forms**: Begin with CodePen examples that are accessible and well-documented
2. **Progress to Real Services**: Test with actual business forms (use test accounts where possible)
3. **Document Limitations**: Record where FormGenius fails to navigate between steps
4. **Identify Patterns**: Note common multi-step form patterns that need support

### Test Scenarios

For each form, test:
- **Form Detection**: Can FormGenius identify it as a multi-step form?
- **First Step Completion**: Can it fill the first step successfully?
- **Navigation**: Can it click "Next" or "Continue" buttons?
- **Step Progression**: Does it recognize when a new step loads?
- **Data Persistence**: Does generated data carry over between steps?
- **Error Handling**: How does it handle validation errors between steps?

## Expected Results

Given FormGenius's current implementation:
- **SUCCESS**: Single-page forms with multiple sections
- **PARTIAL SUCCESS**: First step of multi-step forms
- **FAILURE**: Complete multi-step form workflows
- **NEXT STEPS**: Implementation of true multi-step navigation support

This testing will help validate our README updates and provide concrete examples for future development priorities.
