// 500 Global Ingredients with categorized search UI
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
  return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
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
}