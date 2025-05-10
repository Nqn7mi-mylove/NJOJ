import api from '@/services/api'

// Initial state
const state = {
  problems: [],
  currentProblem: null,
  totalProblems: 0
}

// Getters
const getters = {
  allProblems: state => state.problems,
  currentProblem: state => state.currentProblem,
  totalProblems: state => state.totalProblems
}

// Actions
const actions = {
  async fetchProblems({ commit }, { skip = 0, limit = 20, difficulty = null, tags = [] }) {
    commit('SET_LOADING', true, { root: true })
    try {
      let url = `/problems?skip=${skip}&limit=${limit}`
      
      if (difficulty) {
        url += `&difficulty=${difficulty}`
      }
      
      if (tags && tags.length > 0) {
        tags.forEach(tag => {
          url += `&tags=${tag}`
        })
      }
      
      const response = await api.get(url)
      commit('SET_PROBLEMS', response.data)
      commit('SET_LOADING', false, { root: true })
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch problems', { root: true })
    }
  },
  
  async fetchProblem({ commit }, id) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.get(`/problems/${id}`)
      
      // 确保test_cases是数组
      if (!response.data.test_cases) {
        response.data.test_cases = [];
      }
      
      commit('SET_CURRENT_PROBLEM', response.data)
      commit('SET_LOADING', false, { root: true })
      return response.data
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || '获取问题详情失败', { root: true })
      return null
    }
  },
  
  async createProblem({ commit }, problemData) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.post('/problems', problemData)
      commit('SET_LOADING', false, { root: true })
      return response.data
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to create problem', { root: true })
      return null
    }
  },
  
  async updateProblem({ commit }, { id, problemData }) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.put(`/problems/${id}`, problemData)
      commit('SET_LOADING', false, { root: true })
      return response.data
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to update problem', { root: true })
      return null
    }
  },
  
  async deleteProblem({ commit, dispatch }, id) {
    commit('SET_LOADING', true, { root: true })
    try {
      await api.delete(`/problems/${id}`)
      // Refresh problems list
      dispatch('fetchProblems', { skip: 0, limit: 20 })
      commit('SET_LOADING', false, { root: true })
      return true
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to delete problem', { root: true })
      return false
    }
  }
}

// Mutations
const mutations = {
  SET_PROBLEMS(state, problems) {
    state.problems = problems
    state.totalProblems = problems.length
  },
  SET_CURRENT_PROBLEM(state, problem) {
    state.currentProblem = problem
  },
  CLEAR_CURRENT_PROBLEM(state) {
    state.currentProblem = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
