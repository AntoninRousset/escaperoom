function deepCopyStates(states) {
  const copiedStates = {};
  states.forEach(function copy(state) {
    if (state === null) {
      return null;
    }
    if (! (state.id in copiedStates)) {
      copiedStates[state.id] = {
        ...state, parent: copy(state.parent), children: []
      };
    }
    return copiedStates[state.id]
  });
  return Object.values(copiedStates);
}

export default {
  namespaced: true,
  state: {
    drag: null,
    step: 25,
  },
  getters: {
    rootStates(storeState, getters, rootState, rootGetters) {
      const states = deepCopyStates(rootGetters['engine/states']);
      const rootStates = [];
      states.forEach((state) => {
        if (state.parent) {
          state.parent.children = state.parent.children || [];
          state.parent.children.push(state);
        } else {
          rootStates.push(state);
        }
        if (storeState.drag && state.id == storeState.drag.state.id) {
          state.x += storeState.drag.delta.x;
          state.y += storeState.drag.delta.y;
        }
      });
      return rootStates;
    },
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
