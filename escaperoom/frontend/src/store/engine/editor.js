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

function defaultObject(object, key, type = Object) {
  if (key in object) {
    return object[key];
  } else {
    object[key] = type();
    return object[key];
  }
}

export default {
  namespaced: true,
  state: {
    drag: null,
    step: 20,
  },
  getters: {
    perStateTransitions(storeState, getters, rootState, rootGetters) {
      const transitions = rootGetters['engine/transitions'];
      const perStateTransitions = {};
      transitions.forEach((transition) => {
        if (transition.src && transition.src.parent) { 
          const stateId = transition.src.parent.id;
          defaultObject(perStateTransitions, stateId)[transition.id] =
            transition;
        } else {
          const stateId = null;
          defaultObject(perStateTransitions, stateId)[transition.id] =
            transition;
        }
        if (transition.dest && transition.dest.parent) { 
          const stateId = transition.dest.parent.id;
          defaultObject(perStateTransitions, stateId)[transition.id] =
            transition;
        } else {
          const stateId = null;
          defaultObject(perStateTransitions, stateId)[transition.id] =
            transition;
        }
      });
      for (const [stateId, transitions] of
           Object.entries(perStateTransitions)) { 
        perStateTransitions[stateId] = Object.values(transitions);
      }
      return perStateTransitions;
    },
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
