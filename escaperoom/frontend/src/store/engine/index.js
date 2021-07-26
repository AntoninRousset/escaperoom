import { EngineApi, Configuration } from 'escaperoom-client'
import { MissingPropertyError } from '../exceptions.js'
import editor from './editor.js'

const engineApi = new EngineApi(new Configuration({ basePath: '' }));
let _statesCounter = 0;
let _transitionsCounter = 0;

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
        if (mask && (mask.id <= 0 || mask.id in storeState._states) &&
           (id <= 0 || ! (mask.id in states))) {
          let state = storeState._states[mask.id] || {};
          states[mask.id] = { ...state, ...mask, id };
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
    transitions(storeState, getters) {
      let transitions = {};
      const masks = {
        ...storeState._transitions, ...storeState._transitionsMasks
      };
      for (const [id, mask] of Object.entries(masks)) {
        if (mask && (mask.id <= 0 || mask.id in storeState._transitions) &&
           (id <= 0 || ! (mask.id in transitions))) {
          let transition = storeState._transitions[mask.id] || {};
          transitions[mask.id] = { ...transition, ...mask, id };
        }
      }
      const statesMap = Object.fromEntries(
        getters.states.map((state) => [state.id, state])
      );
      Object.keys(transitions).forEach(function deleteOrphans(id) {
        id = storeState._transitionsMasks[id] ?
          storeState._transitionsMasks[id].id : id;
        const transition = transitions[id];
        if (! (transition.src in statesMap && transition.dest in statesMap)) {
          delete transitions[id];
        }
      });
      Object.values(transitions).forEach(function solveSiblings(transition) {
          transition.src = statesMap[transition.src];
          transition.dest = statesMap[transition.dest];
      });
      return Object.values(transitions);
    },
  },
  mutations: {
    _clean(storeState) {
      storeState._states = {};
      storeState._statesMasks = {};
      storeState._transitions = {};
      storeState._transitionsMasks = {};
      _statesCounter = 0;
      _transitionsCounter = 0;
    },
    setStates(storeState, states) {
      storeState._states = states;
    },
    setTransitions(storeState, transitions) {
      storeState._transitions = transitions;
    },
    addState(storeState, state) {
      const id = (_statesCounter--).toString();
      let parent = state.parent || null;
      if (state.parent && typeof state.parent == 'object') {
        parent = state.parent.id;
      }
      if (state.x === null || state.x === undefined) {
        throw new MissingPropertyError('New state does not have x position');
      } else if (state.y === null || state.y === undefined) {
        throw new MissingPropertyError('New state does not have y position');
      } else if (state.room === null || state.room === undefined) {
        throw new MissingPropertyError('New state does not have a room');
      }
      storeState._statesMasks[id] = { ...state, id, parent };
      return id;
    },
    addTransition(storeState, transition) {
      const id = (_transitionsCounter--).toString();
      let src = transition.src;
      if (transition.src && typeof transition.src == 'object') {
        src = transition.src.id;
      }
      let dest = transition.dest;
      if (transition.dest && typeof transition.dest == 'object') {
        dest = transition.dest.id;
      }
      if (src === null || src === undefined) {
        throw new MissingPropertyError(
          'New transition does not have a source state'
        );
      } else if (dest === null || dest === undefined) {
        throw new MissingPropertyError(
          'New transition does not have a destination state'
        );
      }
      storeState._transitionsMasks[id] = { ...transition, id, src, dest };
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
    changeTransition(storeState, changes) {
      if (! changes.id) {
        throw new MissingPropertyError(
          'Transition to change does not have an id.'
        )
      }
      const mask = storeState._transitionsMasks[changes.id] || {};
      Object.assign(mask, changes);
      if ('src' in changes) {
        if (typeof changes.src === 'object') {
          if ('id' in changes.src) {
            mask.src= changes.src.id;
          } else {
            throw new MissingPropertyError(
              'Given source state does not have an id'
            );
          }
        } else {
          mask.src = changes.src;
        }
      }
      if ('dest' in changes) {
        if (typeof changes.dest === 'object') {
          if ('id' in changes.dest) {
            mask.dest = changes.dest.id;
          } else {
            throw new MissingPropertyError(
              'Given destination state does not have an id'
            );
          }
        } else {
          mask.dest = changes.dest;
        }
      }
      if (mask.src == mask.dest) {
        throw new Error('Self-closing state transition')
      }
      storeState._transitionsMasks[mask.id] = mask;
      console.debug('transition', mask.id, 'changed');
    },
    removeState(storeState, state) {
      if (! state.id) {
        throw new MissingPropertyError('State to remove does not have an id.')
      }
      storeState._statesMasks[state.id] = null;
      console.debug('state', state.id, 'removed');
    },
    removeTransition(storeState, transition) {
      if (! transition.id) {
        throw new MissingPropertyError(
          'Transition to remove does not have an id.'
        )
      }
      storeState._transitionsMasks[transition.id] = null;
      console.debug('transition', transition.id, 'removed');
    },
    // Update state and change mask correspondingly.
    updateState(storeState, { id, state }) {
      const mask = storeState._statesMasks[id];
      for (const key of Object.keys(mask)) {
        if (mask[key] == state[key]) {
          delete mask[key];
        }
      }
      mask.id = state.id;
      if (id != state.id) {
        storeState._statesMasks[state.id] = mask;
        Object.defineProperty(storeState._statesMasks, String(id), {
          get: new Function('return this[id];'.replace('id', state.id)),
          set: new Function('mask', 'this[id]=mask;'.replace('id', state.id)),
        });
      }
      storeState._states[state.id] = state;
    },
    // Update transition and change mask correspondingly.
    updateTransition(storeState, { id, transition}) {
      const mask = storeState._transitionsMasks[id];
      for (const key of Object.keys(mask)) {
        if (mask[key] == transition[key]) {
          delete mask[key];
        }
      }
      mask.id = transition.id;
      if (id != transition.id) {
        storeState._transitionsMasks[transition.id] = mask;
        Object.defineProperty(storeState._transitionsMasks, String(id), {
          get: new Function('return this[id];'.replace('id', transition.id)),
          set: new Function(
            'mask', 'this[id]=mask;'.replace('id', transition.id)
          ),
        });
      }
      storeState._transitions[transition.id] = transition;
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
    // Delete transition and mask
    deleteTransition(storeState, id) {
      const mask = storeState._transitionsMasks[id];
      if (mask) {
        delete storeState._transitions[mask.id];
        delete storeState._transitionsMasks[mask.id];
      }
      delete storeState._transitions[id];
      delete storeState._transitionsMasks[id];
    },
  },
  actions: {
    pull({ commit }) {
      return engineApi.statesList().then((states) => {
        states = Object.fromEntries(
          states.map(state => [state.id, state])
        );
        commit('setStates', states);
      }).then(() => {
        engineApi.statetransitionsList().then((transitions) => {
          transitions = Object.fromEntries(
            transitions.map(transition => [transition.id, transition])
          );
          commit('setTransitions', transitions);
          console.debug('Engine pulled')
        });
      }).catch((error) => {
        console.error('Could not pull', error);
      });
    },
    push({ commit, state }) {
      let statesOperations = {};
      Object.entries(state._statesMasks)
      .forEach(function createOrUpdate([id, mask]) {
        let operation;
        if (! mask) {  // destruction is performed after creations + updates
          return new Promise((resolve) => { resolve(null); });
        } else if (mask.id in statesOperations) {
          operation = statesOperations[mask.id];
        } else if (mask.id <= 0) {  // create
          operation = createOrUpdate(
            [undefined, state._statesMasks[mask.parent]]
          ).then((parent) => {
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
          operation = createOrUpdate(
            [undefined, state._statesMasks[mask.parent]]
          ).then((parent) => {
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
                return null;
              } else {
                throw new Error(
                  'Could not update state', mask.id, ':', error.code
                );
              }
            }).then((state) => {
              // TODO what if state === null (error 404)
              commit('updateState', { id: mask.id, state });
              console.debug('state', mask.id, 'updated');
              return state;
            });
          });
        }
        if (operation) {
          statesOperations[mask.id] = operation;
          if (id) {
            statesOperations[id] = operation;
          }
          return operation;
        }
      });

      let transitionsOperations = {};
      Object.entries(state._transitionsMasks)
      .forEach(function createOrUpdate([id, mask]) {
        let operation;
        if (! mask) {  // destruction is performed after creations + updates
          return new Promise((resolve) => { resolve(null); });
        } else if (mask.id in transitionsOperations) {
          operation = transitionsOperations[mask.id];
        } else if (mask.id <= 0) {  // create
          operation = Promise.all([
            statesOperations[mask.src] || new Promise((resolve) => {
              resolve({ id: mask.src });
            }),
            statesOperations[mask.dest] || new Promise((resolve) => {
              resolve({ id: mask.dest });
            }),
          ]).then(([src, dest]) => {
            if (! src || ! dest) {
              // TODO remove transition
            }
            const transition = { ...mask, id: undefined };
            transition.src = Number(src.id);
            transition.dest = Number(dest.id);
            return engineApi.statetransitionsCreate({ transition })
            .catch((error) => {
              throw new Error('Could not create transition:', error.code);
            }).then((transition) => {
              commit('updateTransition', { id: mask.id, transition });
              console.debug('transition', mask.id, 'created');
              return transition;
            });
          });
        } else if (Object.keys(mask).length > 1) {  // update
          operation = Promise.all([
            statesOperations[mask.src] || new Promise((resolve) => {
              resolve({ id: mask.src });
            }),
            statesOperations[mask.dest] || new Promise((resolve) => {
              resolve({ id: mask.dest });
            }),
          ]).then(([src, dest]) => {
            if (! src || ! dest) {
              // TODO transition
            }
            const patchedStateTransition = { ...mask, id: undefined };
            patchedStateTransition.src = Number(src.id);
            patchedStateTransition.dest = Number(dest.id);
            return engineApi.statetransitionsPartialUpdate(
              { id: mask.id, patchedStateTransition}
            ).catch((error) => {
              if (error.code == 404) {
                console.warning(
                  'Transition', mask.id,
                  'was removed before it could be updated'
                );
                return null;
              } else {
                throw new Error(
                  'Could not update transition', mask.id, ':', error.code
                );
              }
            }).then((transition) => {
              commit('updateTransition', { id: mask.id, transition});
              console.debug('transition', mask.id, 'updated');
              return transition;
            });
          });
        }
        if (operation) {
          transitionsOperations[mask.id] = operation;
          if (id) {
            transitionsOperations[id] = operation;
          }
          return operation;
        }
      });

      const operations = [
        ...Object.values(statesOperations),
        ...Object.values(transitionsOperations)
      ];
      const createdAndUpdated = Promise.all(operations);
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
      Object.entries(state._transitionsMasks)
      .forEach(function destroy([id, mask]) {
        if (! mask && id > 0) {
          createdAndUpdated.then(() => {
            operations[id] = engineApi.statetransitionsDestroy({ id })
            .catch((error) => {
              if (error.code == 404) {
                console.debug('Transition', id, 'was aleady destroyed');
              } else {
                throw new Error(
                  'Could not destroy transition', id, ':', error.message
                );
              }
            }).then(() => {
              commit('deleteTransition', id);
              console.debug('transition', id, 'destroyed');
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
