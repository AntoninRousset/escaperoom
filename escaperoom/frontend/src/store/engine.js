import {EngineApi, createConfiguration} from 'escaperoom-client'

const engineClient = new EngineApi(createConfiguration());

export default {
  namespaced: true,
  state: {
    _states: null,
    _masks: {},
    pulling: false,
  },
  getters: {
    states(storeState) {
      if (storeState._states === null) {
        return null;
      }
      let states = new Array();
      for (const [_id, mask] of Object.entries(storeState._masks)) {
        const state = storeState._states[_id] || {};
        states.push({...state, ...mask});
      }
      return states;
    },
  },
  mutations: {
    setPulling(storeState, pulling) {
      storeState.pulling = pulling;
    },
    setStates(storeState, states) {
      storeState._states = Object.fromEntries(
        states.map(state => [state.id, state])
      );
      for (const id in storeState._states) {
        storeState._masks[id] = storeState._masks[id] || {};
      }
    },
  },
  actions: {
    add({ commit }) {
      console.log('add');
    },
    remove({ commit }, id) {
      console.log('remove', id);
    },
    pull({ commit }) {
      commit('setPulling', true);
      engineClient.statesList()
        .then(states => {
          commit('setStates', states);
        })
        .catch(error => {
          console.error('Could not download states', error);
        })
        .finally(() => {
          commit('setPulling', false);
        });
    }
  }
};
