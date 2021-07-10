let _states = {};
let _transitions = {};

export function _getRemoteStates() {
  return Object.values(_states);
}

export function _getRemoteTransitions() {
  return Object.values(_transitions);
}

export function _setRemoteStates(states) {
  _states = Object.fromEntries(states.map(state => [state.id, state]));
}

export function _setRemoteTransitions(transitions) {
  _transitions = Object.fromEntries(transitions.map(
    (transition) => [transition.id, transition])
  );
}

export class Configuration {
  constructor(configuration = {}) {
    this.configuration = configuration;
  }
}

export class EngineApi {
  constructor(configuration = {}) {
    this.configuration = configuration;
  }

  _checkStateConstraints(state) {
    if (state.parent && ! (state.parent in _states)) {
      throw new Error('parent does not exist');
    }
  }

  _checkTransitionConstraints(transition) {
    if (! transition.src || ! (String(transition.src) in _states)) {
      throw new Error('source does not exist');
    }
    if (! transition.dest || ! (transition.dest in _states)) {
      throw new Error('destination does not exist');
    }
  }

  async statesCreate(requestParameters) {
    for (let id = 1; id <= Object.keys(_states).length + 1; id++) {
      if (!(String(id) in _states)) {
        const state = { ...requestParameters.state, id };
        try {
          this._checkStateConstraints(state);
        } catch (fail) {
          throw new Error('Cannot create state', fail);
        }
        _states[id] = state;
        return state;
      }
    }
    throw new Error('Could not find new id for state in creation');
  }

  async statetransitionsCreate(requestParameters) {
    for (let id = 1; id <= Object.keys(_transitions).length + 1; id++) {
      if (!(String(id) in _transitions)) {
        const transition = { ...requestParameters.transition, id };
        try {
          this._checkTransitionConstraints(transition);
        } catch (fail) {
          throw new Error('Cannot create transition', fail);
        }
        _transitions[id] = transition;
        return transition;
      }
    }
    throw new Error('Could not find new id for transition in creation');
  }

  async statesPartialUpdate(requestParameters) {
    if (requestParameters.id in _states) {
      const state = _states[requestParameters.id];
      Object.assign(state, requestParameters.patchedState);
      return state
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statetransitionsPartialUpdate(requestParameters) {
    if (requestParameters.id in _transitions) {
      const transition = _transitions[requestParameters.id];
      Object.assign(transition, requestParameters.patchedStateTransition);
      return transition
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statesDestroy(requestParameters) {
    if (requestParameters.id in _states) {
      delete _states[requestParameters.id]
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statetransitionsDestroy(requestParameters) {
    if (requestParameters.id in _transitions) {
      delete _transitions[requestParameters.id]
    } else {
      throw new Error()  // TODO error_code
    }
  }

  async statesList() {
    return Object.values(_states);
  }

  async statetransitionsList() {
    return Object.values(_states);
  }
}

