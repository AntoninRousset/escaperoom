import { EngineApi, Configuration } from 'escaperoom-client'
import { MissingPropertyError } from '../exceptions.js'
import editor from './editor.js'

const engineApi = new EngineApi(new Configuration({ basePath: '' }));
let _negativeCounter = 0;

// TODO track and fix non-string id
// TODO removed residual masks after a pull
// TODO keep ordered the list of states returned by getter

export default {
  namespaced: true,
  state: {
    _states: {},
    _statesMasks: {},
    _transitions: {},
    _transitionsMasks: {},
  },
  getters: {
    states(storeState) {
      let states = {};
      const masks = { ...storeState._states, ...storeState._statesMasks };
      for (const [id, mask] of Object.entries(masks)) {
        if (mask && (mask.id <= 0 || mask.id in storeState._states)) {
          if (id <= 0 || ! (mask.id in states)) {
            let state = storeState._states[mask.id] || {};
            states[mask.id] = { ...state, ...mask, id };
          }
        }
      }
      Object.keys(states).forEach(function deleteOrphans(id) {
        id = storeState._statesMasks[id] ? storeState._statesMasks[id].id : id;
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
      storeState._statesMasks = {};
      _negativeCounter = 0;
    },
    setStates(storeState, states) {
      storeState._states = states;
    },
    addState(storeState, state) {
      const id = (_negativeCounter--).toString();
      const parent = state.parent || null;
      if (state.x === null || state.x === undefined) {
        throw new MissingPropertyError('New state does not have x position');
      } else if (state.y === null || state.y === undefined) {
        throw new MissingPropertyError('New state does not have y position');
      } else if (state.room === null || state.room === undefined) {
        throw new MissingPropertyError('New state does not have room');
      }
      storeState._statesMasks[id] = { ...state, id, parent };
      return id;
    },
    changeState(storeState, changes) {
      if (! changes.id) {
        throw new MissingPropertyError('State to change does not have an id.')
      }
      const mask = storeState._statesMasks[changes.id] || {};
      Object.assign(mask, changes);
      if ('parent' in changes) {
        if (typeof changes.parent === 'object') {
          if ('id' in changes.parent) {
            mask.parent = changes.parent.id;
          } else {
            throw new MissingPropertyError('Given parent does not have an id');
          }
        } else {
          mask.parent = changes.parent;
        }
      }
      if (parent == changes.id) {
        throw new Error('Circular reference')
      }
      storeState._statesMasks[mask.id] = mask;
      console.debug('state', mask.id, 'changed');
    },
    removeState(storeState, state) {
      if (! state.id) {
        throw new MissingPropertyError('State to remove does not have an id.')
      }
      storeState._statesMasks[state.id] = null;
      console.debug('state', state.id, 'removed');
    },
    // Update state and change mask correspondingly.
    updateState(storeState, { id, state }) {
      const mask = storeState._statesMasks[id];
      mask.id = state.id;
      for (const key of Object.keys(mask)) {
        if (key !== 'id' && mask[key] == state[key]) {
          delete mask[key];
        }
      }
      if (id != state.id) {
        storeState._statesMasks[state.id] = mask;
        Object.defineProperty(storeState._statesMasks, id.toString(), {
          get: new Function('return this[id];'.replace('id', state.id)),
          set: new Function('mask', 'this[id]=mask;'.replace('id', state.id)),
        });
      }
      storeState._states[state.id] = state;
    },
    // Delete state and mask
    deleteState(storeState, id) {
      const mask = storeState._statesMasks[id];
      if (mask) {
        delete storeState._states[mask.id];
        delete storeState._statesMasks[mask.id];
      }
      delete storeState._states[id];
      delete storeState._statesMasks[id];
    },
  },
  actions: {
    pull({ commit }) {
      return engineApi.statesList().then((states) => {
        states = Object.fromEntries(
          states.map(state => [state.id, state])
        );
        commit('setStates', states);
        console.debug('Engine pulled')
      }).catch((error) => {
        console.error('Could not download states', error);
      });
    },
    push({ commit, state }) {
      let operations = {};
      Object.values(state._statesMasks).forEach(function createOrUpdate(mask) {
        if (! mask) {  // will be destroyed later
          return new Promise((resolve) => { resolve(null); });
        }
        if (mask.id in operations) {
          return operations[mask.id];
        } else if (mask.id <= 0) {  // create
          operations[mask.id] = createOrUpdate(state._statesMasks[mask.parent])
          .then((parent) => {
            const state = { ...mask, id: undefined };
            if (parent) {
              state.parent = Number(parent.id);
            }
            return engineApi.statesCreate({ state }).catch((error) => {
              throw new Error('Could not create state:', error.code);
            }).then((state) => {
              commit('updateState', { id: mask.id, state });
              console.debug('state', mask.id, 'created');
              return state;
            });
          });
        } else if (Object.keys(mask).length > 1) {  // update
          operations[mask.id] = createOrUpdate(state._statesMasks[mask.parent])
          .then((parent) => {
            const patchedState = { ...mask, id: undefined };
            if (parent) {
              patchedState.parent = Number(parent.id);
            }
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
      Object.entries(state._statesMasks).forEach(function destroy([id, mask]) {
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
        console.debug('Engine pushed')
      });
    }
  },
  modules: { editor },
};
