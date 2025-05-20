<template>
  <v-container style="max-width: 800px;">
    <v-card v-if="discussion">
      <v-card-title>{{ discussion.title }}</v-card-title>
      <v-card-subtitle>
        Автор: {{ discussion.author.username }} | 
        {{ new Date(discussion.created_at).toLocaleString() }}
      </v-card-subtitle>
      
      <v-card-text>
        <div class="mb-4">{{ discussion.content }}</div>
        
        <v-divider class="my-4"></v-divider>
        
        <v-list>
          <v-list-item 
            v-for="comment in comments" 
            :key="comment.id"
            class="comment-item"
            :class="{ 'ml-8': comment.parent_id }"
          >
            <template #prepend>
              <v-avatar size="40">
                <v-img :src="`https://i.pravatar.cc/150?u=${comment.author.username}`" />
              </v-avatar>
            </template>
            
            <v-list-item-title>{{ comment.author.username }}</v-list-item-title>
            <v-list-item-subtitle>
              {{ new Date(comment.created_at).toLocaleString() }}
            </v-list-item-subtitle>
            <v-list-item-content class="mt-2">
              {{ comment.content }}
            </v-list-item-content>
            
            <template #append>
              <v-btn 
                v-if="isAuthenticated"
                icon
                size="small"
                @click="replyTo = comment.id"
              >
                <v-icon>mdi-reply</v-icon>
              </v-btn>
            </template>
          </v-list-item>
        </v-list>
        
        <v-form v-if="isAuthenticated" @submit.prevent="addComment">
          <v-textarea
            v-model="newComment"
            label="Ваш комментарий"
            rows="3"
            required
          ></v-textarea>
          
          <input type="hidden" v-model="replyTo">
          
          <v-btn 
            type="submit" 
            color="primary"
            :loading="loading"
          >
            Отправить
          </v-btn>
        </v-form>
        <v-alert v-else type="info">
          Чтобы оставить комментарий, <router-link to="/login">войдите</router-link> в систему.
        </v-alert>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '@/composables/useApi'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const { fetchApi, loading } = useApi()
const authStore = useAuthStore()

const discussion = ref(null)
const comments = ref([])
const newComment = ref('')
const replyTo = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(async () => {
  const discussionId = route.params.id
  discussion.value = await fetchApi(`/discussion/${discussionId}`)
  comments.value = await fetchApi(`/discussion/${discussionId}/comments`)
})

const addComment = async () => {
  try {
    const comment = await fetchApi(`/discussion/${discussion.value.id}/comments`, {
      method: 'POST',
      body: JSON.stringify({
        content: newComment.value,
        parent_id: replyTo.value
      }),
    })
    
    comments.value.push(comment)
    newComment.value = ''
    replyTo.value = null
  } catch (err) {
    console.error('Error adding comment:', err)
  }
}
</script>

<style scoped>
.comment-item {
  border-left: 3px solid #eee;
  /* Adjust border color for dark theme */
  border-left: 3px solid #444;
  margin-bottom: 8px;
  transition: all 0.3s;
}

.comment-item:hover {
  /* Adjust hover border color */
  border-left-color: var(--hover-color);
}

.v-container {
  /* Add padding and center content */
  padding: 20px;
  margin: 0 auto;
}

.v-card {
  /* Apply dark card background */
  background-color: var(--color-background);
  color: var(--text-color);
  border-radius: 8px;
  border: 1px solid #333;
}

.v-card-title {
  color: var(--accent-color);
  font-size: 24px;
  font-weight: 500;
  padding-bottom: 10px;
  border-bottom: 1px solid #333;
}

.v-card-subtitle {
  color: #b0b0b0; /* Slightly lighter grey */
}

.v-list-item {
  background-color: var(--color-background);
}

.v-textarea {
  background-color: var(--color-background);
}
</style>