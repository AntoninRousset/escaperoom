export default {
  namespaced: true,
  state: {
    autoPull: true,
    autoPush: true,
  },
  mutations: {
    setAutoPull(state, autoPull) {
      state.autoPull = autoPull;
    },
    setAutoPush(state, autoPush) {
      state.autoPush = autoPush;
    },
  },
}
