# LOAF

An intelligent recipe assistant that provides conversational access to a knowledge base of recipes, with web search integration and automatic recipe extraction capabilities.

## Features

- **Interactive Chat Interface**: Natural language conversation with the recipe bot
- **Knowledge Base**: Curated collection of recipes with detailed information
- **Web Search Integration**: Automatically searches for recipes when KB confidence is low
- **Recipe Detection**: Extracts structured recipe data from web pages
- **Confidence Scoring**: Provides confidence levels and reasoning for recommendations
- **Smart Query Processing**: Understands cuisine preferences, spice levels, and cooking methods

## Quick Start

1. **Run the chat bot**:
   ```bash
   ./run.sh
   ```

2. **Manual setup** (if needed):
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start chat bot
   python chat.py
   ```

3. **Check environment**:
   ```bash
   ./run.sh --check
   ```

## Chat Interface

Once you run `./run.sh`, you'll enter an interactive chat session:

```
Welcome to Recipe Chat Bot!
==================================================
I can help you find recipes, cooking tips, and food suggestions.
Just ask me anything about food and cooking!

Commands:
  /help     - Show help message
  /recipes  - Show available recipes
  /stats    - Show session statistics
  /clear    - Clear conversation history
  /quit     - Exit the chat

Examples:
  'I want spicy noodles'
  'Korean kimchi recipe'
  'Easy pasta dish'
  'What can I make with chicken?'

You: I want spicy noodles
Bot: 
**Spicy Sichuan Noodles**
   Cuisine: Chinese
   Difficulty: medium
   Spice Level: extra-hot
   Time: 15 minutes + 10 minutes
   Servings: 2

**Ingredients:**
   • 200 g fresh noodles
   • 1 tsp Sichuan peppercorns
   • 2 tbsp chili oil
   • 3 cloves garlic
   • 1 inch ginger
   • 2 tbsp soy sauce
   • 1 tbsp rice vinegar
   • 2 stalks scallions
   • 1 tsp sesame oil

**Instructions:**
   1. Boil noodles according to package instructions until al dente
   2. Toast Sichuan peppercorns in a dry pan until fragrant
   3. Grind peppercorns to a fine powder
   4. Mince garlic and ginger
   5. Heat chili oil in a wok or large pan

**Confidence:** high (1.00)
**Reasoning:** High confidence match with score 1.00. Found strong keyword matches: name:noodles, tag:noodles, ingredient:fresh noodles
Processed in 0.00s
```

## Sample Query Results

**Query**: "I want spicy noodles"
- **Recipe**: Spicy Sichuan Noodles
- **Confidence**: High (1.00)
- **Cuisine**: Chinese
- **Spice Level**: Extra-hot
- **Needs Web**: False

**Query**: "Korean kimchi recipe"
- **Recipe**: None (not in KB)
- **Confidence**: Needs Web (0.00)
- **Needs Web**: True
- **Web Results**: 5 recipe candidates from AllRecipes, Food Network, etc.

## Knowledge Base

The system includes 5 sample recipes covering different cuisines and spice levels:

1. **Spicy Sichuan Noodles** (Chinese, Extra-hot)
2. **Miso Ramen** (Japanese, Mild)
3. **Spicy Pad Thai** (Thai, Hot)
4. **Creamy Mushroom Pasta** (Italian, Mild)
5. **Spicy Thai Green Curry** (Thai, Hot)

## How It Works - Complete Flow

### **User Query Processing**
• User enters a food query (e.g., "I want spicy noodles")
• **QueryProcessor** analyzes the query to extract:
  - Keywords (noodles, spicy, etc.)
  - Cuisine preferences (Chinese, Thai, etc.)
  - Spice level preferences (mild, hot, extra-hot)
  - Cooking method preferences (fried, boiled, etc.)
  - Difficulty preferences (easy, medium, hard)

### **Knowledge Base Search**
• **RecipeMatcher** searches through the curated recipe database
• Compares query keywords against recipe names, tags, and ingredients
• Calculates match scores based on keyword overlap and preferences
• **ConfidenceScorer** evaluates the match quality:
  - High confidence (≥0.8): Strong matches found
  - Medium confidence (≥0.5): Some relevant matches
  - Low confidence (≥0.2): Limited matches
  - Needs Web (<0.2): No strong matches in KB

### **Web Search Integration** (when confidence is low)
• **DuckDuckGoSearcher** scrapes DuckDuckGo HTML results
• Searches for recipe candidates using enhanced query terms
• **RecipeWebSearcher** filters and ranks results:
  - Prioritizes known recipe websites (AllRecipes, Food Network, etc.)
  - Scores results based on title/snippet relevance
  - Returns top 5 recipe candidates with URLs and snippets

### **Recipe Detection** (from web results)
• **RecipeDetector** extracts structured recipe data from web pages
• **StructuredDataExtractor** uses extruct to find:
  - JSON-LD schema.org Recipe markup
  - Microdata recipe information
• **HTMLFallbackExtractor** parses HTML when structured data unavailable:
  - Uses BeautifulSoup to navigate HTML structure
  - Regex patterns identify ingredients and instructions
  - Extracts cooking times, servings, ratings, nutrition info

### **Response Generation**
• **FullStackKBAnswerer** combines all results into unified response
• Formats recipe information with:
  - Recipe details (name, cuisine, difficulty, spice level)
  - Complete ingredient lists with amounts and units
  - Step-by-step cooking instructions
  - Confidence score and reasoning
  - Web search results (if applicable)

### **Interactive Chat Interface**
• **ChatBot** provides conversational interface
• Supports commands: `/help`, `/recipes`, `/stats`, `/clear`, `/quit`
• Displays formatted recipe responses with emojis and structure
• Tracks conversation history and session statistics
• Handles errors gracefully with user-friendly messages

### **System Architecture**
• **Modular Design**: Each component handles specific functionality
• **Pydantic Models**: Type-safe data structures throughout
• **Error Handling**: Graceful fallbacks when services fail
• **Mock Data**: Realistic test data when external services unavailable
• **Virtual Environment**: Isolated Python environment with `uv`
• **Easy Setup**: Single `./run.sh` command for complete setup

## Confidence Scoring

The system calculates confidence based on:
- **Keyword matches** (recipe name, tags, ingredients)
- **Cuisine preference alignment**
- **Spice level matching**
- **Difficulty preference**
- **Query specificity**

Confidence levels:
- **High** (≥0.8): Strong matches, likely to satisfy user
- **Medium** (≥0.5): Some relevant matches found
- **Low** (≥0.2): Limited matches, may not be ideal
- **Needs Web** (<0.2): No strong matches, web search recommended

## Web Search Features

- **DuckDuckGo Integration**: Scrapes DuckDuckGo HTML results for recipe candidates
- **Recipe Site Prioritization**: Ranks results from known recipe websites (AllRecipes, Food Network, etc.)
- **Automatic Fallback**: Triggers web search when KB confidence is low (<0.3)
- **Top 5 Results**: Returns up to 5 recipe candidates with URLs, titles, and snippets
- **Mock Results**: Provides realistic mock results when real search fails (for testing)

## Recipe Detection Features

- **Structured Data Extraction**: Uses extruct to extract JSON-LD and Microdata from HTML
- **Schema.org Support**: Recognizes Recipe schema with ingredients, instructions, timing, ratings
- **HTML Fallback Parsing**: BeautifulSoup-based extraction when structured data is unavailable
- **Pattern Matching**: Regex patterns to identify ingredients and cooking instructions
- **Confidence Scoring**: Calculates extraction confidence based on data completeness
- **Multiple Extraction Methods**: Tries structured data first, falls back to HTML parsing
- **Ingredient Parsing**: Extracts amounts, units, and names from ingredient text
- **Instruction Recognition**: Identifies cooking steps using keyword patterns

## Payment - Stripe Test Cards (Test Mode)

When developing with Stripe in **Test Mode** you should use Stripe's test card numbers — they simulate real card responses without moving real money.

**Common test cards**

- **Successful payment**  
  `4242 4242 4242 4242` — any future expiry, any 3-digit CVC, any ZIP → **succeeds**

- **Card declined**  
  `4000 0000 0000 0002` — simulates a card decline

- **3D Secure / SCA required (auth flow)**  
  `4000 0027 6000 3184` — triggers an authentication flow (useful to test 3D Secure)

**Format rules**
- **Expiry:** any future month/year (e.g., `12/34`)  
- **CVC:** any 3 digits (e.g., `123`)  
- **ZIP/postal:** any 5 digits (if required)

**Notes**
- Make sure Stripe Dashboard is set to **“View test data”** (Test Mode) when using these cards.  
- Test cards only work in Test Mode — they are invalid in Live Mode.  
- Use these cards to test success, declines, and authentication flows during development.
