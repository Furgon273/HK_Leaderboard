import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ProfileView from '@/views/ProfileView.vue'
import DiscussionView from '@/views/DiscussionView.vue'
import LeaderboardView from '@/views/LeaderboardView.vue'
import RunSubmissionView from '@/views/RunSubmissionView.vue'
import ProfileEditView from '@/views/ProfileEditView.vue'
import AdminPanel from '@/views/AdminPanel.vue'
import AddChallengeView from '@/views/AddChallengeView.vue'
import ChallengeDetailView from '@/views/ChallengeDetailView.vue' // Import ChallengeDetailView
import AddAchievementView from '@/views/AddAchievementView.vue'
import AchievementDetailsView from '@/views/AchievementDetailsView.vue' // Import AchievementDetailsView
import EditAchievementView from '@/views/EditAchievementView.vue' // Import EditAchievementView
import LinkConfirmationView from '@/views/LinkConfirmationView.vue' // Import LinkConfirmationView
import { useAuthStore } from '@/store/auth'; // Import useAuthStore

const routes = [
  { path: '/', name: 'home', component: LeaderboardView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/profile/:username', name: 'profile', component: ProfileView },
  { path: '/discussion/:id', name: 'discussion', component: DiscussionView },
  { path: '/leaderboard', name: 'leaderboard', component: LeaderboardView },
  { 
    path: '/submit-run', 
    name: 'submit-run', 
    component: RunSubmissionView, 
    meta: { requiresAuth: true } 
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdit',
    component: ProfileEditView,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { requiresAdmin: true }
  },
  {
    path: '/add-achievement',
    name: 'add-achievement',
    component: AddAchievementView,
  },
  {
    path: '/admin/add-challenge',
    name: 'AddChallenge',
    component: AddChallengeView,
    meta: { requiresAdmin: true }
  },
  {
    path: '/challenge/:id',
    name: 'ChallengeDetail',
    component: ChallengeDetailView,
  },
  {
    path: '/edit-achievement/:id',
    name: 'EditAchievement',
    component: EditAchievementView,
  },
  {
    path: '/achievements/:id',
    name: 'AchievementDetails',
    component: AchievementDetailsView,
  },
  {
    path: '/confirm-link',
    name: 'ConfirmLink',
    component: LinkConfirmationView,
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export const setupRouter = (app) => {
  // Теперь мы можем использовать Pinia здесь

  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore(); // Get the authStore instance inside the guard

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      next('/login')
    } else if (to.meta.requiresAdmin && (!authStore.user || (!authStore.user.is_admin && !authStore.user.is_super_admin))) {
      // If route requires admin and user is not logged in or not admin
      next('/') // Redirect to home or a forbidden page
    } else {
      next()
    }
  })
  return router
}

export default router