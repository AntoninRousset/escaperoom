import { EngineApi, Configuration } from 'escaperoom-client'
import { MissingIdError } from './exceptions.js'

const engineApi = new EngineApi(new Configuration({ basePath: '' }));
let _negativeCounter = 0;

// TODO track and fix non-string id
// TODO removed residual masks after a pull
// TODO keep ordered the list of states returned by getter

export default {
  namespaced: true,
  state: {
    _states: {},
    _masks: {},
  },
  getters: {
    states(storeState) {
      let states = {};
      const masks = { ...storeState._states, ...storeState._masks };
      for (const [id, mask] of Object.entries(masks)) {
        if (mask && (mask.id <= 0 || mask.id in storeState._states)) {
          if (id <= 0 || ! (mask.id in states)) {
            const state = storeState._states[mask.id] || {};
            states[mask.id] = { ...state, ...mask, id };
          }
        }
      }
      Object.keys(states).forEach(function deleteOrphans(id) {
        id = storeState._masks[id] ? storeState._masks[id].id : id;
        const state = states[id];
        if (! state || (state.parent && deleteOrphans(state.parent))) {
          delete states[id];
          return true;
        }
        return false;
      });
      Object.values(states).forEach(function solveParent(state) {
        if (state.parent) {
          state.parent = states[masks[state.parent].id];
        } else {
          state.parent = null;
        }
      });
      return Object.values(states);
    },
  },
  mutations: {
    _clean(storeState) {
      storeState._states = {};
      storeState._masks = {};
      _negativeCounter = 0;
    },
    setMask(storeState, { id, mask }) {
      storeState._masks[id] = mask;
    },
    setStates(storeState, states) {
      storeState._states = states;
    },
    // Update state and change mask correspondingly.
    updateState(storeState, { id, state }) {
      const mask = storeState._masks[id];
      mask.id = state.id;
      for (const key of Object.keys(mask)) {
        if (key !== 'id' && mask[key] == state[key]) {
          delete mask[key];
        }
      }
      if (id != state.id) {
        storeState._masks[state.id] = mask;
        Object.defineProperty(storeState._masks, id.toString(), {
          get: new Function('return this[id];'.replace('id', state.id)),
          set: new Function('mask', 'this[id]=mask;'.replace('id', state.id)),
        });
      }
      storeState._states[state.id] = state;
    },
    // Delete state and mask
    deleteState(storeState, id) {
      const mask = storeState._masks[id];
      if (mask) {
        delete storeState._states[mask.id];
        delete storeState._masks[mask.id];
      }
      delete storeState._states[id];
      delete storeState._masks[id];
    },
  },
  actions: {
    addState({ commit }, state) {
      const id = (_negativeCounter--).toString();
      commit('setMask', { id, mask: { ...state, id, room: 1, x: 0, y: 0 } });
      console.debug('state added');
      return id;
    },
    removeState({ commit }, state) {
      if (! state.id) {
        throw new MissingIdError('State to remove does not have an id.')
      }
      commit('setMask', { id: state.id, mask: null });
      console.debug('state', state.id, 'removed');
    },
    changeState({ commit, state }, mask) {
      if (! mask.id) {
        throw new MissingIdError('State to change does not have an id.')
      }
      const oldMask = state._masks[mask.id] || {};
      const id = oldMask.id || mask.id;
      let parent = null;
      if (mask.parent) {
        if ('id' in mask.parent) {
          parent = mask.parent.id;
        } else {
          throw new Error('Parent has no id');
        }
      }
      commit('setMask', { id, mask: { ...oldMask, ...mask, parent, id } });
      console.debug('state', id, 'changed');
    },
    pull({ commit }) {
      return engineApi.statesList().then((states) => {
        states = Object.fromEntries(
          states.map(state => [state.id, state])
        );
        commit('setStates', states);
        console.log('Engine pulled')
      }).catch((error) => {
        console.error('Could not download states', error);
      });
    },
    push({ commit, state }) {
      let operations = {};
      Object.values(state._masks).forEach(function createOrUpdate(mask) {
        if (! mask) {  // will be destroyed later
          return new Promise((resolve) => { resolve({ id: null }); });
        }
        if (mask.id in operations) {
          return operations[mask.id];
        } else if (mask.id <= 0) {  // create
          operations[mask.id] = createOrUpdate(state._masks[mask.parent])
          .then((parent) => {
            const state = { ...mask, id: undefined, parent: parent.id };
            return engineApi.statesCreate({ state }).catch((error) => {
              throw new Error('Could not create state:', error.code);
            }).then((state) => {
              commit('updateState', { id: mask.id, state });
              console.debug('state', mask.id, 'created');
              return state;
            });
          });
        } else if (Object.keys(mask).length > 1) {  // update
          operations[mask.id] = createOrUpdate(state._masks[mask.parent])
          .then((parent) => {
            const patchedState = { ...mask, id: undefined, parent: parent.id };
            return engineApi.statesPartialUpdate({ id: mask.id, patchedState })
            .catch((error) => {
              if (error.code == 404) {
                console.warning(
                  'State', mask.id, 'was removed before it could be updated'
                );
              } else {
                throw new Error(
                  'Could not update state', mask.id, ':', error.code
                );
              }
            }).then((state) => {
              commit('updateState', { id: mask.id, state });
              console.debug('state', mask.id, 'updated');
              return state;
            });
          });
        }
        return operations[mask.id];
      });

      const createdAndUpdated = Promise.all(Object.values(operations));
      Object.entries(state._masks).forEach(function destroy([id, mask]) {
        if (! mask && id > 0) {
          createdAndUpdated.then(() => {
            operations[id] = engineApi.statesDestroy({ id }).catch((error) => {
              if (error.code == 404) {
                console.debug('State', id, 'was aleady destroyed');
              } else {
                throw new Error(
                  'Could not destroy state', id, ':', error.message
                );
              }
            }).then(() => {
              commit('deleteState', id);
              console.debug('state', id, 'destroyed');
            });
          });
        }
      });

      return Promise.all(Object.values(operations)).then(() => {
        console.log('Engine pushed')
      });
    }
  }
};
