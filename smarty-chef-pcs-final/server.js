const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();

app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname))); // Serve static files from root

const PORT = process.env.PORT || 3000;
const SPOONACULAR_API_KEY = process.env.SPOONACULAR_API_KEY;

if (!SPOONACULAR_API_KEY) {
  console.warn('⚠️  WARNING: SPOONACULAR_API_KEY is not set in environment variables.');
}

// Helper function to transform Spoonacular recipe data
function transformRecipe(recipe) {
  const ingredients = recipe.extendedIngredients 
    ? recipe.extendedIngredients.map(i => i.original)
    : [];
  let instructions = [];
  if (recipe.analyzedInstructions && recipe.analyzedInstructions.length) {
    instructions = recipe.analyzedInstructions[0].steps.map(step => step.step);
  } else if (recipe.instructions) {
    instructions = recipe.instructions.split(/[\r\n]+/).filter(Boolean);
  }
  const description = recipe.summary 
    ? recipe.summary.replace(/<[^>]*>/g, '').substring(0, 200) + '...'
    : 'A delicious recipe made with your selected ingredients.';

  return {
    title: recipe.title || 'Delicious Recipe',
    description,
    ingredients,
    instructions,
    time: recipe.readyInMinutes ? `${recipe.readyInMinutes} minutes` : '',
    dietary_labels: [
      recipe.vegetarian && 'Vegetarian',
      recipe.vegan && 'Vegan',
      recipe.glutenFree && 'Gluten-Free',
      recipe.dairyFree && 'Dairy-Free',
      recipe.veryHealthy && 'Healthy',
      ...(recipe.dishTypes || []),
      ...(recipe.cuisines || [])
    ].filter(Boolean),
    category: recipe.dishTypes ? recipe.dishTypes[0] : 'Main Course',
    servings: recipe.servings ? recipe.servings.toString() : '',
    image: recipe.image || '',
    sourceUrl: recipe.sourceUrl || '',
    spoonacularScore: recipe.spoonacularScore || 0,
    healthScore: recipe.healthScore || 0,
  };
}

// Fallback recipe generation when API unavailable or no results
function createFallbackRecipe(ingredients, dietaryPreference) {
  const mainIngredient = ingredients[0] || 'ingredients';
  const cuisineHint = dietaryPreference === 'indian' ? 'Indian-Style ' : '';

  return {
    title: `${cuisineHint}${mainIngredient.charAt(0).toUpperCase() + mainIngredient.slice(1)} Delight`,
    description: `A homemade ${cuisineHint.toLowerCase()} dish featuring ${ingredients.slice(0, 3).join(', ')}`,
    ingredients: [
      ...ingredients.map(i => `1-2 portions ${i}`),
      'Salt and pepper to taste',
      '2 tbsp cooking oil',
      'Fresh herbs (optional)',
      'Spices as needed'
    ],
    instructions: [
      'Wash and prepare all ingredients.',
      `Heat oil and cook ${ingredients[0]} until golden.`,
      ingredients.length > 1 ? `Add ${ingredients.slice(1).join(', ')} and cook 5-7 minutes.` : 'Cook 5-7 minutes.',
      'Season with salt, pepper and spices.',
      dietaryPreference === 'indian' ? 'Add turmeric, cumin, garam masala.' : 'Add herbs and spices to taste.',
      'Cook until tender and well combined.',
      'Serve hot and enjoy!',
    ],
    time: '25-30 minutes',
    dietary_labels: dietaryPreference ? [dietaryPreference] : ['Homemade'],
    category: 'Main Course',
    servings: '2-4',
    image: '',
    sourceUrl: '',
    spoonacularScore: 0,
    healthScore: 0,
  };
}

app.post('/generate-recipe', async (req, res) => {
  try {
    const { ingredients = [], dietaryPreference = '', allergies = '' } = req.body;

    if (!ingredients.length) {
      return res.status(400).json({ error: 'Please provide at least one ingredient', recipes: [] });
    }

    const fetch = (await import('node-fetch')).default;
    const ingredientsStr = ingredients.join(',+');
    const url = `https://api.spoonacular.com/recipes/findByIngredients?ingredients=${encodeURIComponent(ingredientsStr)}&number=8&ranking=2&ignorePantry=true&apiKey=${SPOONACULAR_API_KEY}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error(`Spoonacular API search failed: ${response.status}`);

    const foundRecipes = await response.json();

    if (!foundRecipes.length) {
      return res.json({ recipes: [createFallbackRecipe(ingredients, dietaryPreference)], apiSource: 'Fallback', message: 'No matches found' });
    }

    const detailedRecipes = await Promise.all(
      foundRecipes.slice(0,5).map(async (item) => {
        try {
          const detailUrl = `https://api.spoonacular.com/recipes/${item.id}/information?includeNutrition=false&apiKey=${SPOONACULAR_API_KEY}`;
          const dResp = await fetch(detailUrl);
          if (!dResp.ok) return null;
          const dData = await dResp.json();
          return transformRecipe(dData);
        } catch {
          return null;
        }
      })
    );

    let validRecipes = detailedRecipes.filter(Boolean);

    if (dietaryPreference) {
      const pref = dietaryPreference.toLowerCase().replace('-', ' ');
      validRecipes = validRecipes.filter(recipe => 
        recipe.dietary_labels.some(label => label.toLowerCase().includes(pref))
      );
    }

    if (allergies) {
      const allergs = allergies.split(',').map(a => a.trim().toLowerCase());
      validRecipes = validRecipes.filter(recipe => {
        const hText = (recipe.title + ' ' + recipe.ingredients.join(' ')).toLowerCase();
        return !allergs.some(all => hText.includes(all));
      });
    }

    if (validRecipes.length === 0) {
      validRecipes = [createFallbackRecipe(ingredients, dietaryPreference)];
    }

    res.json({ recipes: validRecipes, apiSource: 'Spoonacular', totalFound: foundRecipes.length, afterFiltering: validRecipes.length });

  } catch (err) {
    const { ingredients = [], dietaryPreference = '' } = req.body;
    res.json({
      recipes: [createFallbackRecipe(ingredients, dietaryPreference)],
      apiSource: 'Fallback',
      error: err.message,
      message: 'API unavailable, showing fallback recipe'
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: "✅ Smarty-Chef.PCS Server Running!",
    timestamp: new Date().toISOString(),
    apiKeyStatus: SPOONACULAR_API_KEY ? "✅ Configured" : "❌ Missing",
    version: "2.0.0"
  });
});

app.get('/api-status', async (req, res) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const testUrl = `https://api.spoonacular.com/recipes/random?number=1&apiKey=${SPOONACULAR_API_KEY}`;
    const resp = await fetch(testUrl);
    res.json({
      spoonacularAPI: resp.ok ? "✅ Connected" : "❌ Failed",
      statusCode: resp.status,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.json({
      spoonacularAPI: "❌ Connection Failed",
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    availableEndpoints: ['GET /', 'POST /generate-recipe', 'GET /health', 'GET /api-status']
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Smarty-Chef.PCS Server started on port ${PORT}`);
  console.log(`💻 Open http://localhost:${PORT}`);
  console.log(`🔑 API key status: ${SPOONACULAR_API_KEY ? 'Configured' : 'Missing'}`);
});

process.on('SIGTERM', () => {
  console.log('🔄 Server shutting down...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🔄 Server shutting down...');
  process.exit(0);
});