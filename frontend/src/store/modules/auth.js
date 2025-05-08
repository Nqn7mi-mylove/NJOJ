import api from '@/services/api'
import router from '@/router'

// Initial state
const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null
}

// Getters
const getters = {
  isLoggedIn: state => !!state.token,
  currentUser: state => state.user,
  isAdmin: state => state.user && state.user.role === 'admin'
}

// Actions
const actions = {
  async login({ commit }, credentials) {
    commit('SET_LOADING', true, { root: true })
    try {
      // Create FormData
      const formData = new FormData()
      formData.append('username', credentials.username)
      formData.append('password', credentials.password)
      
      // Create request config with correct content type handling
      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
      
      // Send request
      const response = await api.post('/auth/login', formData, config)
      const token = response.data.access_token
      
      // Get user information
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      const userResponse = await api.get('/users/me')
      
      // Save to localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userResponse.data))
      
      // Update state
      commit('SET_TOKEN', token)
      commit('SET_USER', userResponse.data)
      commit('SET_LOADING', false, { root: true })
      return true
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Login failed', { root: true })
      return false
    }
  },
  
  async signup({ commit }, userData) {
    commit('SET_LOADING', true, { root: true })
    try {
      console.log('Sending signup request with data:', userData)
      console.log('API URL:', api.defaults.baseURL)
      
      const response = await api.post('/auth/signup', userData)
      console.log('Signup successful, response:', response.data)
      
      const token = response.data.access_token
      
      // Get user information
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      const userResponse = await api.get('/users/me')
      
      // Save to localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(userResponse.data))
      
      // Update state
      commit('SET_TOKEN', token)
      commit('SET_USER', userResponse.data)
      commit('SET_LOADING', false, { root: true })
      return true
    } catch (error) {
      console.error('Signup failed:', error)
      
      if (error.response) {
        console.error('Error response data:', error.response.data)
        console.error('Error response status:', error.response.status)
        console.error('Error response headers:', error.response.headers)
      } else if (error.request) {
        console.error('No response received:', error.request)
      } else {
        console.error('Error message:', error.message)
      }
      
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Signup failed', { root: true })
      return false
    }
  },
  
  async logout({ commit }) {
    // Remove from localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Update state
    commit('SET_TOKEN', null)
    commit('SET_USER', null)
    
    // Remove Authorization header
    delete api.defaults.headers.common['Authorization']
    
    // Redirect to login page
    if (router.currentRoute.value.meta.requiresAuth) {
      router.push('/login')
    }
  },
  
  async updateProfile({ commit, state }, userData) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.put('/users/me', userData)
      
      // Update localStorage
      localStorage.setItem('user', JSON.stringify(response.data))
      
      // Update state
      commit('SET_USER', response.data)
      commit('SET_LOADING', false, { root: true })
      return true
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to update profile', { root: true })
      return false
    }
  },
  
  // Initialize auth from localStorage
  initAuth({ commit }) {
    const token = localStorage.getItem('token')
    const user = JSON.parse(localStorage.getItem('user'))
    
    if (token && user) {
      // Set Authorization header
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      
      // Update state
      commit('SET_TOKEN', token)
      commit('SET_USER', user)
    }
  }
}

// Mutations
const mutations = {
  SET_TOKEN(state, token) {
    state.token = token
  },
  SET_USER(state, user) {
    state.user = user
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
