import zipfile
import os
from io import BytesIO

# Create a zip file with all the necessary files for Smarty-Chef.PCS
zip_buffer = BytesIO()

# Files content to include in the zip
files_content = {
    'package.json': '''{
  "name": "smarty-chef-pcs",
  "version": "2.0.0",
  "description": "AI-powered smart recipe app with 500+ ingredients and Spoonacular API",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "body-parser": "^1.20.2",
    "node-fetch": "^3.3.2"
  },
  "engines": {
    "node": ">=14.0.0"
  },
  "author": "Clement",
  "license": "MIT",
  "keywords": ["recipe", "api", "spoonacular", "indian", "cooking"]
}''',

    'server.js': '''const express = require('express');
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
    instructions = recipe.instructions.split(/[\\r\\n]+/).filter(Boolean);
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
});''',

    'app.js': '''// 500 Global Ingredients with categorized search UI
const ingredients = {
  vegetables: [
    "Spinach", "Kale", "Cabbage", "Broccoli", "Cauliflower", "Carrot", "Potato", "Sweet Potato",
    "Yam", "Taro", "Eggplant (Aubergine)", "Zucchini (Courgette)", "Pumpkin", "Butternut Squash",
    "Bell Pepper (Red)", "Bell Pepper (Green)", "Bell Pepper (Yellow)", "Tomato", "Cherry Tomato",
    "Okra", "Green Beans", "Snow Peas", "Sugar Snap Peas", "Brussel Sprouts", "Asparagus",
    "Celery", "Fennel Bulb", "Radish", "Beetroot", "Turnip", "Parsnip", "Leek", "Onion (Yellow)",
    "Onion (Red)", "Shallot", "Spring Onion (Scallion)", "Garlic", "Ginger Root", "Lotus Root",
    "Bamboo Shoots", "Daikon Radish", "Bitter Gourd", "Chayote", "Cassava", "Water Chestnut",
    "Kohlrabi", "Artichoke", "Mushroom (Button)", "Mushroom (Shiitake)", "Mushroom (Oyster)",
    "Mushroom (Portobello)", "Mushroom (Enoki)", "Mushroom (Maitake)", "Seaweed (Nori)",
    "Seaweed (Kombu)", "Seaweed (Wakame)", "Seaweed (Hijiki)", "Edamame", "Cucumber", "Gherkin",
    "Lettuce (Romaine)", "Lettuce (Iceberg)", "Lettuce (Butterhead)", "Arugula (Rocket)", "Endive",
    "Watercress", "Mustard Greens", "Collard Greens", "Swiss Chard", "Moringa Leaves"
  ],
  fruits: [
    "Apple (Red Delicious)", "Apple (Granny Smith)", "Pear", "Quince", "Banana", "Plantain", "Mango",
    "Papaya", "Pineapple", "Guava", "Lychee", "Longan", "Rambutan", "Mangosteen", "Passion Fruit",
    "Dragon Fruit", "Kiwi", "Strawberry", "Blueberry", "Raspberry", "Blackberry", "Cranberry", "Grape (Red)",
    "Grape (Green)", "Grape (Concord)", "Cherry", "Sour Cherry", "Plum", "Apricot", "Peach", "Nectarine",
    "Persimmon", "Fig", "Date", "Pomegranate", "Orange", "Mandarin", "Clementine", "Tangerine", "Grapefruit",
    "Lemon", "Lime", "Kumquat", "Yuzu", "Pomelo", "Durian", "Jackfruit", "Breadfruit", "Coconut",
    "Avocado", "Olive (Green)", "Olive (Black)", "Starfruit (Carambola)", "Sapodilla", "Soursop (Graviola)",
    "Tamarind", "Gooseberry", "Amla (Indian Gooseberry)", "Mulberry", "Cloudberry", "Elderberry",
    "Boysenberry", "Currant (Black)", "Currant (Red)", "Currant (White)", "Loquat", "Medlar", "Jujube",
    "Baobab Fruit", "Ackee"
  ],
  grains_legumes_seeds: [
    "Rice (Basmati)", "Rice (Jasmine)", "Rice (Arborio)", "Rice (Brown)", "Rice (Wild)", "Wheat (Durum)",
    "Wheat (Whole)", "Bulgur", "Couscous", "Barley", "Rye", "Spelt", "Farro", "Millet", "Teff", "Quinoa (White)",
    "Quinoa (Red)", "Quinoa (Black)", "Buckwheat", "Amaranth", "Sorghum", "Maize (Yellow Corn)", "White Corn",
    "Hominy", "Polenta", "Lentils (Red)", "Lentils (Green)", "Lentils (Black Beluga)", "Lentils (Brown)",
    "Chickpeas (Garbanzo)", "Black Beans", "Kidney Beans", "Pinto Beans", "Navy Beans", "Cannellini Beans",
    "Mung Beans", "Adzuki Beans", "Soybeans", "Fava Beans", "Broad Beans", "Lima Beans", "Pigeon Peas",
    "Split Peas (Yellow)", "Split Peas (Green)", "Peanuts", "Sunflower Seeds", "Pumpkin Seeds (Pepitas)",
    "Sesame Seeds (White)", "Sesame Seeds (Black)", "Flaxseeds", "Chia Seeds", "Poppy Seeds", "Hemp Seeds",
    "Mustard Seeds (Yellow)", "Mustard Seeds (Brown)", "Caraway Seeds", "Cumin Seeds", "Nigella Seeds",
    "Coriander Seeds", "Fennel Seeds", "Fenugreek Seeds", "Celery Seeds", "Dill Seeds", "Anise Seeds",
    "Cardamom Pods (Green)", "Cardamom Pods (Black)", "Cloves", "Cinnamon Sticks", "Cassia Bark", "Nutmeg",
    "Mace", "Star Anise", "Allspice", "Black Peppercorns", "White Peppercorns", "Green Peppercorns",
    "Pink Peppercorns", "Sichuan Peppercorns", "Vanilla Bean", "Tonka Bean"
  ],
  dairy_eggs: [
    "Cow's Milk", "Goat's Milk", "Sheep's Milk", "Buffalo Milk", "Yogurt", "Kefir", "Buttermilk", "Cream",
    "Sour Cream", "Clotted Cream", "Butter", "Ghee", "Cheese (Cheddar)", "Cheese (Parmesan)", "Cheese (Mozzarella)",
    "Cheese (Feta)", "Cheese (Ricotta)", "Cheese (Paneer)", "Cheese (Halloumi)", "Cheese (Brie)", "Cheese (Camembert)",
    "Cheese (Blue Cheese)", "Cheese (Roquefort)", "Cheese (Gorgonzola)", "Cheese (Manchego)", "Cheese (Queso Fresco)",
    "Cheese (Cotija)", "Cheese (Gruyère)", "Cheese (Emmental)", "Cheese (Provolone)", "Cheese (Monterey Jack)",
    "Cheese (Swiss)", "Cheese (Cream Cheese)", "Cheese (Mascarpone)", "Cheese (Burrata)", "Egg (Chicken)", "Egg (Duck)",
    "Egg (Quail)", "Egg (Goose)", "Egg (Turkey)"
  ],
  indian_dairy: [
    "Paneer", "Khoya (Mawa)", "Chhena", "Dahi (Curd/Yogurt)", "Mishti Doi", "Lassi (Sweet)", "Lassi (Salted)", "Shrikhand",
    "Ghee (Desi)", "White Butter (Makkhan)", "Malai (Clotted Cream)", "Rabri", "Kulfi Base (Milk Reduction)",
    "Chaas (Buttermilk)", "Pedha Base (Milk Solid)", "Sandesh Base (Chhena Mix)", "Kalakand Base (Thickened Milk)",
    "Rasgulla Syrup Base (Chhena Balls)", "Rasmalai Base (Chhena + Cream)", "Khoa-based Barfi Mix"
  ],
  indian_grains_flours_pulses: [
    "Toor Dal (Pigeon Pea)", "Chana Dal (Bengal Gram)", "Moong Dal (Split Green Gram)", "Urad Dal (Black Gram)",
    "Masoor Dal (Red Lentil)", "Horse Gram (Kulthi)", "Rajma (Kidney Bean)", "Kabuli Chana (White Chickpea)",
    "Kala Chana (Black Chickpea)", "Moth Beans (Matki)", "Green Gram Whole (Sabut Moong)",
    "Masoor Whole (Brown Lentil)", "Lobia (Black-eyed Pea)", "Soybean (Indian Variety)", "Bajra (Pearl Millet)",
    "Jowar (Sorghum)", "Ragi (Finger Millet)", "Kodo Millet", "Foxtail Millet", "Barnyard Millet",
    "Little Millet", "Amaranth Seeds (Rajgira)", "Poha (Flattened Rice)", "Idli Rice (Parboiled)",
    "Basmati Rice", "Sona Masoori Rice", "Kolam Rice", "Matta Rice (Kerala Red)", "Ambemohar Rice (Maharashtra)",
    "Black Rice (Chakhao, Manipur)", "Atta (Whole Wheat Flour)", "Maida (Refined Wheat Flour)",
    "Besan (Gram Flour)", "Suji (Rava, Semolina)", "Rice Flour", "Jowar Flour", "Bajra Flour",
    "Ragi Flour", "Cornmeal (Makki ka Atta)", "Sattu (Roasted Gram Flour)", "Multigrain Flour Mix",
    "Dalia (Broken Wheat)", "Vermicelli (Roasted Semolina)", "Sevai (Rice Vermicelli)", "Papad Base (Urad Flour)",
    "Sabudana (Tapioca Pearls)", "Idiyappam Flour (Rice Noodles)", "Appam Batter (Fermented Rice-Coconut)",
    "Dhokla Batter (Rice + Lentil)", "Adai Batter (Mixed Lentil)"
  ],
  indian_vegetables_fruits: [
    "Tindora (Ivy Gourd)", "Turai (Ridge Gourd)", "Lauki (Bottle Gourd)", "Karela (Bitter Gourd)", "Kundru (Ivy Gourd)",
    "Parwal (Pointed Gourd)", "Bhindi (Okra)", "Drumstick Pods (Moringa)", "Methi Leaves (Fenugreek)", "Palak (Spinach)",
    "Amaranth Leaves (Chaulai Saag)", "Sarson ka Saag (Mustard Greens)", "Bathua Saag (Chenopodium)",
    "Colocasia Leaves (Arbi ke Patte)", "Colocasia Root (Arbi)", "Yam (Suran)", "Elephant Foot Yam (Oal)",
    "Ash Gourd (Petha)", "Snake Gourd (Chichinda)", "Sponge Gourd (Nenua)", "Green Mango", "Raw Banana",
    "Jackfruit (Kathal, Raw)", "Ripe Jackfruit", "Guava (Indian Variety)", "Custard Apple (Sitaphal)",
    "Jamun (Java Plum)", "Bael Fruit", "Wood Apple (Kothbel)", "Karonda (Bengal Currant)", "Ber (Indian Jujube)",
    "Tamarind (Imli)", "Kokum (Garcinia Indica)", "Amla (Indian Gooseberry)", "Nimbu (Indian Lemon)",
    "Mosambi (Sweet Lime)", "Paan Leaves (Betel Leaf)", "Lotus Stem (Kamal Kakdi)", "Banana Stem", "Banana Flower",
    "Gongura (Roselle Leaves)", "Red Pumpkin (Kaddu)", "White Pumpkin (Ash Gourd)", "Small Brinjal (Eggplant Varieties)",
    "Green Chillies (Indian)", "Red Chillies (Byadgi)", "Kashmiri Red Chillies", "Bhavnagari Chillies",
    "Banana Pepper (Indian Variety)", "Curry Leaves", "Neem Flowers (Edible)", "Banana Leaf (Cooking Wrapper)",
    "Jackfruit Seeds", "Starfruit (Kamrakh)", "Sapota (Chikoo)", "Mango (Alphonso)", "Mango (Dasheri)",
    "Mango (Langda)", "Mango (Totapuri)", "Mango (Banganapalli)"
  ],
  indian_herbs_spices: [
    "Hing (Asafoetida)", "Ajwain (Carom Seeds)", "Kalonji (Nigella Seeds)", "Radhuni Seeds (Bengali Spice)",
    "Stone Flower (Dagad Phool)", "Black Cardamom", "Green Cardamom", "Clove", "Cinnamon (Indian Cassia)",
    "Bay Leaf (Tej Patta)", "Star Anise", "Fennel Seeds (Saunf)", "Fenugreek Seeds (Methi)", "Mustard Seeds (Black)",
    "Mustard Seeds (Yellow)", "Coriander Seeds (Dhania)", "Cumin Seeds (Jeera)", "Peppercorns (Malabar Black)",
    "Long Pepper (Pippali)", "Turmeric Root (Haldi)", "Dried Turmeric Powder", "Dry Ginger (Sonth)",
    "Curry Powder (Madras Mix)", "Garam Masala Blend", "Panch Phoron (Bengali 5-spice)", "Rasam Powder",
    "Sambar Powder", "Chaat Masala", "Chana Masala Mix", "Pav Bhaji Masala", "Tandoori Masala", "Vindaloo Masala",
    "Kolhapuri Masala", "Malvani Masala", "Goda Masala (Maharashtrian)", "Biryani Masala",
    "Hyderabadi Haleem Masala", "Fish Curry Masala", "Pickle Masala (Achar Masala)", "Dry Coconut (Kopra)",
    "Dry Red Chillies (Guntur)", "Green Cardamom Powder", "Kashmiri Chilli Powder", "Mango Powder (Amchur)",
    "Pomegranate Seeds (Anardana)", "Black Salt (Kala Namak)", "Rock Salt (Sendha Namak)", "White Poppy Seeds (Khus Khus)",
    "Black Sesame Seeds", "Curry Leaf Powder"
  ],
  condiments_pickles: [
    "Tamarind Paste", "Kokum Syrup", "Jaggery (Gur)", "Palm Jaggery (Karupatti)", "Nolen Gur (Date Palm Jaggery)",
    "Pickled Mango (Aam ka Achar)", "Pickled Lemon (Nimbu ka Achar)", "Pickled Green Chilli", "Pickled Garlic",
    "Pickled Red Carrot (Punjabi)", "Pickled Amla", "Pickled Gongura", "Pickled Bamboo Shoot (NE India)",
    "Pickled Fish (Assamese)", "Pickled Shrimp (Goan)", "Chutney (Coconut)", "Chutney (Mint)", "Chutney (Coriander)",
    "Chutney (Tomato-Onion)", "Chutney (Tamarind-Date)"
  ],
  meats_seafood_oils: [
    "Chicken", "Duck", "Turkey", "Pork", "Beef", "Lamb", "Goat", "Rabbit", "Venison", "Kangaroo", "Salmon",
    "Tuna", "Sardine", "Cod", "Mackerel", "Prawns", "Lobster", "Crab", "Octopus", "Squid", "Anchovy",
    "Clams", "Mussels", "Scallops", "Oysters", "Sea Urchin (Uni)", "Shark", "Eel", "Hilsa Fish (India)",
    "Rohu Fish (India)", "Tilapia", "Seer Fish (Surmai)", "Mustard Oil", "Coconut Oil", "Sesame Oil (Gingelly Oil)",
    "Peanut Oil", "Sunflower Oil", "Rice Bran Oil", "Olive Oil (Extra Virgin)", "Grape Seed Oil"
  ]
};

// UI variables
let selectedIngredients = [];
let currentView = 'home';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
  setupEventListeners();
  renderIngredientSelection();
  updateSelectedIngredientsUI();
});

function setupEventListeners() {
  // Navigation
  document.getElementById('homeBtn').addEventListener('click', () => showView('home'));
  document.getElementById('ingredientsBtn').addEventListener('click', () => showView('ingredients'));
  document.getElementById('recipesBtn').addEventListener('click', () => showView('recipes'));
  document.getElementById('aboutBtn').addEventListener('click', () => showView('about'));

  // Search
  const searchInput = document.getElementById('ingredientSearch');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => renderIngredientSelection(e.target.value));
  }

  // Recipe generation
  const generateBtn = document.getElementById('generateRecipes');
  if (generateBtn) {
    generateBtn.addEventListener('click', generateRecipes);
  }

  // Clear ingredients
  const clearBtn = document.getElementById('clearIngredients');
  if (clearBtn) {
    clearBtn.addEventListener('click', clearIngredients);
  }
}

function showView(view) {
  const views = ['home', 'ingredients', 'recipes', 'about'];
  views.forEach(v => {
    const element = document.getElementById(v + 'View');
    if (element) {
      element.style.display = v === view ? 'block' : 'none';
    }
  });
  
  // Update nav buttons
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(view + 'Btn').classList.add('active');
  
  currentView = view;
  
  if (view === 'ingredients') {
    renderIngredientSelection();
  }
}

function renderIngredientSelection(filter = '') {
  const container = document.getElementById('ingredientContainer');
  if (!container) return;
  
  container.innerHTML = '';
  
  Object.keys(ingredients).forEach(category => {
    const categoryItems = ingredients[category].filter(item =>
      item.toLowerCase().includes(filter.toLowerCase())
    );
    
    if (categoryItems.length === 0) return;
    
    // Category header
    const categoryHeader = document.createElement('div');
    categoryHeader.className = 'category-header';
    categoryHeader.innerHTML = `
      <h3>${formatCategoryName(category)}</h3>
      <span class="category-count">${categoryItems.length} items</span>
    `;
    container.appendChild(categoryHeader);
    
    // Ingredients grid
    const grid = document.createElement('div');
    grid.className = 'ingredients-grid';
    
    categoryItems.forEach(ingredient => {
      const card = document.createElement('div');
      card.className = `ingredient-card ${selectedIngredients.includes(ingredient) ? 'selected' : ''}`;
      card.innerHTML = `
        <span class="ingredient-name">${ingredient}</span>
        <span class="ingredient-action">+</span>
      `;
      
      card.addEventListener('click', () => toggleIngredient(ingredient));
      grid.appendChild(card);
    });
    
    container.appendChild(grid);
  });
}

function formatCategoryName(category) {
  return category.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase());
}

function toggleIngredient(ingredient) {
  const index = selectedIngredients.indexOf(ingredient);
  if (index > -1) {
    selectedIngredients.splice(index, 1);
  } else {
    selectedIngredients.push(ingredient);
  }
  
  updateSelectedIngredientsUI();
  renderIngredientSelection(document.getElementById('ingredientSearch')?.value || '');
}

function updateSelectedIngredientsUI() {
  const container = document.getElementById('selectedIngredients');
  const count = document.getElementById('selectedCount');
  
  if (count) {
    count.textContent = selectedIngredients.length;
  }
  
  if (!container) return;
  
  if (selectedIngredients.length === 0) {
    container.innerHTML = '<p class="empty-state">No ingredients selected</p>';
    return;
  }
  
  container.innerHTML = selectedIngredients.map(ingredient => `
    <span class="selected-ingredient">
      ${ingredient}
      <button onclick="toggleIngredient('${ingredient}')" class="remove-btn">&times;</button>
    </span>
  `).join('');
}

function clearIngredients() {
  selectedIngredients = [];
  updateSelectedIngredientsUI();
  renderIngredientSelection(document.getElementById('ingredientSearch')?.value || '');
}

async function generateRecipes() {
  if (selectedIngredients.length === 0) {
    alert('Please select at least one ingredient');
    return;
  }
  
  const generateBtn = document.getElementById('generateRecipes');
  const recipesContainer = document.getElementById('recipesContainer');
  
  if (generateBtn) generateBtn.disabled = true;
  if (recipesContainer) recipesContainer.innerHTML = '<div class="loading">🍳 Generating recipes...</div>';
  
  try {
    const dietaryPreference = document.getElementById('dietaryPreference')?.value || '';
    const allergies = document.getElementById('allergies')?.value || '';
    
    const response = await fetch('/generate-recipe', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ingredients: selectedIngredients,
        dietaryPreference,
        allergies
      })
    });
    
    const data = await response.json();
    
    if (data.recipes && data.recipes.length > 0) {
      displayRecipes(data.recipes);
      showView('recipes');
    } else {
      throw new Error('No recipes found');
    }
    
  } catch (error) {
    console.error('Error generating recipes:', error);
    if (recipesContainer) {
      recipesContainer.innerHTML = `
        <div class="error-state">
          <h3>Oops! Something went wrong</h3>
          <p>Unable to generate recipes. Please try again.</p>
          <button onclick="generateRecipes()">Try Again</button>
        </div>
      `;
    }
  } finally {
    if (generateBtn) generateBtn.disabled = false;
  }
}

function displayRecipes(recipes) {
  const container = document.getElementById('recipesContainer');
  if (!container) return;
  
  container.innerHTML = recipes.map(recipe => `
    <div class="recipe-card">
      <div class="recipe-header">
        <h3>${recipe.title}</h3>
        <div class="recipe-meta">
          <span class="recipe-time">⏱️ ${recipe.time}</span>
          <span class="recipe-servings">👥 ${recipe.servings}</span>
        </div>
      </div>
      
      <p class="recipe-description">${recipe.description}</p>
      
      <div class="recipe-labels">
        ${recipe.dietary_labels.map(label => `<span class="dietary-label">${label}</span>`).join('')}
      </div>
      
      <div class="recipe-section">
        <h4>Ingredients</h4>
        <ul class="ingredients-list">
          ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
        </ul>
      </div>
      
      <div class="recipe-section">
        <h4>Instructions</h4>
        <ol class="instructions-list">
          ${recipe.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
        </ol>
      </div>
      
      ${recipe.sourceUrl ? `<a href="${recipe.sourceUrl}" target="_blank" class="recipe-source">View Original Recipe</a>` : ''}
    </div>
  `).join('');
}

// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/service-worker.js')
      .then(function(registration) {
        console.log('ServiceWorker registration successful');
      }, function(err) {
        console.log('ServiceWorker registration failed: ', err);
      });
  });
}''',

    'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍳 Smarty-Chef.PCS - AI Recipe Generator</title>
    <meta name="description" content="AI-powered smart recipe generator with 500+ ingredients. Create delicious recipes based on your available ingredients.">
    <link rel="manifest" href="/manifest.json">
    <link rel="icon" type="image/png" sizes="192x192" href="/icon-192.jpg">
    <link rel="icon" type="image/png" sizes="512x512" href="/icon-512.jpg">
    <meta name="theme-color" content="#ff6b35">
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">
                <h1>🍳 Smarty-Chef.PCS</h1>
            </div>
            <div class="nav-menu">
                <button id="homeBtn" class="nav-btn active">🏠 Home</button>
                <button id="ingredientsBtn" class="nav-btn">🥬 Ingredients</button>
                <button id="recipesBtn" class="nav-btn">📋 Recipes</button>
                <button id="aboutBtn" class="nav-btn">ℹ️ About</button>
            </div>
        </div>
    </nav>

    <!-- Home View -->
    <div id="homeView" class="view">
        <div class="hero-section">
            <div class="hero-content">
                <h2>🍳 Welcome to Smarty-Chef.PCS</h2>
                <p>Transform your available ingredients into delicious recipes with the power of AI and 500+ global ingredients!</p>
                <div class="hero-stats">
                    <div class="stat">
                        <span class="stat-number">500+</span>
                        <span class="stat-label">Global Ingredients</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">365K+</span>
                        <span class="stat-label">Real Recipes</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">11</span>
                        <span class="stat-label">Categories</span>
                    </div>
                </div>
                <button onclick="showView('ingredients')" class="cta-button">Start Cooking 🚀</button>
            </div>
        </div>
    </div>

    <!-- Ingredients View -->
    <div id="ingredientsView" class="view" style="display: none;">
        <div class="ingredients-section">
            <div class="section-header">
                <h2>🥬 Select Your Ingredients</h2>
                <p>Choose from over 500 global ingredients organized by category</p>
            </div>
            
            <!-- Search and Filters -->
            <div class="controls-panel">
                <div class="search-container">
                    <input type="search" id="ingredientSearch" placeholder="🔍 Search ingredients..." class="search-input">
                </div>
                
                <div class="filters-container">
                    <select id="dietaryPreference" class="filter-select">
                        <option value="">Any Diet</option>
                        <option value="vegetarian">Vegetarian</option>
                        <option value="vegan">Vegan</option>
                        <option value="gluten-free">Gluten-Free</option>
                        <option value="dairy-free">Dairy-Free</option>
                        <option value="indian">Indian Cuisine</option>
                    </select>
                    
                    <input type="text" id="allergies" placeholder="Allergies (comma-separated)" class="filter-input">
                </div>
            </div>

            <!-- Selected Ingredients -->
            <div class="selected-section">
                <h3>Selected Ingredients (<span id="selectedCount">0</span>)</h3>
                <div id="selectedIngredients" class="selected-ingredients">
                    <p class="empty-state">No ingredients selected</p>
                </div>
                <div class="selected-actions">
                    <button id="clearIngredients" class="btn-secondary">Clear All</button>
                    <button id="generateRecipes" class="btn-primary">Generate Recipes 🍳</button>
                </div>
            </div>

            <!-- Ingredients Container -->
            <div id="ingredientContainer" class="ingredients-container">
                <!-- Ingredients will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <!-- Recipes View -->
    <div id="recipesView" class="view" style="display: none;">
        <div class="recipes-section">
            <div class="section-header">
                <h2>📋 Your Generated Recipes</h2>
                <p>Delicious recipes crafted from your selected ingredients</p>
            </div>
            
            <div id="recipesContainer" class="recipes-container">
                <div class="empty-state">
                    <h3>No recipes generated yet</h3>
                    <p>Select some ingredients first to generate amazing recipes!</p>
                    <button onclick="showView('ingredients')" class="btn-primary">Select Ingredients</button>
                </div>
            </div>
        </div>
    </div>

    <!-- About View -->
    <div id="aboutView" class="view" style="display: none;">
        <div class="about-section">
            <div class="section-header">
                <h2>ℹ️ About Smarty-Chef.PCS</h2>
                <p>Your AI-powered cooking companion</p>
            </div>
            
            <div class="about-content">
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>🌍 Global Ingredients</h3>
                        <p>Choose from 500+ ingredients spanning vegetables, fruits, grains, spices, and more from around the world.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🤖 AI-Powered</h3>
                        <p>Advanced AI technology combined with Spoonacular API to generate personalized recipes.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🇮🇳 Indian Cuisine Focus</h3>
                        <p>Specialized collection of Indian ingredients, spices, and traditional cooking methods.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔍 Smart Search</h3>
                        <p>Intelligent ingredient search and filtering to find exactly what you're looking for.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📱 Mobile Ready</h3>
                        <p>Responsive design that works perfectly on mobile devices and can be installed as a PWA.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🍽️ Dietary Support</h3>
                        <p>Support for vegetarian, vegan, gluten-free and other dietary preferences and allergies.</p>
                    </div>
                </div>
                
                <div class="creator-section">
                    <h3>👨‍💻 Made with ❤️ by Clement</h3>
                    <p>Smarty-Chef.PCS combines beautiful design with powerful functionality to make cooking accessible and fun for everyone.</p>
                </div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>'''
}

# Create the final zip file
with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for filename, content in files_content.items():
        zip_file.writestr(filename, content)
    
    # Add additional files
    zip_file.writestr('README.md', '''# 🍳 Smarty-Chef.PCS - FINAL VERSION

## 🎉 Complete AI Recipe Generator with 500+ Ingredients

This is the **ULTIMATE FINAL VERSION** of Smarty-Chef.PCS with:

### ✨ Key Features:
- **500+ Global Ingredients** categorized and searchable
- **Real Spoonacular API Integration** with 365K+ recipes
- **Beautiful Mobile-Responsive UI** 
- **Indian Cuisine Specialization** with authentic ingredients
- **Smart Search & Filtering** across all categories
- **PWA Ready** - Install as mobile app
- **Dietary Preferences** - Vegetarian, Vegan, Gluten-Free support
- **Allergy Awareness** with filtering

### 🚀 Quick Deploy to Render:

1. **Upload to GitHub**
   - Create new repository
   - Upload all files from this zip

2. **Deploy on Render**
   - Connect GitHub repo
   - Build Command: `npm install`  
   - Start Command: `npm start`
   - Environment Variables:
     - `SPOONACULAR_API_KEY`: Your Spoonacular API key
     - `PORT`: 10000

3. **Environment Variables**
   Set in Render dashboard:
   ```
   SPOONACULAR_API_KEY = 7800762921d34589b4b49897b5c09778
   PORT = 10000
   ```

### 🛠️ Local Development:
```bash
npm install
npm start
# Open http://localhost:3000
```

### 📱 Features Overview:
- **Home Page**: Beautiful landing with stats
- **Ingredients Page**: 500+ ingredients with search
- **Recipes Page**: Generated recipes with details
- **About Page**: Feature overview

### 🌟 Made by Clement

This version includes everything needed for a production-ready recipe app!

**🎯 Perfect for deployment with zero configuration required!**
''')
    
    zip_file.writestr('manifest.json', '''{
  "name": "Smarty-Chef.PCS",
  "short_name": "SmartyChef",
  "description": "AI-powered smart recipe generator with 500+ global ingredients",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#ff6b35",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icon-192.jpg",
      "sizes": "192x192",
      "type": "image/jpeg",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.jpg", 
      "sizes": "512x512",
      "type": "image/jpeg",
      "purpose": "any maskable"
    }
  ],
  "categories": ["food", "lifestyle", "productivity"],
  "lang": "en",
  "dir": "ltr",
  "scope": "/",
  "prefer_related_applications": false
}''')

    zip_file.writestr('service-worker.js', '''const CACHE_NAME = 'smarty-chef-pcs-v2.0.0';
const urlsToCache = [
  '/',
  '/app.js',
  '/style.css',
  '/manifest.json',
  '/icon-192.jpg',
  '/icon-512.jpg'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});''')

    zip_file.writestr('style.css', '''/* Reset and Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}

/* Navigation */
.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.nav-brand h1 {
  color: #ff6b35;
  font-size: 1.5rem;
  font-weight: bold;
}

.nav-menu {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  background: none;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.nav-btn:hover {
  background: #f0f0f0;
}

.nav-btn.active {
  background: #ff6b35;
  color: white;
}

/* Views */
.view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* Hero Section */
.hero-section {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  margin: 2rem 0;
  backdrop-filter: blur(10px);
}

.hero-content h2 {
  font-size: 3rem;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-content p {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 2rem;
  margin: 2rem 0;
}

.stat {
  background: rgba(255, 255, 255, 0.2);
  padding: 1.5rem;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: bold;
  color: #ffd700;
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.cta-button {
  background: linear-gradient(135deg, #ff6b35, #f7931e);
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(255, 107, 53, 0.6);
}

/* Section Headers */
.section-header {
  text-align: center;
  margin-bottom: 2rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 15px;
  backdrop-filter: blur(10px);
}

.section-header h2 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.section-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

/* Controls Panel */
.controls-panel {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.search-container {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #ff6b35;
  box-shadow: 0 0 10px rgba(255, 107, 53, 0.2);
}

.filters-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.filter-select, .filter-input {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.filter-select:focus, .filter-input:focus {
  outline: none;
  border-color: #ff6b35;
}

/* Selected Section */
.selected-section {
  background: rgba(255, 255, 255, 0.95);
  padding: 1.5rem;
  border-radius: 15px;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.selected-section h3 {
  color: #333;
  margin-bottom: 1rem;
}

.selected-ingredients {
  min-height: 60px;
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.selected-ingredient {
  background: #ff6b35;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.remove-btn {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.selected-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b35, #f7931e);
  color: white;
  box-shadow: 0 3px 10px rgba(255, 107, 53, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.4);
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

/* Ingredients Container */
.ingredients-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 2rem 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ff6b35;
}

.category-header h3 {
  color: #ff6b35;
  font-size: 1.3rem;
}

.category-count {
  color: #666;
  font-size: 0.9rem;
}

.ingredients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.ingredient-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ingredient-card:hover {
  border-color: #ff6b35;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 107, 53, 0.2);
}

.ingredient-card.selected {
  background: #ff6b35;
  color: white;
  border-color: #ff6b35;
}

.ingredient-name {
  font-weight: 500;
}

.ingredient-action {
  font-weight: bold;
  font-size: 1.2rem;
}

/* Recipes Container */
.recipes-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.recipe-card {
  background: white;
  border-radius: 15px;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-left: 5px solid #ff6b35;
}

.recipe-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.recipe-header h3 {
  color: #ff6b35;
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.recipe-meta {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.recipe-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.recipe-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.dietary-label {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
}

.recipe-section {
  margin-bottom: 1.5rem;
}

.recipe-section h4 {
  color: #333;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.ingredients-list, .instructions-list {
  padding-left: 1.5rem;
  line-height: 1.8;
}

.ingredients-list li {
  color: #555;
  margin-bottom: 0.25rem;
}

.instructions-list li {
  color: #555;
  margin-bottom: 0.5rem;
}

.recipe-source {
  display: inline-block;
  background: #ff6b35;
  color: white;
  padding: 0.5rem 1rem;
  text-decoration: none;
  border-radius: 20px;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.recipe-source:hover {
  background: #e55a2b;
  transform: translateY(-2px);
}

/* About Section */
.about-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 2rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 3rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #ff6b35;
}

.feature-card h3 {
  color: #ff6b35;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

.creator-section {
  text-align: center;
  padding: 2rem;
  background: linear-gradient(135deg, #ff6b35, #f7931e);
  border-radius: 15px;
  color: white;
}

.creator-section h3 {
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

/* Empty States */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty-state h3 {
  margin-bottom: 1rem;
  color: #333;
}

.error-state {
  text-align: center;
  padding: 3rem;
  background: #ffebee;
  border-radius: 10px;
  border-left: 4px solid #f44336;
}

.error-state h3 {
  color: #f44336;
  margin-bottom: 1rem;
}

.loading {
  text-align: center;
  padding: 3rem;
  font-size: 1.2rem;
  color: #ff6b35;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .view {
    padding: 1rem;
  }
  
  .hero-content h2 {
    font-size: 2rem;
  }
  
  .hero-stats {
    grid-template-columns: 1fr;
  }
  
  .section-header h2 {
    font-size: 2rem;
  }
  
  .ingredients-grid {
    grid-template-columns: 1fr;
  }
  
  .recipe-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .selected-actions {
    flex-direction: column;
  }
}''')

# Save the zip file to disk
with open('smarty-chef-pcs-final.zip', 'wb') as f:
    f.write(zip_buffer.getvalue())

print("✅ Final Smarty-Chef.PCS zip package created successfully!")
print("📁 File: smarty-chef-pcs-final.zip")
print("📦 Contains: package.json, server.js, app.js, index.html, style.css, manifest.json, service-worker.js, README.md")
print("🚀 Ready for deployment on Render or any Node.js hosting platform!")