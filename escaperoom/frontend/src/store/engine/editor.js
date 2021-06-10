export default {
  namespaced: true,
  state: {
    drag: {},
    step: 25,
  },
  mutations: {
    setDrag(storeState, drag) {
      storeState.drag = drag;
    },
    setStep(storeState, step) {
      storeState.step = step;
    },
  },
}
