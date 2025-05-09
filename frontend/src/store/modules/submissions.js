import api from '@/services/api'

// Initial state
const state = {
  submissions: [],
  currentSubmission: null,
  totalSubmissions: 0
}

// Getters
const getters = {
  allSubmissions: state => state.submissions,
  currentSubmission: state => state.currentSubmission,
  totalSubmissions: state => state.totalSubmissions
}

// Actions
const actions = {
  async fetchSubmissions({ commit }, { skip = 0, limit = 20, problemId = null, status = null }) {
    commit('SET_LOADING', true, { root: true })
    try {
      let url = `/submissions?skip=${skip}&limit=${limit}`
      
      if (problemId) {
        url += `&problem_id=${problemId}`
      }
      
      if (status) {
        url += `&status=${status}`
      }
      
      const response = await api.get(url)
      
      // 确保接收到的提交记录数组不为空
      if (response.data && response.data.length > 0) {
        commit('SET_SUBMISSIONS', response.data)
      } else {
        // 尝试再次获取所有提交记录，不用相同的筛选条件
        if (problemId) {
          const retryResponse = await api.get(`/submissions?skip=${skip}&limit=${limit}`)
          commit('SET_SUBMISSIONS', retryResponse.data)
        }
      }
      
      commit('SET_LOADING', false, { root: true })
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch submissions', { root: true })
    }
  },
  
  async fetchSubmission({ commit }, id) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.get(`/submissions/${id}`)
      commit('SET_CURRENT_SUBMISSION', response.data)
      commit('SET_LOADING', false, { root: true })
      return response.data
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to fetch submission', { root: true })
      return null
    }
  },
  
  async submitCode({ commit }, { problemId, code, language }) {
    commit('SET_LOADING', true, { root: true })
    try {
      const response = await api.post('/submissions', {
        problem_id: problemId,
        code,
        language
      })
      commit('SET_LOADING', false, { root: true })
      return response.data
    } catch (error) {
      commit('SET_LOADING', false, { root: true })
      commit('SET_ERROR', error.response?.data?.detail || 'Failed to submit code', { root: true })
      return null
    }
  },
  
  async pollSubmissionStatus({ commit, dispatch }, id) {
    const pollInterval = 2000 // 2 seconds
    let attempts = 0
    const maxAttempts = 30 // 1 minute max
    
    const poll = async () => {
      try {
        const response = await api.get(`/submissions/${id}`)
        const submission = response.data
        
        commit('SET_CURRENT_SUBMISSION', submission)
        
        // If still judging, continue polling
        if (submission.status === 'pending' || submission.status === 'judging') {
          if (attempts < maxAttempts) {
            attempts++
            setTimeout(poll, pollInterval)
          } else {
            commit('SET_ERROR', 'Judging is taking longer than expected', { root: true })
          }
        }
        
        return submission
      } catch (error) {
        commit('SET_ERROR', error.response?.data?.detail || 'Failed to get submission status', { root: true })
        return null
      }
    }
    
    return poll()
  }
}

// Mutations
const mutations = {
  SET_SUBMISSIONS(state, submissions) {
    state.submissions = submissions
    state.totalSubmissions = submissions.length
  },
  SET_CURRENT_SUBMISSION(state, submission) {
    state.currentSubmission = submission
  },
  CLEAR_CURRENT_SUBMISSION(state) {
    state.currentSubmission = null
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
