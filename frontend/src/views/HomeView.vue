<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '@/composables/useApi'
import { useRouter } from 'vue-router'

const { fetchApi, error, loading } = useApi()
const seasons = ref([])
const router = useRouter()

onMounted(async () => {
  try {
    loading.value = true
    const seasonUuids = await fetchApi('/seasons')
    
    if (seasonUuids && seasonUuids.length > 0) {
      const seasonData = await Promise.all(seasonUuids.map(uuid => fetchApi(`/season_info/${uuid}`)))
      const cardsData = await Promise.all(seasonUuids.map(uuid => fetchApi(`/cards/${uuid}`)))

      seasons.value = seasonData.map((season, index) => ({
        ...season,
        cards: cardsData[index] || []
      }))
    } else {
        seasons.value = [] // No seasons found
    }
  } catch (err) {
    console.error('Ошибка загрузки данных:', err)
    error.value = 'Error loading data. Please try again later.'
  } finally {
    loading.value = false
  }
})

const navigateToCard = (cardUuid) => {
  router.push(`/card/${cardUuid}`)
}
</script>

<template>
  <div>
    <div v-if="loading" class="loading">Loading cards...</div>
    <div v-else-if="error" class="loading" style="color: #ff5555;">{{ error }}</div>
    <div v-else-if="seasons.length === 0" class="loading">No seasons found</div>

    <div v-else id="seasons-container">
      <div v-for="season in seasons" :key="season.uuid" class="season">
        <h2 class="season-title">{{ season.name }}</h2>
        <div class="cards-container">
          <div v-if="season.cards.length === 0" style="grid-column: 1/-1; text-align: center; color: #666;">No cards in this season</div>
          <div v-else v-for="card in season.cards" :key="card.uuid" class="card" @click="navigateToCard(card.uuid)">
            <img v-if="card.img" :src="`/card_imgs/${card.img}`" :alt="card.name" class="card-image">
            <div v-else class="image-placeholder">No image</div>
            <div class="card-name">{{ card.name }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:root {
    --bg-color: #121212;
    --card-bg: #1e1e1e;
    --text-color: #e0e0e0;
    --accent-color: #ffffff;
    --hover-color: #bb86fc;
}

body { /* Note: Body styles might be better in a global CSS file */
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: var(--bg-color);
    color: var(--text-color);
}

.season {
    background-color: var(--card-bg);
    border-radius: 8px;
    padding: 25px;
    margin-bottom: 40px;
    border: 1px solid #333;
}

.season-title {
    font-size: 24px;
    margin-bottom: 20px;
    color: var(--accent-color);
    font-weight: 500;
    padding-bottom: 10px;
    border-bottom: 1px solid #333;
}

.cards-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
}

.card {
    cursor: pointer;
    transition: transform 0.3s ease;
    text-align: center;
    background-color: #252525;
    border-radius: 8px;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-5px);
}

.card-image {
    width: 100%;
    height: 280px;
    object-fit: cover;
}

.image-placeholder {
    width: 100%;
    height: 280px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #333;
    color: #666;
}

.loading {
    text-align: center;
    font-size: 16px;
    margin: 50px 0;
    color: var(--accent-color);
}

@media (max-width: 768px) {
    .cards-container {
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    }

    .card-image, .image-placeholder {
        height: 220px;
    }
}
</style>